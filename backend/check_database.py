#!/usr/bin/env python3
"""Check database contents."""

import asyncio
from sqlalchemy import select, func
from database.config import get_db
from models.exercise import Exercise
from models.user import User

async def check_database():
    """Check what's in the database."""
    print("=" * 50)
    print("DATABASE CHECK")
    print("=" * 50)
    
    async for db in get_db():
        # Check exercises
        result = await db.execute(select(func.count()).select_from(Exercise))
        exercise_count = result.scalar()
        print(f"\n✓ Exercises in database: {exercise_count}")
        
        if exercise_count > 0:
            # Get first few exercises
            result = await db.execute(select(Exercise).limit(3))
            exercises = result.scalars().all()
            
            print("\nFirst 3 exercises:")
            for ex in exercises:
                print(f"  - {ex.title} ({ex.difficulty}) - {ex.topic_name}")
        
        # Check users
        result = await db.execute(select(func.count()).select_from(User))
        user_count = result.scalar()
        print(f"\n✓ Users in database: {user_count}")
        
        if user_count > 0:
            result = await db.execute(select(User).limit(3))
            users = result.scalars().all()
            
            print("\nFirst 3 users:")
            for user in users:
                print(f"  - {user.email} ({user.name})")
        
        print("\n" + "=" * 50)
        print("DATABASE CHECK COMPLETE")
        print("=" * 50)
        
        break  # Only need one iteration

if __name__ == "__main__":
    asyncio.run(check_database())
