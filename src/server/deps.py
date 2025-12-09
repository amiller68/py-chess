from typing import cast

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import APIKeyCookie
from fastapi_sso.sso.base import OpenID
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.logger import Logger
from src.state import AppState

SESSION_COOKIE_NAME = "session"


def async_db(request: Request) -> AsyncSession:
    return cast(AsyncSession, request.state.db)


def logger(request: Request) -> Logger:
    return cast(Logger, request.state.logger)


def app_state(request: Request) -> AppState:
    return cast(AppState, request.state.app_state)


async def get_logged_in_user(
    cookie: str = Security(APIKeyCookie(name=SESSION_COOKIE_NAME, auto_error=False)),
    db: AsyncSession = Depends(async_db),
    log: Logger = Depends(logger),
    state: AppState = Depends(app_state),
) -> User | None:
    """Get the logged in user from the session cookie, or None if not logged in"""
    if not cookie:
        return None

    try:
        claims = jwt.decode(cookie, key=state.secrets.service_secret, algorithms=["HS256"])
        openid = OpenID(**claims["pld"])

        if not openid.email:
            return None

        user = await User.read_by_email(email=openid.email, session=db, logger=log)
        if not user:
            log.info(f"Creating new user: {openid.email}")
            user = await User.create(email=openid.email, session=db, logger=log)
            await db.commit()

        return user
    except Exception:
        return None


async def require_logged_in_user(user: User | None = Depends(get_logged_in_user)) -> User:
    """Require that a user is logged in, otherwise raise 401"""
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
