"""
Dapr client helper functions for state management and pub/sub.

Per research.md decision 2: Dapr sidecar for PostgreSQL state and Kafka pub/sub.
"""

import json
from typing import Any

import structlog
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem

from backend.shared.correlation import get_correlation_id

log = structlog.get_logger(__name__)

# Default component names (configured in k8s/infrastructure/dapr/)
DEFAULT_STATE_STORE = "statestore"  # PostgreSQL via Dapr
DEFAULT_PUBSUB = "kafka-pubsub"  # Kafka via Dapr


async def save_state(
    key: str,
    value: Any,
    store_name: str = DEFAULT_STATE_STORE,
    metadata: dict[str, str] | None = None,
) -> None:
    """
    Save state to Dapr state store (PostgreSQL).

    Args:
        key: State key (e.g., "student:42:topic:2")
        value: Value to store (will be JSON serialized)
        store_name: Dapr state store component name
        metadata: Optional metadata for the state operation
    """
    with DaprClient() as client:
        client.save_state(
            store_name=store_name,
            key=key,
            value=json.dumps(value),
            state_metadata=metadata,
        )
    log.debug("state_saved", key=key, store=store_name)


async def get_state(
    key: str,
    store_name: str = DEFAULT_STATE_STORE,
) -> Any | None:
    """
    Get state from Dapr state store.

    Args:
        key: State key to retrieve
        store_name: Dapr state store component name

    Returns:
        Deserialized value or None if not found
    """
    with DaprClient() as client:
        state = client.get_state(store_name=store_name, key=key)
        if state.data:
            log.debug("state_retrieved", key=key, store=store_name)
            return json.loads(state.data)
    log.debug("state_not_found", key=key, store=store_name)
    return None


async def delete_state(
    key: str,
    store_name: str = DEFAULT_STATE_STORE,
) -> None:
    """
    Delete state from Dapr state store.

    Args:
        key: State key to delete
        store_name: Dapr state store component name
    """
    with DaprClient() as client:
        client.delete_state(store_name=store_name, key=key)
    log.debug("state_deleted", key=key, store=store_name)


async def publish_event(
    topic: str,
    data: dict[str, Any],
    pubsub_name: str = DEFAULT_PUBSUB,
    partition_key: str | None = None,
) -> None:
    """
    Publish event to Kafka via Dapr pub/sub.

    Per research.md decision 4: Use student_id as partition key for ordering.

    Args:
        topic: Kafka topic name (e.g., "learning.response", "code.executed")
        data: Event payload (will be JSON serialized)
        pubsub_name: Dapr pub/sub component name
        partition_key: Partition key for ordering (typically student_id)
    """
    # Add correlation ID to event data
    correlation_id = get_correlation_id()
    event_data = {
        "correlation_id": correlation_id,
        **data,
    }

    # Build metadata with partition key if provided
    metadata: dict[str, str] = {}
    if partition_key:
        metadata["partitionKey"] = str(partition_key)

    with DaprClient() as client:
        client.publish_event(
            pubsub_name=pubsub_name,
            topic_name=topic,
            data=json.dumps(event_data),
            publish_metadata=metadata,
        )

    log.info(
        "event_published",
        topic=topic,
        partition_key=partition_key,
        pubsub=pubsub_name,
    )


async def bulk_save_state(
    items: list[tuple[str, Any]],
    store_name: str = DEFAULT_STATE_STORE,
) -> None:
    """
    Save multiple state items in a single operation.

    Args:
        items: List of (key, value) tuples
        store_name: Dapr state store component name
    """
    with DaprClient() as client:
        state_items = [
            StateItem(key=key, value=json.dumps(value))
            for key, value in items
        ]
        client.save_bulk_state(store_name=store_name, states=state_items)
    log.debug("bulk_state_saved", count=len(items), store=store_name)


# Kafka topic constants per FR-012
class KafkaTopics:
    """Kafka topic names for EmberLearn events."""

    # Learning events
    LEARNING_QUERY = "learning.query"
    LEARNING_RESPONSE = "learning.response"

    # Code execution events
    CODE_SUBMITTED = "code.submitted"
    CODE_EXECUTED = "code.executed"

    # Exercise events
    EXERCISE_CREATED = "exercise.created"
    EXERCISE_COMPLETED = "exercise.completed"

    # Struggle detection events
    STRUGGLE_DETECTED = "struggle.detected"
    STRUGGLE_RESOLVED = "struggle.resolved"


# Example usage:
# await publish_event(
#     topic=KafkaTopics.CODE_EXECUTED,
#     data={"student_id": 42, "result": "success", "output": "Hello World"},
#     partition_key="42"  # student_id for ordering
# )
