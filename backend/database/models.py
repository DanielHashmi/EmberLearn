"""
SQLAlchemy ORM models for EmberLearn database.

Per data-model.md: 10 entities with relationships, validation rules, indexes.
"""

from datetime import datetime
from enum import Enum as PyEnum
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Enums
class UserRole(str, PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class MasteryLevel(str, PyEnum):
    BEGINNER = "beginner"      # 0-40%
    LEARNING = "learning"      # 41-70%
    PROFICIENT = "proficient"  # 71-90%
    MASTERED = "mastered"      # 91-100%


class StruggleTrigger(str, PyEnum):
    SAME_ERROR_3X = "same_error_3x"
    FAILED_EXECUTIONS_5X = "failed_executions_5x"
    QUIZ_BELOW_50 = "quiz_below_50"
    NO_PROGRESS_7D = "no_progress_7d"
    EXPLICIT_HELP = "explicit_help"


# Models
class User(Base):
    """User entity - Students, Teachers, Admins."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("ExerciseSubmission", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    struggle_alerts = relationship("StruggleAlert", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_uuid", "uuid"),
    )


class Topic(Base):
    """Topic entity - 8 Python curriculum modules."""
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    prerequisites = Column(JSONB, default=list)  # List of topic IDs
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    progress = relationship("Progress", back_populates="topic")
    exercises = relationship("Exercise", back_populates="topic")
    quizzes = relationship("Quiz", back_populates="topic")

    __table_args__ = (
        Index("ix_topics_order", "order"),
    )


class Progress(Base):
    """Progress entity - Per-student mastery scores."""
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)

    # Mastery components (per data-model.md lines 133-139)
    exercise_score = Column(Float, default=0.0, nullable=False)  # 40% weight
    quiz_score = Column(Float, default=0.0, nullable=False)      # 30% weight
    code_quality_score = Column(Float, default=0.0, nullable=False)  # 20% weight
    streak_days = Column(Integer, default=0, nullable=False)     # 10% weight

    # Computed mastery score (trigger-updated)
    mastery_score = Column(Float, default=0.0, nullable=False)
    mastery_level = Column(Enum(MasteryLevel), default=MasteryLevel.BEGINNER, nullable=False)

    exercises_completed = Column(Integer, default=0, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", back_populates="progress")

    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_progress_user_topic"),
        Index("ix_progress_user_id", "user_id"),
        Index("ix_progress_topic_id", "topic_id"),
        CheckConstraint("mastery_score >= 0 AND mastery_score <= 100", name="ck_mastery_score_range"),
    )


class Exercise(Base):
    """Exercise entity - Coding challenges."""
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    starter_code = Column(Text, default="", nullable=False)
    solution_code = Column(Text, nullable=True)  # Hidden from students
    difficulty = Column(Enum(MasteryLevel), default=MasteryLevel.BEGINNER, nullable=False)
    hints = Column(JSONB, default=list)  # List of hint strings
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="exercises")
    test_cases = relationship("TestCase", back_populates="exercise", cascade="all, delete-orphan")
    submissions = relationship("ExerciseSubmission", back_populates="exercise")

    __table_args__ = (
        Index("ix_exercises_topic_id", "topic_id"),
        Index("ix_exercises_uuid", "uuid"),
        Index("ix_exercises_difficulty", "difficulty"),
    )


class TestCase(Base):
    """TestCase entity - Exercise validation criteria."""
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    input = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    # Relationships
    exercise = relationship("Exercise", back_populates="test_cases")

    __table_args__ = (
        Index("ix_test_cases_exercise_id", "exercise_id"),
    )


class ExerciseSubmission(Base):
    """ExerciseSubmission entity - Student attempts with auto-grading."""
    __tablename__ = "exercise_submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False)
    code = Column(Text, nullable=False)

    # Grading results
    passed = Column(Boolean, default=False, nullable=False)
    tests_passed = Column(Integer, default=0, nullable=False)
    tests_total = Column(Integer, default=0, nullable=False)
    execution_time_ms = Column(Integer, nullable=True)

    # Code review results (JSONB for flexibility)
    code_review = Column(JSONB, nullable=True)  # {rating, issues, summary}

    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="submissions")
    exercise = relationship("Exercise", back_populates="submissions")

    __table_args__ = (
        Index("ix_submissions_user_id", "user_id"),
        Index("ix_submissions_exercise_id", "exercise_id"),
        Index("ix_submissions_submitted_at", "submitted_at"),
    )


class Quiz(Base):
    """Quiz entity - Multiple-choice assessments."""
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    questions = Column(JSONB, nullable=False)  # List of {question, options, correct_index}
    passing_score = Column(Float, default=70.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz")

    __table_args__ = (
        Index("ix_quizzes_topic_id", "topic_id"),
    )


class QuizAttempt(Base):
    """QuizAttempt entity - Quiz scores."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    answers = Column(JSONB, nullable=False)  # List of selected option indices
    score = Column(Float, nullable=False)
    passed = Column(Boolean, nullable=False)
    attempted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")

    __table_args__ = (
        Index("ix_quiz_attempts_user_id", "user_id"),
        Index("ix_quiz_attempts_quiz_id", "quiz_id"),
    )


class StruggleAlert(Base):
    """StruggleAlert entity - Teacher notifications."""
    __tablename__ = "struggle_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID(as_uuid=True), default=uuid4, unique=True, nullable=False)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    trigger = Column(Enum(StruggleTrigger), nullable=False)
    trigger_data = Column(JSONB, nullable=True)  # Context about the trigger
    is_resolved = Column(Boolean, default=False, nullable=False)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    student = relationship("User", back_populates="struggle_alerts", foreign_keys=[student_id])

    __table_args__ = (
        Index("ix_struggle_alerts_student_id", "student_id"),
        Index("ix_struggle_alerts_is_resolved", "is_resolved"),
        Index("ix_struggle_alerts_created_at", "created_at"),
    )
