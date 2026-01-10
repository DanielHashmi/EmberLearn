"""
Dapr client helper functions for state management and pub/sub messaging.

Simplifies common Dapr operations with error handling and logging.
"""

import json
from typing import Any, Dict, Optional

import structlog
from dapr.clients import DaprClient
from dapr.clients.exceptions import DaprInternalError

logger = structlog.get_logger()


async def save_state(
    state_store: str,
    key: str,
    value: Any,
    dapr_client: Optional[DaprClient] = None
) -> bool:
    """
    Save state to Dapr state store.

    Args:
        state_store: Name of the state store component
        key: State key
        value: State value (will be JSON serialized)
        dapr_client: Optional DaprClient instance (creates new if None)

    Returns:
        True if successful, False otherwise
    """
    try:
        if dapr_client:
            dapr_client.save_state(state_store, key, json.dumps(value))
        else:
            with DaprClient() as client:
                client.save_state(state_store, key, json.dumps(value))

        logger.info("state_saved", state_store=state_store, key=key)
        return True

    except DaprInternalError as e:
        logger.error("state_save_failed", state_store=state_store, key=key, error=str(e))
        return False


async def get_state(
    state_store: str,
    key: str,
    dapr_client: Optional[DaprClient] = None
) -> Optional[Any]:
    """
    Get state from Dapr state store.

    Args:
        state_store: Name of the state store component
        key: State key
        dapr_client: Optional DaprClient instance (creates new if None)

    Returns:
        Deserialized state value, or None if not found or error
    """
    try:
        if dapr_client:
            response = dapr_client.get_state(state_store, key)
        else:
            with DaprClient() as client:
                response = client.get_state(state_store, key)

        if response.data:
            value = json.loads(response.data)
            logger.info("state_retrieved", state_store=state_store, key=key)
            return value
        else:
            logger.info("state_not_found", state_store=state_store, key=key)
            return None

    except DaprInternalError as e:
        logger.error("state_get_failed", state_store=state_store, key=key, error=str(e))
        return None


async def publish_event(
    pubsub_name: str,
    topic: str,
    data: Dict[str, Any],
    dapr_client: Optional[DaprClient] = None
) -> bool:
    """
    Publish event to Kafka via Dapr pub/sub.

    Args:
        pubsub_name: Name of the pub/sub component (e.g., "kafka-pubsub")
        topic: Kafka topic name
        data: Event data dictionary
        dapr_client: Optional DaprClient instance (creates new if None)

    Returns:
        True if successful, False otherwise
    """
    try:
        if dapr_client:
            dapr_client.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic,
                data=json.dumps(data),
                data_content_type="application/json"
            )
        else:
            with DaprClient() as client:
                client.publish_event(
                    pubsub_name=pubsub_name,
                    topic_name=topic,
                    data=json.dumps(data),
                    data_content_type="application/json"
                )

        logger.info("event_published", pubsub=pubsub_name, topic=topic)
        return True

    except DaprInternalError as e:
        logger.error("event_publish_failed", pubsub=pubsub_name, topic=topic, error=str(e))
        return False


async def invoke_service(
    app_id: str,
    method: str,
    data: Optional[Dict[str, Any]] = None,
    dapr_client: Optional[DaprClient] = None
) -> Optional[Any]:
    """
    Invoke another service via Dapr service invocation.

    Args:
        app_id: Target service app ID
        method: Method/endpoint to invoke
        data: Optional request data
        dapr_client: Optional DaprClient instance (creates new if None)

    Returns:
        Response data, or None if error
    """
    try:
        if dapr_client:
            response = dapr_client.invoke_method(
                app_id=app_id,
                method_name=method,
                data=json.dumps(data) if data else None,
                http_verb="POST"
            )
        else:
            with DaprClient() as client:
                response = client.invoke_method(
                    app_id=app_id,
                    method_name=method,
                    data=json.dumps(data) if data else None,
                    http_verb="POST"
                )

        logger.info("service_invoked", app_id=app_id, method=method)
        return json.loads(response.data) if response.data else None

    except DaprInternalError as e:
        logger.error("service_invocation_failed", app_id=app_id, method=method, error=str(e))
        return None
