"""
Pytest configuration and fixtures for EmberLearn backend tests.
"""

import os
import sys

import pytest

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set test environment variables
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRY_HOURS", "24")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio for async tests."""
    return "asyncio"
