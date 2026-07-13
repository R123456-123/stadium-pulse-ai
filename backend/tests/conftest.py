"""Shared test fixtures for StadiumPulse AI backend tests.

Key fixtures:
    - test_settings: Settings with test-specific overrides (in-memory SQLite)
    - test_db: Fresh database per test (tables created + dropped)
    - test_client: httpx.AsyncClient wired to the FastAPI test app
    - seeded_db: test_db pre-populated with seed data

Design decisions:
    - Uses in-memory SQLite (sqlite+aiosqlite:///) for speed — no disk I/O
    - Each test gets a fresh database — no test pollution
    - Gemini calls are never made in tests — mock fixtures provided
"""

from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings
from app.core.database import Base, get_session
from app.main import create_app


# ── Settings Override ────────────────────────────────────────

@pytest.fixture
def test_settings() -> Settings:
    """Settings configured for testing — in-memory DB, no real API key."""
    return Settings(
        app_name="StadiumPulse AI Test",
        debug=True,
        database_url="sqlite+aiosqlite:///",
        gemini_api_key="test-key-not-real",
        gemini_model="gemini-2.5-flash",
        cors_origins=["http://testserver"],
        rate_limit_chat="100/minute",
    )


# ── Database Fixtures ────────────────────────────────────────

@pytest.fixture
async def test_db() -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    """Create a fresh in-memory database for each test.

    Yields a session factory. Tables are created before the test
    and dropped after it — complete isolation between tests.
    """
    engine = create_async_engine("sqlite+aiosqlite:///", echo=False)
    session_factory = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_session(
    test_db: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Provide a single database session for a test."""
    async with test_db() as session:
        yield session


# ── HTTP Client Fixture ──────────────────────────────────────

@pytest.fixture
async def test_client(
    test_db: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client wired to a test FastAPI app.

    Overrides the database session dependency so all requests
    use the test database instead of the production one.
    """
    app = create_app()

    # Override DB session to use test database
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with test_db() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.clear()


# ── Gemini Mock Fixtures ─────────────────────────────────────

@pytest.fixture
def mock_gemini_client() -> MagicMock:
    """A mock Gemini client that never hits the real API.

    Returns a MagicMock with async methods pre-configured.
    Tests should set return values on specific methods as needed:

        mock_gemini_client.chat_with_tools.return_value = ChatResult(...)
    """
    client = MagicMock()
    client.chat_with_tools = AsyncMock()
    client.generate_recommendations = AsyncMock(return_value=[])
    return client
