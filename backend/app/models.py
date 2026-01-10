"""SQLAlchemy database models"""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User model"""
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    mastery_score = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc)
    )


class Exercise(Base):
    """Exercise model"""
    __tablename__ = "exercises"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    difficulty = Column(String)  # easy, medium, hard
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class LearningEvent(Base):
    """Learning event for tracking progress"""
    __tablename__ = "learning_events"

    id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    event_type = Column(String)  # exercise_completed, quiz_passed, concept_learned
    topic = Column(String)
    score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
