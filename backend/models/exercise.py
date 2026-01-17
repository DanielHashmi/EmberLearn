"""Exercise and attempt models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.config import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    topic_slug = Column(String(50), nullable=False, index=True)
    topic_name = Column(String(100), nullable=False)
    starter_code = Column(Text, nullable=False, default="")
    solution = Column(Text, nullable=False, default="")
    test_cases = Column(JSON, nullable=False, default=list)  # [{input: str, expected: str}]
    estimated_time = Column(Integer, default=10)  # minutes
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    attempts = relationship("ExerciseAttempt", back_populates="exercise", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exercise {self.title}>"


class ExerciseAttempt(Base):
    __tablename__ = "exercise_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)
    score = Column(Integer, default=0, nullable=False)  # 0-100
    passed = Column(Boolean, default=False, nullable=False)
    output = Column(Text, default="", nullable=False)
    error = Column(Text, default="", nullable=True)
    execution_time_ms = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="attempts")
    exercise = relationship("Exercise", back_populates="attempts")

    def __repr__(self):
        return f"<ExerciseAttempt score={self.score}>"
