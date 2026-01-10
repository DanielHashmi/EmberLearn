"""
FastAPI middleware for correlation ID injection and request tracking.

Ensures all logs and events can be traced across microservices.
"""

import uuid
from contextvars import ContextVar
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = structlog.get_logger()

# Context variable to store correlation ID for the current request
_correlation_id_ctx_var: ContextVar[str] = ContextVar("correlation_id", default="")


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts or generates correlation IDs for request tracing.

    Checks for X-Correlation-ID header, generates one if missing, and binds it
    to structlog context for all logs during request processing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Store in context variable
        _correlation_id_ctx_var.set(correlation_id)

        # Bind to structlog for all logs in this request
        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        # Clear structlog context
        structlog.contextvars.clear_contextvars()

        return response


def get_correlation_id() -> str:
    """
    Get the correlation ID for the current request.

    Returns:
        Correlation ID string, or empty string if not in request context
    """
    return _correlation_id_ctx_var.get()
