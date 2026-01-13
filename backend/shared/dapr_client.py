"""
Dapr Client Helper Functions

Provides a simplified interface for Dapr operations:
- State management (get/set/delete)
- Pub/Sub messaging
- Service invocation
"""

import json
from typing import Any, Optional

import httpx

from .config import settings
from .correlation import get_correlation_headers
from .logging_config import get_logger

logger = get_logger(__name__)


class DaprClient:
    """
    Helper class for Dapr sidecar operations.
    
    Uses HTTP API for simplicity and compatibility.
    """
    
    def __init__(
        self,
        dapr_http_port: Optional[int] = None,
        pubsub_name: Optional[str] = None,
        statestore_name: Optional[str] = None,
    ):
        self.dapr_port = dapr_http_port or settings.dapr_http_port
        self.base_url = f"http://localhost:{self.dapr_port}"
        self.pubsub_name = pubsub_name or settings.dapr_pubsub_name
        self.statestore_name = statestore_name or settings.dapr_statestore_name
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client
    
    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    # ==================== State Management ====================
    
    async def get_state(
        self,
        key: str,
        store_name: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Get state value by key.
        
        Args:
            key: State key
            store_name: Override default state store name
            
        Returns:
            State value or None if not found
        """
        store = store_name or self.statestore_name
        client = await self._get_client()
        
        try:
            response = await client.get(
                f"/v1.0/state/{store}/{key}",
                headers=get_correlation_headers(),
            )
            
            if response.status_code == 204:
                return None
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            logger.error("dapr_get_state_failed", key=key, error=str(e))
            raise
    
    async def save_state(
        self,
        key: str,
        value: Any,
        store_name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Save state value.
        
        Args:
            key: State key
            value: Value to store (will be JSON serialized)
            store_name: Override default state store name
            metadata: Optional metadata for the state entry
        """
        store = store_name or self.statestore_name
        client = await self._get_client()
        
        state_entry = {
            "key": key,
            "value": value,
        }
        if metadata:
            state_entry["metadata"] = metadata
        
        try:
            response = await client.post(
                f"/v1.0/state/{store}",
                json=[state_entry],
                headers=get_correlation_headers(),
            )
            response.raise_for_status()
            logger.debug("dapr_state_saved", key=key)
            
        except httpx.HTTPStatusError as e:
            logger.error("dapr_save_state_failed", key=key, error=str(e))
            raise
    
    async def delete_state(
        self,
        key: str,
        store_name: Optional[str] = None,
    ) -> None:
        """
        Delete state by key.
        
        Args:
            key: State key to delete
            store_name: Override default state store name
        """
        store = store_name or self.statestore_name
        client = await self._get_client()
        
        try:
            response = await client.delete(
                f"/v1.0/state/{store}/{key}",
                headers=get_correlation_headers(),
            )
            response.raise_for_status()
            logger.debug("dapr_state_deleted", key=key)
            
        except httpx.HTTPStatusError as e:
            logger.error("dapr_delete_state_failed", key=key, error=str(e))
            raise
    
    # ==================== Pub/Sub ====================
    
    async def publish_event(
        self,
        topic: str,
        data: Any,
        pubsub_name: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """
        Publish event to a topic.
        
        Args:
            topic: Topic name
            data: Event data (will be JSON serialized)
            pubsub_name: Override default pubsub component name
            metadata: Optional metadata for the event
        """
        pubsub = pubsub_name or self.pubsub_name
        client = await self._get_client()
        
        headers = get_correlation_headers()
        headers["Content-Type"] = "application/json"
        
        if metadata:
            for key, value in metadata.items():
                headers[f"metadata.{key}"] = value
        
        try:
            response = await client.post(
                f"/v1.0/publish/{pubsub}/{topic}",
                json=data,
                headers=headers,
            )
            response.raise_for_status()
            logger.info("dapr_event_published", topic=topic)
            
        except httpx.HTTPStatusError as e:
            logger.error("dapr_publish_failed", topic=topic, error=str(e))
            raise
    
    # ==================== Service Invocation ====================
    
    async def invoke_service(
        self,
        app_id: str,
        method: str,
        data: Optional[Any] = None,
        http_method: str = "POST",
    ) -> Any:
        """
        Invoke a method on another service via Dapr.
        
        Args:
            app_id: Target service app ID
            method: Method/endpoint to invoke
            data: Request body data
            http_method: HTTP method (GET, POST, etc.)
            
        Returns:
            Response data from the service
        """
        client = await self._get_client()
        
        try:
            response = await client.request(
                method=http_method,
                url=f"/v1.0/invoke/{app_id}/method/{method}",
                json=data if data else None,
                headers=get_correlation_headers(),
            )
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return None
            
        except httpx.HTTPStatusError as e:
            logger.error(
                "dapr_invoke_failed",
                app_id=app_id,
                method=method,
                error=str(e),
            )
            raise
    
    # ==================== Health Check ====================
    
    async def health_check(self) -> bool:
        """
        Check if Dapr sidecar is healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        client = await self._get_client()
        
        try:
            response = await client.get("/v1.0/healthz")
            return response.status_code == 204
        except Exception:
            return False


# Global client instance (lazy initialization)
_dapr_client: Optional[DaprClient] = None


def get_dapr_client() -> DaprClient:
    """Get the global Dapr client instance."""
    global _dapr_client
    if _dapr_client is None:
        _dapr_client = DaprClient()
    return _dapr_client
