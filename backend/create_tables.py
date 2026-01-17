"""Create all database tables."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from database.config import engine, Base
from models import User, UserProgress, Exercise, ExerciseAttempt, UserStreak, ChatMessage


async def create_tables():
    """Drop and create all tables in the database."""
    async with engine.begin() as conn:
        # Drop all existing tables
        await conn.run_sync(Base.metadata.drop_all)
        print("✓ Dropped existing tables")
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("✓ All tables created successfully")


if __name__ == "__main__":
    asyncio.run(create_tables())
