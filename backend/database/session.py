"""
Database Session Management

Async SQLAlchemy session factory and utilities.
Supports PostgreSQL (Neon) with connection pooling.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from shared.config import settings
from shared.logging_config import get_logger

from .models import Base

logger = get_logger(__name__)

# Database URL handling
def get_database_url() -> str:
    """Get the database URL, converting to async driver if needed."""
    url = settings.database_url
    
    if not url:
        # Fallback to SQLite for development
        logger.warning("No DATABASE_URL set, using SQLite")
        return "sqlite+aiosqlite:///./app.db"
    
    # Convert postgres:// to postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return url


# Create async engine
engine = create_async_engine(
    get_database_url(),
    echo=settings.debug,
    pool_pre_ping=True,
    # Use NullPool for serverless (Neon) to avoid connection issues
    poolclass=NullPool if "neon" in (settings.database_url or "") else None,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    
    Usage in FastAPI:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias for FastAPI dependency injection
get_db = get_async_session


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for getting async database sessions.
    
    Usage:
        async with get_session() as session:
            result = await session.execute(query)
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database tables.
    
    Creates all tables defined in models if they don't exist.
    For production, use Alembic migrations instead.
    """
    logger.info("Initializing database...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Database initialized successfully")


async def close_db() -> None:
    """Close database connections."""
    logger.info("Closing database connections...")
    await engine.dispose()
    logger.info("Database connections closed")


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error("Database connection check failed", error=str(e))
        return False
