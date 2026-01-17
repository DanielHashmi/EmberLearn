"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-09

Creates all initial tables for EmberLearn platform.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(100)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('role', sa.String(20), default='student'),
        sa.Column('xp', sa.Integer, default=0),
        sa.Column('level', sa.Integer, default=1),
        sa.Column('streak_days', sa.Integer, default=0),
        sa.Column('last_activity_date', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_index('ix_users_level', 'users', ['level'])

    # Topics table
    op.create_table(
        'topics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('icon', sa.String(10)),
        sa.Column('order', sa.Integer, default=0),
        sa.Column('concepts', sa.JSON),
        sa.Column('prerequisites', sa.JSON),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_topics_slug', 'topics', ['slug'])
    op.create_index('ix_topics_order', 'topics', ['order'])

    # Exercises table
    op.create_table(
        'exercises',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('topic_id', sa.String(36), sa.ForeignKey('topics.id'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('instructions', sa.Text, nullable=False),
        sa.Column('starter_code', sa.Text, default='# Write your code here\n'),
        sa.Column('solution_code', sa.Text),
        sa.Column('difficulty', sa.String(20), default='medium'),
        sa.Column('estimated_time_minutes', sa.Integer, default=15),
        sa.Column('xp_reward', sa.Integer, default=100),
        sa.Column('order', sa.Integer, default=0),
        sa.Column('hints', sa.JSON),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_exercises_topic_id', 'exercises', ['topic_id'])
    op.create_index('ix_exercises_difficulty', 'exercises', ['difficulty'])
    op.create_index('ix_exercises_topic_order', 'exercises', ['topic_id', 'order'])

    # Test cases table
    op.create_table(
        'test_cases',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('exercise_id', sa.String(36), sa.ForeignKey('exercises.id'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('input_data', sa.Text, default=''),
        sa.Column('expected_output', sa.Text, nullable=False),
        sa.Column('is_hidden', sa.Boolean, default=False),
        sa.Column('order', sa.Integer, default=0),
    )
    op.create_index('ix_test_cases_exercise_id', 'test_cases', ['exercise_id'])
    op.create_index('ix_test_cases_exercise_order', 'test_cases', ['exercise_id', 'order'])

    # Exercise submissions table
    op.create_table(
        'exercise_submissions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('exercise_id', sa.String(36), sa.ForeignKey('exercises.id'), nullable=False),
        sa.Column('code', sa.Text, nullable=False),
        sa.Column('score', sa.Float, default=0.0),
        sa.Column('passed', sa.Boolean, default=False),
        sa.Column('tests_passed', sa.Integer, default=0),
        sa.Column('tests_total', sa.Integer, default=0),
        sa.Column('execution_time_ms', sa.Integer),
        sa.Column('feedback', sa.Text),
        sa.Column('test_results', sa.JSON),
        sa.Column('submitted_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_submissions_user_id', 'exercise_submissions', ['user_id'])
    op.create_index('ix_submissions_exercise_id', 'exercise_submissions', ['exercise_id'])
    op.create_index('ix_submissions_user_exercise', 'exercise_submissions', ['user_id', 'exercise_id'])
    op.create_index('ix_submissions_submitted_at', 'exercise_submissions', ['submitted_at'])

    # Progress table
    op.create_table(
        'progress',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('topic_id', sa.String(36), sa.ForeignKey('topics.id'), nullable=False),
        sa.Column('exercise_score', sa.Float, default=0.0),
        sa.Column('quiz_score', sa.Float, default=0.0),
        sa.Column('quality_score', sa.Float, default=0.0),
        sa.Column('consistency_score', sa.Float, default=0.0),
        sa.Column('mastery_score', sa.Float, default=0.0),
        sa.Column('mastery_level', sa.String(20), default='beginner'),
        sa.Column('exercises_completed', sa.Integer, default=0),
        sa.Column('exercises_total', sa.Integer, default=0),
        sa.Column('last_activity', sa.DateTime),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_progress_user_id', 'progress', ['user_id'])
    op.create_index('ix_progress_topic_id', 'progress', ['topic_id'])
    op.create_index('ix_progress_mastery', 'progress', ['mastery_score'])
    op.create_unique_constraint('uq_progress_user_topic', 'progress', ['user_id', 'topic_id'])

    # Struggle alerts table
    op.create_table(
        'struggle_alerts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('trigger_type', sa.String(50), nullable=False),
        sa.Column('topic', sa.String(100)),
        sa.Column('exercise_id', sa.String(36)),
        sa.Column('details', sa.JSON),
        sa.Column('severity', sa.Integer, default=3),
        sa.Column('resolved', sa.Boolean, default=False),
        sa.Column('resolved_at', sa.DateTime),
        sa.Column('resolved_by', sa.String(36)),
        sa.Column('resolution_notes', sa.Text),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_struggle_alerts_user_id', 'struggle_alerts', ['user_id'])
    op.create_index('ix_struggle_alerts_unresolved', 'struggle_alerts', ['user_id', 'resolved'])
    op.create_index('ix_struggle_alerts_created', 'struggle_alerts', ['created_at'])

    # Chat sessions table
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(200)),
        sa.Column('topic', sa.String(100)),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_chat_sessions_user_id', 'chat_sessions', ['user_id'])
    op.create_index('ix_chat_sessions_updated', 'chat_sessions', ['updated_at'])

    # Chat messages table
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('session_id', sa.String(36), sa.ForeignKey('chat_sessions.id'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('agent_type', sa.String(50)),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_chat_messages_session_id', 'chat_messages', ['session_id'])
    op.create_index('ix_chat_messages_session_created', 'chat_messages', ['session_id', 'created_at'])

    # Achievements table
    op.create_table(
        'achievements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('slug', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('icon', sa.String(10), default='🏆'),
        sa.Column('category', sa.String(50), default='general'),
        sa.Column('xp_reward', sa.Integer, default=50),
        sa.Column('criteria', sa.JSON),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_achievements_slug', 'achievements', ['slug'])

    # User achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('achievement_id', sa.String(36), sa.ForeignKey('achievements.id'), nullable=False),
        sa.Column('earned_at', sa.DateTime, default=sa.func.now()),
    )
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('ix_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])
    op.create_unique_constraint('uq_user_achievement', 'user_achievements', ['user_id', 'achievement_id'])


def downgrade() -> None:
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('chat_messages')
    op.drop_table('chat_sessions')
    op.drop_table('struggle_alerts')
    op.drop_table('progress')
    op.drop_table('exercise_submissions')
    op.drop_table('test_cases')
    op.drop_table('exercises')
    op.drop_table('topics')
    op.drop_table('users')
