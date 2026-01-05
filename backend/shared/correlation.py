"""
FastAPI middleware for correlation ID injection and propagation.

Ensures all requests have a correlation_id for distributed tracing.
"""

import uuid
from contextvars import ContextVar
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable for correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

# Header name for correlation ID propagation
CORRELATION_ID_HEADER = "X-Correlation-ID"


def get_correlation_id() -> str:
    """Get the current correlation ID from context."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in context."""
    correlation_id_ctx.set(correlation_id)
    # Also bind to structlog context for automatic inclusion in logs
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that extracts or generates correlation ID for each request.

    - If X-Correlation-ID header exists, use it (for inter-service calls)
    - Otherwise, generate a new UUID
    - Bind to structlog context for automatic log inclusion
    - Add to response headers for client visibility
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate correlation ID
        correlation_id = request.headers.get(CORRELATION_ID_HEADER)
        if not correlation_id:
            correlation_id = str(uuid.uuid4())

        # Set in context
        set_correlation_id(correlation_id)

        # Log request start
        log = structlog.get_logger()
        log.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_host=request.client.host if request.client else None,
        )

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers[CORRELATION_ID_HEADER] = correlation_id

        # Log request completion
        log.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
        )

        return response


def create_correlation_id() -> str:
    """Create a new correlation ID (for initiating new traces)."""
    return str(uuid.uuid4())


# Example usage in FastAPI app:
# from fastapi import FastAPI
# from backend.shared.correlation import CorrelationIdMiddleware
#
# app = FastAPI()
# app.add_middleware(CorrelationIdMiddleware)
