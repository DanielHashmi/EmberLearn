"""Application configuration"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "EmberLearn"
    app_version: str = "0.1.0"
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./test.db"  # Local SQLite for dev
    )

    # Auth
    jwt_secret_key: str = os.getenv(
        "JWT_SECRET_KEY",
        "dev-secret-key-change-in-production"
    )
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-4o-mini"

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Kafka (optional, for future integration)
    kafka_bootstrap_servers: str = os.getenv(
        "KAFKA_BOOTSTRAP_SERVERS",
        "localhost:9092"
    )
    kafka_topics: dict = {
        "learning": "learning.events",
        "code": "code.events",
        "exercise": "exercise.events",
        "struggle": "struggle.events",
    }

    # Dapr (optional, for future integration)
    dapr_enabled: bool = os.getenv("DAPR_ENABLED", "false").lower() == "true"
    dapr_host: str = os.getenv("DAPR_HOST", "localhost")
    dapr_port: int = int(os.getenv("DAPR_PORT", "3500"))

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
