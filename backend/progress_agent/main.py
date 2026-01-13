"""
Progress Agent - FastAPI Service

Tracks and calculates student progress by:
- Computing mastery scores using weighted formula
- Aggregating dashboard data
- Tracking streaks and achievements
- Providing progress summaries
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import setup_logging, get_logger
from shared.correlation import CorrelationMiddleware
from shared.models import (
    ChatRequest, ChatResponse, AgentType,
    ProgressData, TopicProgress, MasteryLevel,
    ProgressUpdateRequest
)
from shared.dapr_client import get_dapr_client

from .agent import ProgressAgent

setup_logging(service_name="progress-agent")
logger = get_logger(__name__)

progress_agent: Optional[ProgressAgent] = None


class DashboardResponse(BaseModel):
    """Dashboard data for a student."""
    success: bool = True
    user_id: str
    overall_mastery: float = Field(ge=0, le=100)
    overall_level: MasteryLevel
    streak_days: int
    total_xp: int
    level: int
    topics: list[TopicProgress]
    recent_activity: list[dict]
    achievements: list[dict]
    recommendations: list[str]


class MasteryUpdateRequest(BaseModel):
    """Request to update mastery for a topic."""
    user_id: str
    topic_id: str
    exercise_score: Optional[float] = Field(None, ge=0, le=100)
    quiz_score: Optional[float] = Field(None, ge=0, le=100)
    code_quality_score: Optional[float] = Field(None, ge=0, le=100)


class MasteryResponse(BaseModel):
    """Response with updated mastery."""
    success: bool = True
    topic_id: str
    previous_mastery: float
    new_mastery: float
    mastery_level: MasteryLevel
    xp_earned: int
    level_up: bool = False
    achievements_unlocked: list[str] = Field(default_factory=list)


class StreakResponse(BaseModel):
    """Response with streak information."""
    success: bool = True
    current_streak: int
    longest_streak: int
    streak_maintained: bool
    bonus_xp: int = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global progress_agent
    logger.info("Starting Progress Agent service...")
    progress_agent = ProgressAgent()
    logger.info("Progress Agent service started successfully")
    yield
    logger.info("Shutting down Progress Agent service...")
    dapr = get_dapr_client()
    await dapr.close()


app = FastAPI(
    title="EmberLearn Progress Agent",
    description="Tracks student progress and calculates mastery scores",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CorrelationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "progress-agent"}


@app.get("/ready")
async def readiness_check():
    dapr = get_dapr_client()
    if not await dapr.health_check():
        raise HTTPException(status_code=503, detail="Dapr sidecar not ready")
    return {"status": "ready", "service": "progress-agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle progress-related chat requests.
    
    Provides progress summaries and recommendations.
    """
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info("processing_progress_chat", user_id=request.user_id)
        response = await progress_agent.chat(request)
        return response
    except Exception as e:
        logger.exception("progress_chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard/{user_id}", response_model=DashboardResponse)
async def get_dashboard(user_id: str):
    """
    Get complete dashboard data for a student.
    
    Aggregates all progress metrics and recommendations.
    """
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info("fetching_dashboard", user_id=user_id)
        dashboard = await progress_agent.get_dashboard(user_id)
        return dashboard
    except Exception as e:
        logger.exception("dashboard_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-mastery", response_model=MasteryResponse)
async def update_mastery(request: MasteryUpdateRequest):
    """
    Update mastery score for a topic.
    
    Uses weighted formula: 40% exercise + 30% quiz + 20% quality + 10% consistency
    """
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "updating_mastery",
            user_id=request.user_id,
            topic_id=request.topic_id,
        )
        
        result = await progress_agent.update_mastery(
            user_id=request.user_id,
            topic_id=request.topic_id,
            exercise_score=request.exercise_score,
            quiz_score=request.quiz_score,
            code_quality_score=request.code_quality_score,
        )
        
        logger.info(
            "mastery_updated",
            user_id=request.user_id,
            topic_id=request.topic_id,
            new_mastery=result.new_mastery,
        )
        
        return result
    except Exception as e:
        logger.exception("mastery_update_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/progress/{user_id}", response_model=ProgressData)
async def get_progress(user_id: str):
    """Get complete progress data for a student."""
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        progress = await progress_agent.get_progress(user_id)
        return progress
    except Exception as e:
        logger.exception("get_progress_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/streak/{user_id}", response_model=StreakResponse)
async def get_streak(user_id: str):
    """Get streak information for a student."""
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        streak = await progress_agent.get_streak(user_id)
        return streak
    except Exception as e:
        logger.exception("get_streak_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/record-activity")
async def record_activity(user_id: str, activity_type: str, data: dict = None):
    """Record a learning activity for streak and XP tracking."""
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = await progress_agent.record_activity(user_id, activity_type, data or {})
        return result
    except Exception as e:
        logger.exception("record_activity_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/achievements/{user_id}")
async def get_achievements(user_id: str):
    """Get all achievements for a student."""
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        achievements = await progress_agent.get_achievements(user_id)
        return {"achievements": achievements}
    except Exception as e:
        logger.exception("get_achievements_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/leaderboard")
async def get_leaderboard(limit: int = 10):
    """Get top students by XP."""
    global progress_agent
    
    if not progress_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        leaderboard = await progress_agent.get_leaderboard(limit)
        return {"leaderboard": leaderboard}
    except Exception as e:
        logger.exception("get_leaderboard_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    return [
        {
            "pubsubname": settings.dapr_pubsub_name,
            "topic": settings.kafka_topic_learning,
            "route": "/events/learning",
        },
        {
            "pubsubname": settings.dapr_pubsub_name,
            "topic": settings.kafka_topic_exercise,
            "route": "/events/exercise",
        },
    ]


@app.post("/events/learning")
async def handle_learning_event(event: dict):
    """Handle learning events to update progress."""
    global progress_agent
    
    logger.info("received_learning_event", event_type=event.get("event_type"))
    
    if progress_agent:
        try:
            await progress_agent.handle_learning_event(event)
        except Exception as e:
            logger.exception("handle_learning_event_failed", error=str(e))
    
    return {"status": "SUCCESS"}


@app.post("/events/exercise")
async def handle_exercise_event(event: dict):
    """Handle exercise events to update progress."""
    global progress_agent
    
    logger.info("received_exercise_event", event_type=event.get("event_type"))
    
    if progress_agent:
        try:
            await progress_agent.handle_exercise_event(event)
        except Exception as e:
            logger.exception("handle_exercise_event_failed", error=str(e))
    
    return {"status": "SUCCESS"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=8006, reload=settings.debug)
