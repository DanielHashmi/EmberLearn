"""Progress API endpoints for tracking user mastery, streaks, and XP."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database.config import get_db
from services.progress import ProgressService, TopicProgressResponse, UserStatsResponse
from routers.auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["progress"])


# Response models
class ActivityResponse(BaseModel):
    """Response for recording activity."""
    streak: int
    xp_earned: int
    message: str


class MasteryUpdateResponse(BaseModel):
    """Response for mastery update."""
    topic_slug: str
    mastery_score: float
    message: str


# Endpoints
@router.get("", response_model=UserStatsResponse)
async def get_user_progress(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete user statistics including streak, XP, level, and topic mastery.
    
    Returns user's overall progress across all topics.
    """
    stats = await ProgressService.get_user_stats(db, current_user.id)
    return stats


@router.get("/topics", response_model=List[TopicProgressResponse])
async def get_topics_progress(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get per-topic mastery progress.
    
    Returns mastery scores and exercise completion for each Python topic.
    """
    topics = await ProgressService.get_all_topics_progress(db, current_user.id)
    return topics


@router.get("/topics/{topic_slug}", response_model=TopicProgressResponse)
async def get_topic_progress(
    topic_slug: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get progress for a specific topic.
    
    Args:
        topic_slug: The topic identifier (e.g., 'basics', 'control-flow')
    """
    # Validate topic exists
    valid_topics = [
        "basics", "control-flow", "data-structures", "functions",
        "oop", "files", "errors", "libraries"
    ]
    if topic_slug not in valid_topics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_slug}' not found"
        )
    
    progress = await ProgressService.get_topic_progress(db, current_user.id, topic_slug)
    return progress


@router.post("/activity", response_model=ActivityResponse)
async def record_activity(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record daily activity for streak tracking.
    
    Call this endpoint when user performs any learning activity.
    Updates streak count and awards bonus XP for consecutive days.
    """
    streak, xp_earned = await ProgressService.record_activity(db, current_user.id)
    await db.commit()
    
    if xp_earned > 0:
        message = f"Streak continued! Day {streak} - earned {xp_earned} bonus XP"
    elif streak == 1:
        message = "Activity recorded. Keep learning daily to build your streak!"
    else:
        message = f"Activity recorded. Current streak: {streak} days"
    
    return ActivityResponse(
        streak=streak,
        xp_earned=xp_earned,
        message=message
    )


@router.post("/topics/{topic_slug}/complete-exercise", response_model=MasteryUpdateResponse)
async def complete_exercise(
    topic_slug: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record exercise completion for a topic.
    
    Updates mastery score and awards XP.
    """
    # Validate topic exists
    valid_topics = [
        "basics", "control-flow", "data-structures", "functions",
        "oop", "files", "errors", "libraries"
    ]
    if topic_slug not in valid_topics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Topic '{topic_slug}' not found"
        )
    
    # Update mastery
    mastery = await ProgressService.update_mastery(
        db, current_user.id, topic_slug, exercise_completed=True
    )
    
    # Award XP
    from services.progress import XP_PER_EXERCISE
    await ProgressService.add_xp(db, current_user.id, XP_PER_EXERCISE)
    
    # Update streak
    await ProgressService.update_streak(db, current_user.id)
    
    await db.commit()
    
    return MasteryUpdateResponse(
        topic_slug=topic_slug,
        mastery_score=mastery,
        message=f"Exercise completed! Mastery updated to {mastery:.1f}%"
    )
