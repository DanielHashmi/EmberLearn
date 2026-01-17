"""Progress service for tracking user mastery, streaks, and XP."""

import uuid
from datetime import date, timedelta
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from models.progress import UserProgress
from models.streak import UserStreak


# Python curriculum topics
TOPICS = [
    {"slug": "basics", "name": "Variables & Types", "total_exercises": 15},
    {"slug": "control-flow", "name": "Control Flow", "total_exercises": 15},
    {"slug": "data-structures", "name": "Data Structures", "total_exercises": 15},
    {"slug": "functions", "name": "Functions", "total_exercises": 15},
    {"slug": "oop", "name": "Object-Oriented Programming", "total_exercises": 15},
    {"slug": "files", "name": "File Handling", "total_exercises": 10},
    {"slug": "errors", "name": "Error Handling", "total_exercises": 10},
    {"slug": "libraries", "name": "Libraries & Packages", "total_exercises": 10},
]

# XP rewards
XP_PER_EXERCISE = 10
XP_STREAK_BONUS_MULTIPLIER = 0.1  # 10% bonus per streak day (capped at 50%)
MAX_STREAK_BONUS = 0.5  # 50% max bonus


class TopicProgressResponse(BaseModel):
    """Response model for topic progress."""
    slug: str
    name: str
    mastery_score: float
    exercises_completed: int
    total_exercises: int


class UserStatsResponse(BaseModel):
    """Response model for user statistics."""
    user_id: str
    streak: int
    longest_streak: int
    total_xp: int
    level: int
    overall_mastery: float
    topics: List[TopicProgressResponse]


class ProgressService:
    """Service for managing user progress, mastery, and streaks."""

    @staticmethod
    def calculate_mastery(
        exercises_completed: int,
        total_exercises: int,
        quiz_score: float = 0.0,
        code_quality_score: float = 0.0,
        streak_bonus: float = 0.0,
    ) -> float:
        """
        Calculate mastery score using weighted formula.
        
        Formula: 40% exercises + 30% quiz + 20% code quality + 10% streak bonus
        
        Args:
            exercises_completed: Number of exercises completed
            total_exercises: Total exercises in topic
            quiz_score: Quiz score (0-100)
            code_quality_score: Code quality score (0-100)
            streak_bonus: Streak bonus percentage (0-100)
            
        Returns:
            Mastery score (0-100)
        """
        exercise_pct = (exercises_completed / max(total_exercises, 1)) * 100
        
        mastery = (
            0.4 * exercise_pct +
            0.3 * quiz_score +
            0.2 * code_quality_score +
            0.1 * streak_bonus
        )
        
        return min(100.0, max(0.0, mastery))

    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """
        Calculate user level from total XP.
        
        Formula: floor(totalXP / 200) + 1
        
        Args:
            total_xp: Total XP earned
            
        Returns:
            User level (minimum 1)
        """
        return (total_xp // 200) + 1

    @staticmethod
    def calculate_xp_with_streak(base_xp: int, current_streak: int) -> int:
        """
        Calculate XP with streak bonus.
        
        Args:
            base_xp: Base XP amount
            current_streak: Current streak count
            
        Returns:
            XP with streak bonus applied
        """
        streak_bonus = min(current_streak * XP_STREAK_BONUS_MULTIPLIER, MAX_STREAK_BONUS)
        return int(base_xp * (1 + streak_bonus))

    @staticmethod
    async def get_or_create_streak(
        db: AsyncSession, 
        user_id: uuid.UUID
    ) -> UserStreak:
        """Get or create user streak record."""
        result = await db.execute(
            select(UserStreak).where(UserStreak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()
        
        if not streak:
            streak = UserStreak(
                user_id=user_id,
                current_streak=0,
                longest_streak=0,
                total_xp=0,
                last_activity_date=None
            )
            db.add(streak)
            await db.flush()
        
        return streak

    @staticmethod
    async def update_streak(
        db: AsyncSession, 
        user_id: uuid.UUID
    ) -> tuple[int, bool]:
        """
        Update user streak based on activity.
        
        Returns:
            Tuple of (new_streak, streak_increased)
        """
        streak = await ProgressService.get_or_create_streak(db, user_id)
        today = date.today()
        
        if streak.last_activity_date is None:
            # First activity ever
            streak.current_streak = 1
            streak.longest_streak = 1
            streak.last_activity_date = today
            await db.flush()
            return (1, True)
        
        days_since_activity = (today - streak.last_activity_date).days
        
        if days_since_activity == 0:
            # Already active today, no change
            return (streak.current_streak, False)
        elif days_since_activity == 1:
            # Consecutive day - increment streak
            streak.current_streak += 1
            streak.longest_streak = max(streak.longest_streak, streak.current_streak)
            streak.last_activity_date = today
            await db.flush()
            return (streak.current_streak, True)
        else:
            # Missed day(s) - reset streak to 1
            streak.current_streak = 1
            streak.last_activity_date = today
            await db.flush()
            return (1, True)

    @staticmethod
    async def add_xp(
        db: AsyncSession, 
        user_id: uuid.UUID, 
        amount: int
    ) -> int:
        """
        Add XP to user's total.
        
        Args:
            db: Database session
            user_id: User ID
            amount: Base XP amount (streak bonus applied automatically)
            
        Returns:
            Total XP after addition
        """
        streak = await ProgressService.get_or_create_streak(db, user_id)
        xp_with_bonus = ProgressService.calculate_xp_with_streak(amount, streak.current_streak)
        streak.total_xp += xp_with_bonus
        await db.flush()
        return streak.total_xp

    @staticmethod
    async def get_or_create_topic_progress(
        db: AsyncSession,
        user_id: uuid.UUID,
        topic_slug: str
    ) -> UserProgress:
        """Get or create progress record for a topic."""
        result = await db.execute(
            select(UserProgress).where(
                and_(
                    UserProgress.user_id == user_id,
                    UserProgress.topic_slug == topic_slug
                )
            )
        )
        progress = result.scalar_one_or_none()
        
        if not progress:
            # Find topic info
            topic_info = next(
                (t for t in TOPICS if t["slug"] == topic_slug),
                {"total_exercises": 15}
            )
            progress = UserProgress(
                user_id=user_id,
                topic_slug=topic_slug,
                mastery_score=0.0,
                exercises_completed=0,
                total_exercises=topic_info["total_exercises"],
                quiz_score=0.0,
                code_quality_score=0.0
            )
            db.add(progress)
            await db.flush()
        
        return progress

    @staticmethod
    async def update_mastery(
        db: AsyncSession,
        user_id: uuid.UUID,
        topic_slug: str,
        exercise_completed: bool = False,
        quiz_score: Optional[float] = None,
        code_quality_score: Optional[float] = None
    ) -> float:
        """
        Update mastery score for a topic.
        
        Args:
            db: Database session
            user_id: User ID
            topic_slug: Topic slug
            exercise_completed: Whether an exercise was completed
            quiz_score: New quiz score (if taken)
            code_quality_score: New code quality score (if evaluated)
            
        Returns:
            Updated mastery score
        """
        progress = await ProgressService.get_or_create_topic_progress(
            db, user_id, topic_slug
        )
        streak = await ProgressService.get_or_create_streak(db, user_id)
        
        if exercise_completed:
            progress.exercises_completed = min(
                progress.exercises_completed + 1,
                progress.total_exercises
            )
        
        if quiz_score is not None:
            progress.quiz_score = quiz_score
        
        if code_quality_score is not None:
            progress.code_quality_score = code_quality_score
        
        # Calculate streak bonus (0-100 scale)
        streak_bonus = min(streak.current_streak * 10, 100)
        
        progress.mastery_score = ProgressService.calculate_mastery(
            exercises_completed=progress.exercises_completed,
            total_exercises=progress.total_exercises,
            quiz_score=progress.quiz_score,
            code_quality_score=progress.code_quality_score,
            streak_bonus=streak_bonus
        )
        
        await db.flush()
        return progress.mastery_score

    @staticmethod
    async def get_topic_progress(
        db: AsyncSession,
        user_id: uuid.UUID,
        topic_slug: str
    ) -> TopicProgressResponse:
        """Get progress for a specific topic."""
        progress = await ProgressService.get_or_create_topic_progress(
            db, user_id, topic_slug
        )
        topic_info = next(
            (t for t in TOPICS if t["slug"] == topic_slug),
            {"name": topic_slug, "total_exercises": 15}
        )
        
        return TopicProgressResponse(
            slug=topic_slug,
            name=topic_info["name"],
            mastery_score=progress.mastery_score,
            exercises_completed=progress.exercises_completed,
            total_exercises=progress.total_exercises
        )

    @staticmethod
    async def get_all_topics_progress(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> List[TopicProgressResponse]:
        """Get progress for all topics."""
        topics_progress = []
        
        for topic in TOPICS:
            progress = await ProgressService.get_topic_progress(
                db, user_id, topic["slug"]
            )
            topics_progress.append(progress)
        
        return topics_progress

    @staticmethod
    async def get_user_stats(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> UserStatsResponse:
        """Get complete user statistics."""
        streak = await ProgressService.get_or_create_streak(db, user_id)
        topics = await ProgressService.get_all_topics_progress(db, user_id)
        
        # Calculate overall mastery as average of all topics
        if topics:
            overall_mastery = sum(t.mastery_score for t in topics) / len(topics)
        else:
            overall_mastery = 0.0
        
        return UserStatsResponse(
            user_id=str(user_id),
            streak=streak.current_streak,
            longest_streak=streak.longest_streak,
            total_xp=streak.total_xp,
            level=ProgressService.calculate_level(streak.total_xp),
            overall_mastery=overall_mastery,
            topics=topics
        )

    @staticmethod
    async def record_activity(
        db: AsyncSession,
        user_id: uuid.UUID
    ) -> tuple[int, int]:
        """
        Record daily activity and update streak.
        
        Returns:
            Tuple of (current_streak, xp_earned)
        """
        new_streak, streak_increased = await ProgressService.update_streak(db, user_id)
        
        # Award bonus XP for maintaining streak
        xp_earned = 0
        if streak_increased and new_streak > 1:
            # Bonus XP for streak continuation
            xp_earned = min(new_streak * 5, 50)  # 5 XP per streak day, max 50
            await ProgressService.add_xp(db, user_id, xp_earned)
        
        return (new_streak, xp_earned)
