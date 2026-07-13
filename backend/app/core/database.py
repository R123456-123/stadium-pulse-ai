"""Async SQLAlchemy database engine and session management.

Uses SQLAlchemy 2.0's async API with aiosqlite for development.
The async engine ensures FastAPI's event loop is never blocked by
database I/O. Connection string is configurable via DATABASE_URL
in .env to support Postgres in production.

Architecture note:
    Engine and session factory are module-level singletons initialized
    at app startup via init_engine(). This avoids creating a new engine
    per request while keeping the module importable without side effects.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    All models inherit from this. SQLAlchemy uses it to track
    table metadata and generate CREATE TABLE statements.
    """


# ── Module-level singletons (initialized at startup) ────────
_engine = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(database_url: str, *, echo: bool = False) -> None:
    """Initialize the async database engine and session factory.

    Called once during FastAPI lifespan startup. Must be called
    before any database operations.

    Args:
        database_url: SQLAlchemy-compatible async connection string.
                      e.g. "sqlite+aiosqlite:///./stadiumPulse.db"
        echo: If True, log all SQL statements (useful for debugging).
    """
    global _engine, _async_session_factory
    _engine = create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
    )
    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def create_tables() -> None:
    """Create all tables defined by ORM models.

    Uses Base.metadata.create_all() which is safe to call repeatedly —
    it only creates tables that don't already exist.

    Note: A production deployment would use Alembic migrations instead.
    """
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides an async database session.

    Usage in a router::

        @router.get("/zones")
        async def list_zones(session: AsyncSession = Depends(get_session)):
            ...

    The session auto-commits on success and auto-rolls-back on exception.
    Each request gets its own session — no shared state between requests.
    """
    if _async_session_factory is None:
        raise RuntimeError("Database engine not initialized. Call init_engine() first.")
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def close_engine() -> None:
    """Dispose of the database engine on app shutdown.

    Closes all pooled connections cleanly. Called during
    FastAPI lifespan shutdown.
    """
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
