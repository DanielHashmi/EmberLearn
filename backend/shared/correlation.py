"""
Correlation ID Middleware

Provides request tracing across microservices using correlation IDs.
Integrates with structlog for automatic correlation ID logging.
"""

import uuid
from contextvars import ContextVar
from typing import Callable, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import structlog

# Context variable for correlation ID
correlation_id_ctx: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)

# Header names for correlation ID propagation
CORRELATION_ID_HEADER = "X-Correlation-ID"
REQUEST_ID_HEADER = "X-Request-ID"


def get_correlation_id() -> Optional[str]:
    """Get the current correlation ID from context."""
    return correlation_id_ctx.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in context."""
    correlation_id_ctx.set(correlation_id)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages correlation IDs for request tracing.
    
    - Extracts correlation ID from incoming request headers
    - Generates new ID if not present
    - Adds correlation ID to response headers
    - Binds correlation ID to structlog context
    """
    
    def __init__(
        self,
        app: ASGIApp,
        header_name: str = CORRELATION_ID_HEADER,
    ) -> None:
        super().__init__(app)
        self.header_name = header_name
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        # Extract or generate correlation ID
        correlation_id = (
            request.headers.get(self.header_name)
            or request.headers.get(REQUEST_ID_HEADER)
            or generate_correlation_id()
        )
        
        # Set in context
        set_correlation_id(correlation_id)
        
        # Bind to structlog context
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
        )
        
        # Get logger and log request
        logger = structlog.get_logger()
        logger.info(
            "request_started",
            client_host=request.client.host if request.client else None,
            query_params=str(request.query_params),
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Log response
            logger.info(
                "request_completed",
                status_code=response.status_code,
            )
            
            # Add correlation ID to response headers
            response.headers[self.header_name] = correlation_id
            
            return response
            
        except Exception as e:
            logger.exception(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
        
        finally:
            # Clear context
            structlog.contextvars.clear_contextvars()


def get_correlation_headers() -> dict[str, str]:
    """
    Get headers dict with correlation ID for outgoing requests.
    
    Use this when making HTTP calls to other services to propagate
    the correlation ID.
    """
    correlation_id = get_correlation_id()
    if correlation_id:
        return {CORRELATION_ID_HEADER: correlation_id}
    return {}
