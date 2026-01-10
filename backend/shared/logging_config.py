"""
Structured logging configuration using structlog and orjson.

Provides JSON-formatted logs with correlation IDs for distributed tracing.
"""

import logging
import sys
from typing import Any

import orjson
import structlog


def orjson_dumps(obj: Any, **kwargs) -> str:
    """Serialize to JSON using orjson for performance."""
    return orjson.dumps(obj).decode('utf-8')


def configure_logging(service_name: str, level: str = "INFO"):
    """
    Configure structured logging for the service.

    Args:
        service_name: Name of the microservice (e.g., "triage_agent")
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(serializer=orjson_dumps),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Add service name to all logs
    structlog.contextvars.bind_contextvars(service=service_name)

    logger = structlog.get_logger()
    logger.info("logging_configured", service=service_name, level=level)

    return logger
