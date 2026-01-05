"""Create mastery score calculation trigger.

Revision ID: 003_mastery_triggers
Revises: 002_seed_topics
Create Date: 2026-01-05

Creates PostgreSQL trigger to auto-calculate mastery score using weighted formula:
- 40% exercise completion
- 30% quiz scores
- 20% code quality
- 10% consistency (streak)

Per data-model.md lines 133-139.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers
revision: str = "003_mastery_triggers"
down_revision: Union[str, None] = "002_seed_topics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create function to calculate mastery score
    op.execute("""
        CREATE OR REPLACE FUNCTION calculate_mastery_score()
        RETURNS TRIGGER AS $$
        DECLARE
            new_score FLOAT;
            new_level TEXT;
        BEGIN
            -- Calculate weighted mastery score
            -- 40% exercise + 30% quiz + 20% code quality + 10% streak (max 10 days = 100%)
            new_score := (
                (COALESCE(NEW.exercise_score, 0) * 0.4) +
                (COALESCE(NEW.quiz_score, 0) * 0.3) +
                (COALESCE(NEW.code_quality_score, 0) * 0.2) +
                (LEAST(COALESCE(NEW.streak_days, 0), 10) * 10 * 0.1)
            );

            -- Clamp to 0-100 range
            new_score := GREATEST(0, LEAST(100, new_score));

            -- Determine mastery level based on score
            IF new_score >= 91 THEN
                new_level := 'mastered';
            ELSIF new_score >= 71 THEN
                new_level := 'proficient';
            ELSIF new_score >= 41 THEN
                new_level := 'learning';
            ELSE
                new_level := 'beginner';
            END IF;

            -- Update the record
            NEW.mastery_score := new_score;
            NEW.mastery_level := new_level::masterylevel;
            NEW.updated_at := NOW();

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on progress table
    op.execute("""
        CREATE TRIGGER trigger_calculate_mastery
        BEFORE INSERT OR UPDATE OF exercise_score, quiz_score, code_quality_score, streak_days
        ON progress
        FOR EACH ROW
        EXECUTE FUNCTION calculate_mastery_score();
    """)

    # Create function to update exercise score when submission is graded
    op.execute("""
        CREATE OR REPLACE FUNCTION update_exercise_progress()
        RETURNS TRIGGER AS $$
        DECLARE
            topic_id_val INTEGER;
            total_exercises INTEGER;
            passed_exercises INTEGER;
            new_exercise_score FLOAT;
        BEGIN
            -- Get topic_id from exercise
            SELECT topic_id INTO topic_id_val FROM exercises WHERE id = NEW.exercise_id;

            -- Count total and passed exercises for this user/topic
            SELECT
                COUNT(DISTINCT e.id),
                COUNT(DISTINCT CASE WHEN es.passed THEN e.id END)
            INTO total_exercises, passed_exercises
            FROM exercises e
            LEFT JOIN exercise_submissions es ON e.id = es.exercise_id AND es.user_id = NEW.user_id
            WHERE e.topic_id = topic_id_val AND e.is_active = true;

            -- Calculate exercise score (percentage of passed exercises)
            IF total_exercises > 0 THEN
                new_exercise_score := (passed_exercises::FLOAT / total_exercises::FLOAT) * 100;
            ELSE
                new_exercise_score := 0;
            END IF;

            -- Upsert progress record
            INSERT INTO progress (user_id, topic_id, exercise_score, exercises_completed, last_activity)
            VALUES (NEW.user_id, topic_id_val, new_exercise_score, passed_exercises, NOW())
            ON CONFLICT (user_id, topic_id)
            DO UPDATE SET
                exercise_score = new_exercise_score,
                exercises_completed = passed_exercises,
                last_activity = NOW();

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on exercise_submissions
    op.execute("""
        CREATE TRIGGER trigger_update_exercise_progress
        AFTER INSERT OR UPDATE OF passed
        ON exercise_submissions
        FOR EACH ROW
        EXECUTE FUNCTION update_exercise_progress();
    """)

    # Create function to update quiz score when attempt is recorded
    op.execute("""
        CREATE OR REPLACE FUNCTION update_quiz_progress()
        RETURNS TRIGGER AS $$
        DECLARE
            topic_id_val INTEGER;
            avg_quiz_score FLOAT;
        BEGIN
            -- Get topic_id from quiz
            SELECT topic_id INTO topic_id_val FROM quizzes WHERE id = NEW.quiz_id;

            -- Calculate average quiz score for this user/topic
            SELECT AVG(qa.score) INTO avg_quiz_score
            FROM quiz_attempts qa
            JOIN quizzes q ON qa.quiz_id = q.id
            WHERE qa.user_id = NEW.user_id AND q.topic_id = topic_id_val;

            -- Upsert progress record
            INSERT INTO progress (user_id, topic_id, quiz_score, last_activity)
            VALUES (NEW.user_id, topic_id_val, COALESCE(avg_quiz_score, 0), NOW())
            ON CONFLICT (user_id, topic_id)
            DO UPDATE SET
                quiz_score = COALESCE(avg_quiz_score, 0),
                last_activity = NOW();

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger on quiz_attempts
    op.execute("""
        CREATE TRIGGER trigger_update_quiz_progress
        AFTER INSERT
        ON quiz_attempts
        FOR EACH ROW
        EXECUTE FUNCTION update_quiz_progress();
    """)


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trigger_update_quiz_progress ON quiz_attempts")
    op.execute("DROP FUNCTION IF EXISTS update_quiz_progress()")
    op.execute("DROP TRIGGER IF EXISTS trigger_update_exercise_progress ON exercise_submissions")
    op.execute("DROP FUNCTION IF EXISTS update_exercise_progress()")
    op.execute("DROP TRIGGER IF EXISTS trigger_calculate_mastery ON progress")
    op.execute("DROP FUNCTION IF EXISTS calculate_mastery_score()")
