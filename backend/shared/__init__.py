"""Backend shared module initialization."""

from backend.shared.logging_config import configure_logging, get_logger
from backend.shared.correlation import (
    CorrelationIdMiddleware,
    get_correlation_id,
    set_correlation_id,
    create_correlation_id,
)
from backend.shared.dapr_client import (
    save_state,
    get_state,
    delete_state,
    publish_event,
    bulk_save_state,
    KafkaTopics,
)

__all__ = [
    "configure_logging",
    "get_logger",
    "CorrelationIdMiddleware",
    "get_correlation_id",
    "set_correlation_id",
    "create_correlation_id",
    "save_state",
    "get_state",
    "delete_state",
    "publish_event",
    "bulk_save_state",
    "KafkaTopics",
]
