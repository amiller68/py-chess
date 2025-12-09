import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.logger import Logger

from ..database import Base, DatabaseException


class UserModel(BaseModel):
    """Pydantic model for User serialization"""

    id: str
    email: str


class User(Base):
    """User database model"""

    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def model(self) -> UserModel:
        return UserModel(
            id=str(self.id),
            email=str(self.email),
        )

    @staticmethod
    async def create(email: str, session: AsyncSession, logger: Logger | None = None) -> "User":
        try:
            user = User(email=email)
            session.add(user)
            await session.flush()
            return user
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)

    @staticmethod
    async def read(id: str, session: AsyncSession, logger: Logger | None = None) -> "User | None":
        try:
            result = await session.execute(select(User).filter_by(id=id))
            return result.scalars().first()
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)

    @staticmethod
    async def read_by_email(
        email: str, session: AsyncSession, logger: Logger | None = None
    ) -> "User | None":
        try:
            result = await session.execute(select(User).filter_by(email=email))
            return result.scalars().first()
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)
