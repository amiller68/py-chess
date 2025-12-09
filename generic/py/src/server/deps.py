from fastapi import (
    Request,
    Depends,
    HTTPException,
    Security,
)
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_sso.sso.base import OpenID
from jose import jwt

from src.state import AppState
from src.database.models import User
from src.logger import Logger

SESION_COOKIE_NAME = "session"


def async_db(request: Request) -> AsyncSession:
    return request.state.db


def logger(request: Request) -> Logger:
    return request.state.logger


def app_state(request: Request) -> AppState:
    return request.state.app_state


async def get_logged_in_user(
    cookie: str = Security(APIKeyCookie(name=SESION_COOKIE_NAME)),
    async_db: AsyncSession = Depends(async_db),
    logger: Logger = Depends(logger),
    app_state: AppState = Depends(app_state),
) -> User:
    try:
        claims = jwt.decode(
            cookie, key=app_state.secrets.service_secret, algorithms=["HS256"]
        )
        openid = OpenID(**claims["pld"])

        if not openid.email:
            raise ValueError("Email is required")

        user = await User.read_by_email(
            email=openid.email, session=async_db, logger=logger
        )
        if not user:
            logger.info(f"Creating new user: {openid.email}")
            user = await User.create(
                email=openid.email, session=async_db, logger=logger
            )
            await async_db.commit()

        return user
    except Exception as error:
        raise HTTPException(status_code=401, detail="Unauthorized") from error


async def require_logged_in_user(user: User = Depends(get_logged_in_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user
