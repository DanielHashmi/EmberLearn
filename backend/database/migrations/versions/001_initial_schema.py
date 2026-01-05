"""Initial schema for EmberLearn database.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-01-05

Creates all 10 tables from data-model.md:
- users, topics, progress, exercises, test_cases
- exercise_submissions, quizzes, quiz_attempts, struggle_alerts
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin')")
    op.execute("CREATE TYPE masterylevel AS ENUM ('beginner', 'learning', 'proficient', 'mastered')")
    op.execute("CREATE TYPE struggletrigger AS ENUM ('same_error_3x', 'failed_executions_5x', 'quiz_below_50', 'no_progress_7d', 'explicit_help')")

    # Users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", postgresql.ENUM("student", "teacher", "admin", name="userrole", create_type=False), nullable=False, server_default="student"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uuid"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_uuid", "users", ["uuid"])

    # Topics table
    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("prerequisites", postgresql.JSONB(), nullable=True, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_topics_order", "topics", ["order"])

    # Progress table
    op.create_table(
        "progress",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("exercise_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("quiz_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("code_quality_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("streak_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("mastery_level", postgresql.ENUM("beginner", "learning", "proficient", "mastered", name="masterylevel", create_type=False), nullable=False, server_default="beginner"),
        sa.Column("exercises_completed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_activity", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "topic_id", name="uq_progress_user_topic"),
        sa.CheckConstraint("mastery_score >= 0 AND mastery_score <= 100", name="ck_mastery_score_range"),
    )
    op.create_index("ix_progress_user_id", "progress", ["user_id"])
    op.create_index("ix_progress_topic_id", "progress", ["topic_id"])

    # Exercises table
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.Text(), nullable=False, server_default=""),
        sa.Column("solution_code", sa.Text(), nullable=True),
        sa.Column("difficulty", postgresql.ENUM("beginner", "learning", "proficient", "mastered", name="masterylevel", create_type=False), nullable=False, server_default="beginner"),
        sa.Column("hints", postgresql.JSONB(), nullable=True, server_default="[]"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_exercises_topic_id", "exercises", ["topic_id"])
    op.create_index("ix_exercises_uuid", "exercises", ["uuid"])
    op.create_index("ix_exercises_difficulty", "exercises", ["difficulty"])

    # Test cases table
    op.create_table(
        "test_cases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("expected_output", sa.Text(), nullable=False),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_test_cases_exercise_id", "test_cases", ["exercise_id"])

    # Exercise submissions table
    op.create_table(
        "exercise_submissions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("tests_passed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tests_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("code_review", postgresql.JSONB(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercises.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_submissions_user_id", "exercise_submissions", ["user_id"])
    op.create_index("ix_submissions_exercise_id", "exercise_submissions", ["exercise_id"])
    op.create_index("ix_submissions_submitted_at", "exercise_submissions", ["submitted_at"])

    # Quizzes table
    op.create_table(
        "quizzes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("questions", postgresql.JSONB(), nullable=False),
        sa.Column("passing_score", sa.Float(), nullable=False, server_default="70.0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_quizzes_topic_id", "quizzes", ["topic_id"])

    # Quiz attempts table
    op.create_table(
        "quiz_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.Column("answers", postgresql.JSONB(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["quiz_id"], ["quizzes.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_quiz_attempts_user_id", "quiz_attempts", ["user_id"])
    op.create_index("ix_quiz_attempts_quiz_id", "quiz_attempts", ["quiz_id"])

    # Struggle alerts table
    op.create_table(
        "struggle_alerts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=True),
        sa.Column("trigger", postgresql.ENUM("same_error_3x", "failed_executions_5x", "quiz_below_50", "no_progress_7d", "explicit_help", name="struggletrigger", create_type=False), nullable=False),
        sa.Column("trigger_data", postgresql.JSONB(), nullable=True),
        sa.Column("is_resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_index("ix_struggle_alerts_student_id", "struggle_alerts", ["student_id"])
    op.create_index("ix_struggle_alerts_is_resolved", "struggle_alerts", ["is_resolved"])
    op.create_index("ix_struggle_alerts_created_at", "struggle_alerts", ["created_at"])


def downgrade() -> None:
    op.drop_table("struggle_alerts")
    op.drop_table("quiz_attempts")
    op.drop_table("quizzes")
    op.drop_table("exercise_submissions")
    op.drop_table("test_cases")
    op.drop_table("exercises")
    op.drop_table("progress")
    op.drop_table("topics")
    op.drop_table("users")
    op.execute("DROP TYPE struggletrigger")
    op.execute("DROP TYPE masterylevel")
    op.execute("DROP TYPE userrole")
