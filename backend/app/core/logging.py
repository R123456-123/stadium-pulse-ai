"""Structured logging configuration using structlog.

Provides JSON-formatted logs in production and human-readable
colored output in development. All application code should use
structlog.get_logger() instead of print() or logging.getLogger().

Why structlog over stdlib logging?
    - Structured key-value pairs instead of formatted strings
    - JSON output for production log aggregation (Cloud Logging, ELK)
    - Colored, readable output for development
    - Context variables that automatically attach to all log entries
      within a request (request_id, user_role, etc.)
"""

import logging
import sys

import structlog


def setup_logging(*, debug: bool = False) -> None:
    """Configure structured logging for the application.

    Args:
        debug: If True, use human-readable colored console output.
               If False, use JSON output for production log aggregation.
    """
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if debug:
        # Human-readable colored output for development
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(colors=True)
    else:
        # JSON output for production log aggregation
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Bridge stdlib logging → structlog so third-party libraries
    # (uvicorn, sqlalchemy) also produce structured output
    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if debug else logging.WARNING
    )
