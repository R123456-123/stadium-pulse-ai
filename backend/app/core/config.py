"""Application configuration loaded from environment variables.

Uses pydantic-settings to provide type-safe, validated configuration
with automatic .env file loading. Never hardcode secrets here — all
sensitive values must come from environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable binding.

    Every field maps to an environment variable of the same name
    (case-insensitive). Fields without defaults are required —
    the app will fail fast at startup if they're missing from .env.
    """

    # ── App ──────────────────────────────────────────────────
    app_name: str = "StadiumPulse AI"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./stadiumPulse.db"

    # ── Gemini AI ────────────────────────────────────────────
    gemini_api_key: str  # Required — no default, must be set in .env
    gemini_model: str = "gemini-3.1-flash-lite"

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:5173", "https://stadium-pulse-ai-blush.vercel.app"]

    # ── Rate Limiting ────────────────────────────────────────
    rate_limit_chat: str = "10/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# ── Singleton ────────────────────────────────────────────────
# Cached at module level so we don't re-read .env on every request.
# FastAPI's Depends() still works — get_settings() returns this instance.
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the application settings singleton.

    First call reads from .env and environment variables.
    Subsequent calls return the cached instance.
    """
    global _settings  # noqa: PLW0603
    if _settings is None:
        _settings = Settings()
    return _settings
