"""Seed 8 Python topics for curriculum.

Revision ID: 002_seed_topics
Revises: 001_initial_schema
Create Date: 2026-01-05

Seeds the 8 Python curriculum topics from data-model.md.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = "002_seed_topics"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert 8 Python curriculum topics per data-model.md
    op.execute("""
        INSERT INTO topics (name, description, "order", prerequisites) VALUES
        ('Python Basics', 'Variables, data types, operators, input/output', 1, '[]'),
        ('Control Flow', 'If statements, loops (for, while), break/continue', 2, '[1]'),
        ('Functions', 'Defining functions, parameters, return values, scope', 3, '[1, 2]'),
        ('Data Structures', 'Lists, tuples, dictionaries, sets, comprehensions', 4, '[1, 2, 3]'),
        ('Object-Oriented Programming', 'Classes, objects, inheritance, polymorphism', 5, '[1, 2, 3, 4]'),
        ('File Handling', 'Reading/writing files, context managers, CSV/JSON', 6, '[1, 2, 3, 4]'),
        ('Error Handling', 'Try/except, raising exceptions, custom exceptions', 7, '[1, 2, 3]'),
        ('Libraries', 'Standard library, pip, virtual environments, common packages', 8, '[1, 2, 3, 4, 5, 6, 7]')
    """)


def downgrade() -> None:
    op.execute("DELETE FROM topics WHERE name IN ('Python Basics', 'Control Flow', 'Functions', 'Data Structures', 'Object-Oriented Programming', 'File Handling', 'Error Handling', 'Libraries')")
