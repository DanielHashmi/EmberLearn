"""User progress model for tracking topic mastery."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database.config import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_slug = Column(String(50), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0, nullable=False)
    exercises_completed = Column(Integer, default=0, nullable=False)
    total_exercises = Column(Integer, default=15, nullable=False)
    quiz_score = Column(Float, default=0.0, nullable=False)
    code_quality_score = Column(Float, default=0.0, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="progress")

    # Unique constraint on user_id + topic_slug
    __table_args__ = (
        {"sqlite_autoincrement": True},
    )

    def __repr__(self):
        return f"<UserProgress {self.topic_slug}: {self.mastery_score}%>"
