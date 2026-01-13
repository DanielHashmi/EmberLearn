"""Seed exercises data

Revision ID: 002_seed_exercises
Revises: 001_initial
Create Date: 2026-01-10

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


# revision identifiers, used by Alembic.
revision: str = '002_seed_exercises'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Exercise data for all 8 Python topics
EXERCISES = [
    # Topic 1: Basics (Variables & Types)
    {
        "id": str(uuid.uuid4()),
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
        "id": str(uuid.uuid4()),
        "title": "Variable Assignment",
        "description": "Create a variable called 'name' with your name and print it.",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": "# Create a variable 'name' and print it\nname = \n",
        "solution": "name = 'Alice'\nprint(name)",
        "test_cases": [{"input": "", "expected": "Alice"}],
        "estimated_time": 5
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Type Conversion",
        "description": "Convert the string '42' to an integer and print it multiplied by 2.",
        "difficulty": "easy",
        "topic_slug": "basics",
        "topic_name": "Variables & Types",
        "starter_code": "num_str = '42'\n# Convert to int and multiply by 2\n",
        "solution": "num_str = '42'\nresult = int(num_str) * 2\nprint(result)",
        "test_cases": [{"input": "", "expected": "84"}],
        "estimated_time": 5
    },
    
    # Topic 2: Control Flow
    {
        "id": str(uuid.uuid4()),
        "title": "Even or Odd",
        "description": "Write a function that returns 'Even' if a number is even, 'Odd' otherwise.",
        "difficulty": "easy",
        "topic_slug": "control-flow",
        "topic_name": "Control Flow",
        "starter_code": "def even_or_odd(n):\n    # Your code here\n    pass\n",
        "solution": "def even_or_odd(n):\n    if n % 2 == 0:\n        return 'Even'\n    return 'Odd'",
        "test_cases": [
            {"input": "even_or_odd(4)", "expected": "'Even'"},
            {"input": "even_or_odd(7)", "expected": "'Odd'"}
        ],
        "estimated_time": 10
    },
    {
        "id": str(uuid.uuid4()),
        "title": "FizzBuzz",
        "description": "Print numbers 1-15. For multiples of 3 print 'Fizz', for 5 print 'Buzz', for both print 'FizzBuzz'.",
        "difficulty": "medium",
        "topic_slug": "control-flow",
        "topic_name": "Control Flow",
        "starter_code": "def fizzbuzz():\n    # Print 1-15 with FizzBuzz rules\n    pass\n",
        "solution": "def fizzbuzz():\n    for i in range(1, 16):\n        if i % 15 == 0:\n            print('FizzBuzz')\n        elif i % 3 == 0:\n            print('Fizz')\n        elif i % 5 == 0:\n            print('Buzz')\n        else:\n            print(i)",
        "test_cases": [{"input": "fizzbuzz()", "expected": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz"}],
        "estimated_time": 15
    },
    
    # Topic 3: Data Structures
    {
        "id": str(uuid.uuid4()),
        "title": "Sum of List",
        "description": "Write a function that returns the sum of all numbers in a list.",
        "difficulty": "easy",
        "topic_slug": "data-structures",
        "topic_name": "Data Structures",
        "starter_code": "def sum_list(numbers):\n    # Return sum of all numbers\n    pass\n",
        "solution": "def sum_list(numbers):\n    return sum(numbers)",
        "test_cases": [
            {"input": "sum_list([1, 2, 3, 4, 5])", "expected": "15"},
            {"input": "sum_list([])", "expected": "0"}
        ],
        "estimated_time": 10
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Dictionary Lookup",
        "description": "Write a function that returns the value for a key, or 'Not found' if key doesn't exist.",
        "difficulty": "easy",
        "topic_slug": "data-structures",
        "topic_name": "Data Structures",
        "starter_code": "def safe_get(d, key):\n    # Return value or 'Not found'\n    pass\n",
        "solution": "def safe_get(d, key):\n    return d.get(key, 'Not found')",
        "test_cases": [
            {"input": "safe_get({'a': 1, 'b': 2}, 'a')", "expected": "1"},
            {"input": "safe_get({'a': 1}, 'c')", "expected": "'Not found'"}
        ],
        "estimated_time": 10
    },
    
    # Topic 4: Functions
    {
        "id": str(uuid.uuid4()),
        "title": "Factorial",
        "description": "Write a recursive function to calculate factorial of n.",
        "difficulty": "medium",
        "topic_slug": "functions",
        "topic_name": "Functions",
        "starter_code": "def factorial(n):\n    # Calculate n! recursively\n    pass\n",
        "solution": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)",
        "test_cases": [
            {"input": "factorial(5)", "expected": "120"},
            {"input": "factorial(0)", "expected": "1"}
        ],
        "estimated_time": 15
    },
    {
        "id": str(uuid.uuid4()),
        "title": "Default Parameters",
        "description": "Write a function greet(name, greeting='Hello') that returns '{greeting}, {name}!'",
        "difficulty": "easy",
        "topic_slug": "functions",
        "topic_name": "Functions",
        "starter_code": "def greet(name, greeting='Hello'):\n    # Return formatted greeting\n    pass\n",
        "solution": "def greet(name, greeting='Hello'):\n    return f'{greeting}, {name}!'",
        "test_cases": [
            {"input": "greet('Alice')", "expected": "'Hello, Alice!'"},
            {"input": "greet('Bob', 'Hi')", "expected": "'Hi, Bob!'"}
        ],
        "estimated_time": 10
    },
    
    # Topic 5: OOP
    {
        "id": str(uuid.uuid4()),
        "title": "Simple Class",
        "description": "Create a Person class with name and age attributes, and a greet() method.",
        "difficulty": "medium",
        "topic_slug": "oop",
        "topic_name": "Object-Oriented Programming",
        "starter_code": "class Person:\n    def __init__(self, name, age):\n        # Initialize attributes\n        pass\n    \n    def greet(self):\n        # Return 'Hello, I am {name}'\n        pass\n",
        "solution": "class Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def greet(self):\n        return f'Hello, I am {self.name}'",
        "test_cases": [
            {"input": "Person('Alice', 30).greet()", "expected": "'Hello, I am Alice'"}
        ],
        "estimated_time": 15
    },
    
    # Topic 6: Files
    {
        "id": str(uuid.uuid4()),
        "title": "Parse CSV Line",
        "description": "Write a function that parses a CSV line into a list of values.",
        "difficulty": "easy",
        "topic_slug": "files",
        "topic_name": "File Handling",
        "starter_code": "def parse_csv_line(line):\n    # Split by comma and return list\n    pass\n",
        "solution": "def parse_csv_line(line):\n    return line.split(',')",
        "test_cases": [
            {"input": "parse_csv_line('a,b,c')", "expected": "['a', 'b', 'c']"}
        ],
        "estimated_time": 10
    },
    
    # Topic 7: Errors
    {
        "id": str(uuid.uuid4()),
        "title": "Safe Division",
        "description": "Write a function that divides two numbers, returning None if division by zero.",
        "difficulty": "easy",
        "topic_slug": "errors",
        "topic_name": "Error Handling",
        "starter_code": "def safe_divide(a, b):\n    # Return a/b or None if b is 0\n    pass\n",
        "solution": "def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return None",
        "test_cases": [
            {"input": "safe_divide(10, 2)", "expected": "5.0"},
            {"input": "safe_divide(10, 0)", "expected": "None"}
        ],
        "estimated_time": 10
    },
    
    # Topic 8: Libraries
    {
        "id": str(uuid.uuid4()),
        "title": "Random Number",
        "description": "Write a function that returns a random integer between min and max (inclusive).",
        "difficulty": "easy",
        "topic_slug": "libraries",
        "topic_name": "Libraries & Packages",
        "starter_code": "import random\n\ndef random_between(min_val, max_val):\n    # Return random int between min and max\n    pass\n",
        "solution": "import random\n\ndef random_between(min_val, max_val):\n    return random.randint(min_val, max_val)",
        "test_cases": [
            {"input": "1 <= random_between(1, 10) <= 10", "expected": "True"}
        ],
        "estimated_time": 10
    },
]


def upgrade() -> None:
    # Insert exercises
    exercises_table = sa.table(
        'exercises',
        sa.column('id', UUID),
        sa.column('title', sa.String),
        sa.column('description', sa.Text),
        sa.column('difficulty', sa.String),
        sa.column('topic_slug', sa.String),
        sa.column('topic_name', sa.String),
        sa.column('starter_code', sa.Text),
        sa.column('solution', sa.Text),
        sa.column('test_cases', sa.JSON),
        sa.column('estimated_time', sa.Integer),
        sa.column('created_at', sa.DateTime),
    )
    
    from datetime import datetime
    now = datetime.utcnow()
    
    for exercise in EXERCISES:
        op.execute(
            exercises_table.insert().values(
                id=exercise['id'],
                title=exercise['title'],
                description=exercise['description'],
                difficulty=exercise['difficulty'],
                topic_slug=exercise['topic_slug'],
                topic_name=exercise['topic_name'],
                starter_code=exercise['starter_code'],
                solution=exercise['solution'],
                test_cases=exercise['test_cases'],
                estimated_time=exercise['estimated_time'],
                created_at=now,
            )
        )


def downgrade() -> None:
    # Delete all seeded exercises
    op.execute("DELETE FROM exercises")
