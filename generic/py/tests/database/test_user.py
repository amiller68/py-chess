import os
import uuid
import pytest
import pytest_asyncio
from src.database.database import AsyncDatabase
from src.database.models.user import User

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def db():
    # Get database connection info from environment
    postgres_url = os.getenv("POSTGRES_URL")
    if not postgres_url:
        raise ValueError("POSTGRES_URL is not set")

    # Convert to async URL if needed
    if not postgres_url.startswith("postgresql+asyncpg://"):
        postgres_url = postgres_url.replace("postgresql://", "postgresql+asyncpg://")

    # Create database connection
    db = AsyncDatabase(postgres_url)
    await db.initialize()
    yield db

    # Cleanup
    await db.engine.dispose()


@pytest_asyncio.fixture
async def session(db):
    # Use a simple session with rollback for cleanup
    async with db.session() as session:
        yield session
        # Rollback any changes
        await session.rollback()


async def test_create_user(session):
    # Test creating a user with valid email - use unique email
    email = f"test_{uuid.uuid4()}@example.com"
    user = await User.create(email=email, session=session)

    assert user.id is not None
    assert user.email == email
    assert user.created_at is not None
    assert user.updated_at is not None
