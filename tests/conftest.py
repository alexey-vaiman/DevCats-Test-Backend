import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db.database import Base, get_db
from app.core.config import settings
from main import app

from unittest.mock import patch, MagicMock

# Use a separate test PostgreSQL database to match production behavior.
# Ensure that this database exists (e.g., CREATE DATABASE marketplace_test;)
test_db_url = str(settings.DATABASE_URL)
if test_db_url.endswith("/marketplace"):
    TEST_DATABASE_URL = test_db_url.replace("/marketplace", "/marketplace_test")
else:
    TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/marketplace_test"

from sqlalchemy.pool import NullPool
engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine_test, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(autouse=True)
def mock_s3_service():
    with patch("boto3.client") as mock_client:
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        yield mock_s3

@pytest_asyncio.fixture(scope="session")
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    # Override the dependency yielding the test session
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    # Cleanup overrides after the test
    app.dependency_overrides.clear()
