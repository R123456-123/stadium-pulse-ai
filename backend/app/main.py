"""FastAPI application factory with lifespan management.

The app factory pattern (create_app function) keeps the module importable
without side effects — important for testing, where you want to create
a fresh app instance per test with different settings.

Lifespan handles:
    1. Startup: initialize database engine, create tables, setup logging,
       start the crowd simulator background task
    2. Shutdown: stop the crowd simulator, close database connections
"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

from app.core.config import get_settings
from app.core.database import close_engine, create_tables, init_engine
from app.core.logging import setup_logging
from app.core.security import configure_cors, limiter, rate_limit_exceeded_handler

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    Everything before ``yield`` runs at startup.
    Everything after ``yield`` runs at shutdown.
    """
    settings = get_settings()

    # ── Startup ──────────────────────────────────────────────
    setup_logging(debug=settings.debug)
    logger.info(
        "starting_application",
        app_name=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    # Initialize database
    init_engine(settings.database_url, echo=settings.debug)
    await create_tables()
    logger.info("database_ready", url=settings.database_url.split("///")[0] + "///***")

    # Start crowd simulator as a background task
    from app.core.database import _async_session_factory
    from app.routers.ws_crowd import manager as ws_manager
    from app.services.crowd_simulator import CrowdSimulator

    simulator = CrowdSimulator(
        session_factory=_async_session_factory,
        broadcast_fn=ws_manager.broadcast,
    )
    simulator_task = asyncio.create_task(simulator.run())
    logger.info("crowd_simulator_task_created")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    simulator.stop()
    simulator_task.cancel()
    try:
        await simulator_task
    except asyncio.CancelledError:
        pass
    logger.info("crowd_simulator_stopped")

    await close_engine()
    logger.info("application_shutdown_complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Fully configured FastAPI instance with middleware,
        error handlers, and routers attached.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Smart Stadium Operations & Fan Assistant for FIFA World Cup 2026. "
            "Powered by Google Gemini AI."
        ),
        docs_url="/docs" if settings.debug else None,  # Disable Swagger in prod
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────
    configure_cors(app, settings.cors_origins)

    # ── Rate Limiting ────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # ── Health Check ─────────────────────────────────────────
    @app.get("/api/v1/health", tags=["meta"])
    async def health_check() -> dict:
        """Health check endpoint for Cloud Run and monitoring."""
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
        }

    # ── Routers ──────────────────────────────────────────────
    from app.routers import stadium_info, ws_crowd

    app.include_router(stadium_info.router)
    app.include_router(ws_crowd.router)
    # app.include_router(fan_chat.router)       # Phase 5
    # app.include_router(ops_dashboard.router)  # Phase 6

    return app


# ── Application instance ─────────────────────────────────────
# This is what uvicorn imports: uvicorn app.main:app
app = create_app()
