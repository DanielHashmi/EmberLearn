import asyncio
import uuid
from datetime import datetime
from sqlalchemy import delete
from database.config import engine
from models.exercise import Exercise, ExerciseAttempt
from models.progress import UserProgress
from models.streak import UserStreak

# Use fixed UUIDs for core exercises to ensure frontend consistency
HELLO_WORLD_ID = uuid.UUID("8b549bf2-7752-457e-9680-596f94b92ec9")
VAR_ASSIGN_ID = uuid.UUID("6008bb50-14cb-4552-9343-0d4002c0609c")

EXERCISES = [
    {
        "id": HELLO_WORLD_ID,
        "title": "Hello World",
        "description": "Write a program that prints 'Hello, World!' to the console.",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": "# Print Hello, World!\n",
        "solution": "print('Hello, World!')",
        "test_cases": [{"input": "", "expected": "Hello, World!"}],
        "estimated_time": 5
    },
    {
        "id": VAR_ASSIGN_ID,
        "title": "Variable Assignment",
        "description": "Create a variable called 'name' with the value 'Alice' and print it.",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": "# Create a variable 'name' and print it\nname = \n",
        "solution": "name = 'Alice'\nprint(name)",
        "test_cases": [{"input": "", "expected": "Alice"}],
        "estimated_time": 5
    }
]

async def reseed():
    async with engine.begin() as conn:
        # Clear existing data
        await conn.execute(delete(ExerciseAttempt))
        await conn.execute(delete(UserProgress))
        await conn.execute(delete(UserStreak))
        await conn.execute(delete(Exercise))
        
        now = datetime.utcnow()
        for ex in EXERCISES:
            await conn.execute(
                Exercise.__table__.insert().values(
                    id=ex['id'],
                    title=ex['title'],
                    description=ex['description'],
                    difficulty=ex['difficulty'],
                    topic_slug=ex['topic_slug'],
                    topic_name=ex['topic_name'],
                    starter_code=ex['starter_code'],
                    solution=ex['solution'],
                    test_cases=ex['test_cases'],
                    estimated_time=ex['estimated_time'],
                    created_at=now
                )
            )
    print("Database re-seeded successfully with fixed IDs")

if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.join(os.getcwd(), "backend"))
    asyncio.run(reseed())
