from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from sqlalchemy.future import select

from src.logger import Logger
from ..database import Base, DatabaseException


class UserModel(BaseModel):
    id: str
    email: str


class User(Base):
    __tablename__ = "users"

    # Unique identifier
    id = Column(
        String, primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False
    )

    # email
    email = Column(String, unique=True, nullable=False)

    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def model(self):
        return UserModel(
            id=str(self.id),
            email=self.email,
        )

    @staticmethod
    async def create(email: str, session: AsyncSession, logger: Logger | None = None):
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
    async def read(id: str, session: AsyncSession, logger: Logger | None = None):
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
    ):
        try:
            result = await session.execute(select(User).filter_by(email=email))
            return result.scalars().first()
        except Exception as e:
            if logger:
                logger.error(e)
            raise DatabaseException.from_sqlalchemy_error(e)
