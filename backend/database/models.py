"""
SQLAlchemy ORM Models

Database models for the EmberLearn platform.
Supports PostgreSQL (Neon) with async operations.
"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid4())


# ==================== User Model ====================

class User(Base):
    """User account model."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile
    display_name: Mapped[Optional[str]] = mapped_column(String(100))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="student")  # student, teacher, admin
    
    # Gamification
    xp: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    last_activity_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    progress: Mapped[list["Progress"]] = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[list["ExerciseSubmission"]] = relationship("ExerciseSubmission", back_populates="user", cascade="all, delete-orphan")
    chat_sessions: Mapped[list["ChatSession"]] = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    struggle_alerts: Mapped[list["StruggleAlert"]] = relationship("StruggleAlert", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_level", "level"),
    )


# ==================== Topic Model ====================

class Topic(Base):
    """Python curriculum topic."""
    
    __tablename__ = "topics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(10))  # Emoji
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Content
    concepts: Mapped[Optional[dict]] = mapped_column(JSON)  # List of concepts covered
    prerequisites: Mapped[Optional[list]] = mapped_column(JSON)  # List of prerequisite topic slugs
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    exercises: Mapped[list["Exercise"]] = relationship("Exercise", back_populates="topic", cascade="all, delete-orphan")
    progress: Mapped[list["Progress"]] = relationship("Progress", back_populates="topic", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_topics_order", "order"),
    )


# ==================== Exercise Model ====================

class Exercise(Base):
    """Coding exercise/challenge."""
    
    __tablename__ = "exercises"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("topics.id"), nullable=False, index=True)
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[str] = mapped_column(Text, default="# Write your code here\n")
    solution_code: Mapped[Optional[str]] = mapped_column(Text)
    
    # Metadata
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")  # easy, medium, hard
    estimated_time_minutes: Mapped[int] = mapped_column(Integer, default=15)
    xp_reward: Mapped[int] = mapped_column(Integer, default=100)
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Hints (JSON array)
    hints: Mapped[Optional[list]] = mapped_column(JSON)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="exercises")
    test_cases: Mapped[list["TestCase"]] = relationship("TestCase", back_populates="exercise", cascade="all, delete-orphan")
    submissions: Mapped[list["ExerciseSubmission"]] = relationship("ExerciseSubmission", back_populates="exercise", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_exercises_difficulty", "difficulty"),
        Index("ix_exercises_topic_order", "topic_id", "order"),
    )


# ==================== TestCase Model ====================

class TestCase(Base):
    """Test case for an exercise."""
    
    __tablename__ = "test_cases"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    exercise_id: Mapped[str] = mapped_column(String(36), ForeignKey("exercises.id"), nullable=False, index=True)
    
    # Test data
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data: Mapped[str] = mapped_column(Text, default="")
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="test_cases")
    
    __table_args__ = (
        Index("ix_test_cases_exercise_order", "exercise_id", "order"),
    )


# ==================== ExerciseSubmission Model ====================

class ExerciseSubmission(Base):
    """Student submission for an exercise."""
    
    __tablename__ = "exercise_submissions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    exercise_id: Mapped[str] = mapped_column(String(36), ForeignKey("exercises.id"), nullable=False, index=True)
    
    # Submission data
    code: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Results
    score: Mapped[float] = mapped_column(Float, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    tests_passed: Mapped[int] = mapped_column(Integer, default=0)
    tests_total: Mapped[int] = mapped_column(Integer, default=0)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Feedback
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    test_results: Mapped[Optional[dict]] = mapped_column(JSON)  # Detailed test results
    
    # Timestamps
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="submissions")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="submissions")
    
    __table_args__ = (
        Index("ix_submissions_user_exercise", "user_id", "exercise_id"),
        Index("ix_submissions_submitted_at", "submitted_at"),
    )


# ==================== Progress Model ====================

class Progress(Base):
    """Student progress for a topic."""
    
    __tablename__ = "progress"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    topic_id: Mapped[str] = mapped_column(String(36), ForeignKey("topics.id"), nullable=False, index=True)
    
    # Mastery calculation components (weighted average)
    # 40% exercise + 30% quiz + 20% quality + 10% consistency
    exercise_score: Mapped[float] = mapped_column(Float, default=0.0)  # 40%
    quiz_score: Mapped[float] = mapped_column(Float, default=0.0)      # 30%
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)   # 20%
    consistency_score: Mapped[float] = mapped_column(Float, default=0.0)  # 10%
    
    # Calculated mastery
    mastery_score: Mapped[float] = mapped_column(Float, default=0.0)
    mastery_level: Mapped[str] = mapped_column(String(20), default="beginner")
    
    # Completion tracking
    exercises_completed: Mapped[int] = mapped_column(Integer, default=0)
    exercises_total: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="progress")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="progress")
    
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_progress_user_topic"),
        Index("ix_progress_mastery", "mastery_score"),
    )
    
    def calculate_mastery(self) -> float:
        """Calculate weighted mastery score."""
        self.mastery_score = (
            self.exercise_score * 0.4 +
            self.quiz_score * 0.3 +
            self.quality_score * 0.2 +
            self.consistency_score * 0.1
        )
        
        # Update mastery level
        if self.mastery_score <= 40:
            self.mastery_level = "beginner"
        elif self.mastery_score <= 70:
            self.mastery_level = "learning"
        elif self.mastery_score <= 90:
            self.mastery_level = "proficient"
        else:
            self.mastery_level = "mastered"
        
        return self.mastery_score


# ==================== StruggleAlert Model ====================

class StruggleAlert(Base):
    """Alert when a student is struggling."""
    
    __tablename__ = "struggle_alerts"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Alert details
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: repeated_error, stuck_too_long, low_quiz_score, explicit_statement, failed_executions
    
    topic: Mapped[Optional[str]] = mapped_column(String(100))
    exercise_id: Mapped[Optional[str]] = mapped_column(String(36))
    
    # Context
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    severity: Mapped[int] = mapped_column(Integer, default=3)  # 1-5
    
    # Resolution
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    resolved_by: Mapped[Optional[str]] = mapped_column(String(36))  # Teacher user_id
    resolution_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="struggle_alerts")
    
    __table_args__ = (
        Index("ix_struggle_alerts_unresolved", "user_id", "resolved"),
        Index("ix_struggle_alerts_created", "created_at"),
    )


# ==================== ChatSession Model ====================

class ChatSession(Base):
    """Chat session with AI tutor."""
    
    __tablename__ = "chat_sessions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session metadata
    title: Mapped[Optional[str]] = mapped_column(String(200))
    topic: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_chat_sessions_updated", "updated_at"),
    )


# ==================== ChatMessage Model ====================

class ChatMessage(Base):
    """Individual chat message."""
    
    __tablename__ = "chat_messages"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    
    # Message content
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Agent info (for assistant messages)
    agent_type: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Metadata
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    
    __table_args__ = (
        Index("ix_chat_messages_session_created", "session_id", "created_at"),
    )


# ==================== Achievement Model ====================

class Achievement(Base):
    """Achievement/badge definition."""
    
    __tablename__ = "achievements"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    
    # Achievement info
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(10), default="🏆")  # Emoji
    
    # Requirements
    category: Mapped[str] = mapped_column(String(50), default="general")
    xp_reward: Mapped[int] = mapped_column(Integer, default=50)
    criteria: Mapped[Optional[dict]] = mapped_column(JSON)  # Criteria for earning
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


# ==================== UserAchievement Model ====================

class UserAchievement(Base):
    """User's earned achievement."""
    
    __tablename__ = "user_achievements"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    achievement_id: Mapped[str] = mapped_column(String(36), ForeignKey("achievements.id"), nullable=False, index=True)
    
    # Timestamps
    earned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")
    
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )
