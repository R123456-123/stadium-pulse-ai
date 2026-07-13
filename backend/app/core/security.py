"""Security configuration: CORS middleware and rate limiting.

CORS origins are locked to known frontends via Settings —
no wildcard "*" in production. Rate limiting uses SlowAPI to
prevent abuse of the Gemini-backed chat endpoint, controlling
both cost and security exposure.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


# ── Rate Limiter ─────────────────────────────────────────────
# Keyed by client IP address. The actual rate (e.g. "10/minute")
# is applied per-endpoint using the @limiter.limit() decorator.
limiter = Limiter(key_func=get_remote_address)


def configure_cors(app: FastAPI, origins: list[str]) -> None:
    """Add CORS middleware with the specified allowed origins.

    Args:
        app: The FastAPI application instance.
        origins: List of allowed origin URLs (e.g., ["http://localhost:5173"]).

    Security notes:
        - allow_methods is restricted to GET and POST — the only HTTP methods
          our API actually uses. No PUT/DELETE/PATCH.
        - allow_credentials is True to support cookie-based auth if needed later.
        - allow_headers is "*" because browsers send various standard headers
          and restricting them causes more debugging pain than security benefit.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit violations.

    Returns a clear JSON error instead of SlowAPI's default plain-text
    response. This keeps error format consistent with FastAPI's built-in
    error responses.
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please wait before sending another message.",
            "retry_after": str(exc.detail),
        },
    )
