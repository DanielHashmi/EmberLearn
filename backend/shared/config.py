"""
Environment Configuration

Centralized configuration management using Pydantic Settings.
Loads from environment variables and .env files.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = "EmberLearn"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    openai_max_tokens: int = 2048
    openai_temperature: float = 0.7
    
    # Database (Neon PostgreSQL)
    database_url: Optional[str] = None
    database_pool_size: int = 5
    database_max_overflow: int = 10
    
    # Dapr
    dapr_http_port: int = 3500
    dapr_grpc_port: int = 50001
    dapr_app_id: str = "emberlearn"
    dapr_pubsub_name: str = "kafka-pubsub"
    dapr_statestore_name: str = "postgres-statestore"
    
    # Kafka Topics
    kafka_topic_learning: str = "learning.events"
    kafka_topic_code: str = "code.events"
    kafka_topic_exercise: str = "exercise.events"
    kafka_topic_struggle: str = "struggle.alerts"
    
    # Code Sandbox
    sandbox_timeout_seconds: int = 5
    sandbox_memory_limit_mb: int = 50
    sandbox_allowed_imports: str = "math,random,datetime,collections,itertools,functools,string,re,json"
    
    # JWT Auth
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: str = "RS256"
    jwt_expiry_hours: int = 24
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins string into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def sandbox_allowed_imports_list(self) -> list[str]:
        """Parse allowed imports string into list."""
        return [imp.strip() for imp in self.sandbox_allowed_imports.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    @property
    def dapr_http_url(self) -> str:
        """Get Dapr HTTP endpoint URL."""
        return f"http://localhost:{self.dapr_http_port}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
