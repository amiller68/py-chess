from contextlib import asynccontextmanager
from enum import Enum as PyEnum
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class DatabaseExceptionType(PyEnum):
    conflict = "conflict"
    not_found = "not_found"
    invalid = "invalid"


class DatabaseException(Exception):
    def __init__(self, type: DatabaseExceptionType, message: str):
        self.message = message
        self.type = type

    def __str__(self) -> str:
        return f"{self.message}"

    @staticmethod
    def from_sqlalchemy_error(e: Exception) -> Exception:
        """Convert SQLAlchemy errors to typed DatabaseException"""
        if not isinstance(e, Exception):
            return e

        error_msg = str(e).lower()

        # Foreign key constraint violations
        if any(
            phrase in error_msg
            for phrase in [
                "violates foreign key constraint",
                "foreign key constraint failed",
            ]
        ):
            return DatabaseException(DatabaseExceptionType.invalid, str(e))

        # Unique constraint violations
        if any(
            phrase in error_msg
            for phrase in [
                "violates unique constraint",
                "unique constraint failed",
                "duplicate key",
            ]
        ):
            return DatabaseException(DatabaseExceptionType.conflict, str(e))

        # Not found errors
        if any(
            phrase in error_msg
            for phrase in [
                "no row was found for one",
                "no results found",
                "record not found",
            ]
        ):
            return DatabaseException(DatabaseExceptionType.not_found, str(e))

        # Check constraint violations
        if any(
            phrase in error_msg
            for phrase in ["violates check constraint", "check constraint failed"]
        ):
            return DatabaseException(DatabaseExceptionType.invalid, str(e))

        return e


class AsyncDatabase:
    """Async database connection manager"""

    def __init__(self, database_async_url: str):
        self.database_url = database_async_url

        self.engine = create_async_engine(
            database_async_url,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
            echo=False,
        )

        self.AsyncSession = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)  # type: ignore

    async def initialize(self) -> None:
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session"""
        session = self.AsyncSession()
        try:
            yield session
        finally:
            await session.close()
