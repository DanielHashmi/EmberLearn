"""
Structured JSON logging configuration using structlog + orjson.

Per research.md decision 6: Cloud-native logging with correlation IDs.
"""

import logging
import sys
from typing import Any

import orjson
import structlog


def orjson_dumps(v: Any, *, default: Any = None) -> str:
    """Serialize to JSON string using orjson for performance."""
    return orjson.dumps(v, default=default).decode("utf-8")


def configure_logging(service_name: str, log_level: str = "INFO") -> None:
    """
    Configure structlog for JSON logging to stdout.

    Args:
        service_name: Name of the service (e.g., "triage-agent")
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            # Add contextvars (correlation_id, etc.)
            structlog.contextvars.merge_contextvars,
            # Add log level
            structlog.stdlib.add_log_level,
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Add timestamp in ISO format
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            # Add service name
            structlog.processors.CallsiteParameterAdder(
                [
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                    structlog.processors.CallsiteParameter.LINENO,
                ]
            ),
            # Add exception info
            structlog.processors.format_exc_info,
            # Render as JSON
            structlog.processors.JSONRenderer(serializer=orjson_dumps),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Bind service name to all logs
    structlog.contextvars.bind_contextvars(service_name=service_name)


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Optional logger name

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


# Example usage:
# configure_logging("triage-agent", "INFO")
# log = get_logger(__name__)
# log.info("query_received", student_id=42, query_length=25)
#
# Output:
# {
#   "event": "query_received",
#   "level": "info",
#   "timestamp": "2026-01-05T10:30:45.123456Z",
#   "service_name": "triage-agent",
#   "student_id": 42,
#   "query_length": 25
# }
