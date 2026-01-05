"""Base agent infrastructure for EmberLearn AI agents."""

from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from shared.logging_config import configure_logging
from shared.correlation import CorrelationIdMiddleware


def create_agent_app(
    service_name: str,
    title: str,
    description: str,
    version: str = "1.0.0",
) -> FastAPI:
    """Create a FastAPI application with standard agent configuration.

    Args:
        service_name: Service identifier for logging
        title: API title
        description: API description
        version: API version

    Returns:
        Configured FastAPI application
    """
    configure_logging(service_name)
    logger = structlog.get_logger()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan handler."""
        logger.info(f"{service_name}_starting")
        yield
        logger.info(f"{service_name}_stopping")

    app = FastAPI(
        title=title,
        description=description,
        version=version,
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint for Kubernetes probes."""
        return {"status": "healthy", "service": service_name}

    return app
