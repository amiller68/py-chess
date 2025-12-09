from typing import cast

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.logger import Logger
from src.state import AppState


def async_db(request: Request) -> AsyncSession:
    return cast(AsyncSession, request.state.db)


def logger(request: Request) -> Logger:
    return cast(Logger, request.state.logger)


def app_state(request: Request) -> AppState:
    return cast(AppState, request.state.app_state)
