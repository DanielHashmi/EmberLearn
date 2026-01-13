"""
EmberLearn Shared Backend Utilities

This module provides common utilities used across all AI agent microservices:
- Logging configuration with structlog
- Correlation ID middleware for request tracing
- Dapr client helpers
- Pydantic models/schemas
- Environment configuration
"""

from .config import settings
from .logging_config import setup_logging, get_logger
from .correlation import CorrelationMiddleware, get_correlation_id
from .dapr_client import DaprClient
from .models import (
    BaseResponse,
    ErrorResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CodeExecutionRequest,
    CodeExecutionResponse,
    ExerciseRequest,
    ExerciseResponse,
    ProgressData,
    MasteryLevel,
)

__all__ = [
    # Config
    "settings",
    # Logging
    "setup_logging",
    "get_logger",
    # Correlation
    "CorrelationMiddleware",
    "get_correlation_id",
    # Dapr
    "DaprClient",
    # Models
    "BaseResponse",
    "ErrorResponse",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "CodeExecutionRequest",
    "CodeExecutionResponse",
    "ExerciseRequest",
    "ExerciseResponse",
    "ProgressData",
    "MasteryLevel",
]
