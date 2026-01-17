"""
Progress Agent - Mastery Calculation and Progress Tracking

Tracks student progress using weighted mastery formula:
- 40% Exercise completion
- 30% Quiz scores
- 20% Code quality ratings
- 10% Consistency (streak)
"""

import json
from typing import Optional
from uuid import uuid4
from datetime import datetime, timedelta

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import get_logger
from shared.models import (
    ChatRequest, ChatResponse, AgentType,
    ProgressData, TopicProgress, MasteryLevel
)
from shared.dapr_client import get_dapr_client

logger = get_logger(__name__)

# Mastery calculation weights
WEIGHT_EXERCISE = 0.40
WEIGHT_QUIZ = 0.30
WEIGHT_CODE_QUALITY = 0.20
WEIGHT_CONSISTENCY = 0.10

# XP rewards
XP_EXERCISE_COMPLETE = 50
XP_QUIZ_PASS = 30
XP_STREAK_BONUS = 10
XP_ACHIEVEMENT = 100
XP_LEVEL_THRESHOLD = 500

PROGRESS_PROMPT = """You are a progress tracking assistant for EmberLearn.
Analyze the student's learning data and provide personalized recommendations.

Consider:
1. **Mastery Levels**: Which topics need more practice?
2. **Learning Patterns**: When are they most active?
3. **Strengths**: What are they doing well?
4. **Growth Areas**: Where can they improve?

Be encouraging and specific with recommendations.

Respond with JSON:
{
    "summary": "Brief progress summary",
    "strengths": ["What they're doing well"],
    "focus_areas": ["Topics needing attention"],
    "recommendations": ["Specific next steps"],
    "motivation": "Encouraging message"
}"""


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


class ProgressAgent:
    """Agent that tracks and calculates student progress."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dapr = get_dapr_client()
        self.model = settings.openai_model
        
        # In-memory cache (would use Dapr state store in production)
        self._progress_cache: dict[str, dict] = {}
        self._activity_cache: dict[str, list] = {}
    
    async def get_dashboard(self, user_id: str) -> DashboardResponse:
        """
        Get complete dashboard data for a student.
        
        Aggregates all progress metrics and generates recommendations.
        """
        # Get or initialize progress data
        progress = await self._get_user_progress(user_id)
        
        # Get recent activity
        recent_activity = await self._get_recent_activity(user_id)
        
        # Get achievements
        achievements = await self._get_user_achievements(user_id)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(progress)
        
        return DashboardResponse(
            user_id=user_id,
            overall_mastery=progress.get("overall_mastery", 0),
            overall_level=MasteryLevel.from_score(progress.get("overall_mastery", 0)),
            streak_days=progress.get("streak_days", 0),
            total_xp=progress.get("total_xp", 0),
            level=progress.get("level", 1),
            topics=[
                TopicProgress(
                    topic_id=t["topic_id"],
                    topic_name=t["topic_name"],
                    mastery_score=t["mastery_score"],
                    mastery_level=MasteryLevel.from_score(t["mastery_score"]),
                    exercises_completed=t.get("exercises_completed", 0),
                    exercises_total=t.get("exercises_total", 10),
                    quiz_average=t.get("quiz_average"),
                    code_quality_average=t.get("code_quality_average"),
                )
                for t in progress.get("topics", [])
            ],
            recent_activity=recent_activity,
            achievements=achievements,
            recommendations=recommendations,
        )
    
    async def update_mastery(
        self,
        user_id: str,
        topic_id: str,
        exercise_score: Optional[float] = None,
        quiz_score: Optional[float] = None,
        code_quality_score: Optional[float] = None,
    ) -> MasteryResponse:
        """
        Update mastery score for a topic using weighted formula.
        
        Formula: 40% exercise + 30% quiz + 20% quality + 10% consistency
        """
        # Get current progress
        progress = await self._get_user_progress(user_id)
        topic_data = self._get_topic_data(progress, topic_id)
        
        previous_mastery = topic_data.get("mastery_score", 0)
        
        # Update component scores
        if exercise_score is not None:
            topic_data["exercise_avg"] = self._update_average(
                topic_data.get("exercise_avg", 0),
                topic_data.get("exercise_count", 0),
                exercise_score
            )
            topic_data["exercise_count"] = topic_data.get("exercise_count", 0) + 1
            topic_data["exercises_completed"] = topic_data.get("exercises_completed", 0) + 1
        
        if quiz_score is not None:
            topic_data["quiz_avg"] = self._update_average(
                topic_data.get("quiz_avg", 0),
                topic_data.get("quiz_count", 0),
                quiz_score
            )
            topic_data["quiz_count"] = topic_data.get("quiz_count", 0) + 1
            topic_data["quiz_average"] = topic_data["quiz_avg"]
        
        if code_quality_score is not None:
            topic_data["quality_avg"] = self._update_average(
                topic_data.get("quality_avg", 0),
                topic_data.get("quality_count", 0),
                code_quality_score
            )
            topic_data["quality_count"] = topic_data.get("quality_count", 0) + 1
            topic_data["code_quality_average"] = topic_data["quality_avg"]
        
        # Calculate new mastery using weighted formula
        consistency_score = min(progress.get("streak_days", 0) * 10, 100)
        
        new_mastery = (
            WEIGHT_EXERCISE * topic_data.get("exercise_avg", 0) +
            WEIGHT_QUIZ * topic_data.get("quiz_avg", 0) +
            WEIGHT_CODE_QUALITY * topic_data.get("quality_avg", 0) +
            WEIGHT_CONSISTENCY * consistency_score
        )
        
        topic_data["mastery_score"] = min(new_mastery, 100)
        
        # Calculate XP earned
        xp_earned = 0
        if exercise_score is not None:
            xp_earned += int(XP_EXERCISE_COMPLETE * (exercise_score / 100))
        if quiz_score is not None and quiz_score >= 50:
            xp_earned += XP_QUIZ_PASS
        
        # Update total XP and check for level up
        old_level = progress.get("level", 1)
        progress["total_xp"] = progress.get("total_xp", 0) + xp_earned
        new_level = (progress["total_xp"] // XP_LEVEL_THRESHOLD) + 1
        progress["level"] = new_level
        level_up = new_level > old_level
        
        # Check for achievements
        achievements_unlocked = await self._check_achievements(user_id, progress, topic_data)
        
        # Update overall mastery
        await self._update_overall_mastery(progress)
        
        # Save progress
        await self._save_user_progress(user_id, progress)
        
        # Publish event
        await self._publish_progress_event(user_id, topic_id, new_mastery, xp_earned)
        
        return MasteryResponse(
            topic_id=topic_id,
            previous_mastery=previous_mastery,
            new_mastery=topic_data["mastery_score"],
            mastery_level=MasteryLevel.from_score(topic_data["mastery_score"]),
            xp_earned=xp_earned,
            level_up=level_up,
            achievements_unlocked=achievements_unlocked,
        )
    
    async def get_progress(self, user_id: str) -> ProgressData:
        """Get complete progress data for a student."""
        progress = await self._get_user_progress(user_id)
        
        return ProgressData(
            user_id=user_id,
            overall_mastery=progress.get("overall_mastery", 0),
            overall_level=MasteryLevel.from_score(progress.get("overall_mastery", 0)),
            streak_days=progress.get("streak_days", 0),
            total_xp=progress.get("total_xp", 0),
            level=progress.get("level", 1),
            topics=[
                TopicProgress(
                    topic_id=t["topic_id"],
                    topic_name=t["topic_name"],
                    mastery_score=t["mastery_score"],
                    mastery_level=MasteryLevel.from_score(t["mastery_score"]),
                    exercises_completed=t.get("exercises_completed", 0),
                    exercises_total=t.get("exercises_total", 10),
                )
                for t in progress.get("topics", [])
            ],
            recent_exercises=progress.get("recent_exercises", []),
            achievements=progress.get("achievements", []),
        )
    
    async def get_streak(self, user_id: str) -> StreakResponse:
        """Get streak information for a student."""
        progress = await self._get_user_progress(user_id)
        
        current_streak = progress.get("streak_days", 0)
        longest_streak = progress.get("longest_streak", 0)
        last_activity = progress.get("last_activity_date")
        
        # Check if streak is maintained (activity within last 24 hours)
        streak_maintained = False
        if last_activity:
            last_date = datetime.fromisoformat(last_activity)
            streak_maintained = (datetime.utcnow() - last_date) < timedelta(days=1)
        
        # Calculate bonus XP for streak
        bonus_xp = current_streak * XP_STREAK_BONUS if streak_maintained else 0
        
        return StreakResponse(
            current_streak=current_streak,
            longest_streak=longest_streak,
            streak_maintained=streak_maintained,
            bonus_xp=bonus_xp,
        )
    
    async def record_activity(self, user_id: str, activity_type: str, data: dict) -> dict:
        """Record a learning activity."""
        progress = await self._get_user_progress(user_id)
        
        # Update streak
        last_activity = progress.get("last_activity_date")
        today = datetime.utcnow().date().isoformat()
        
        if last_activity:
            last_date = datetime.fromisoformat(last_activity).date()
            today_date = datetime.utcnow().date()
            
            if last_date == today_date:
                # Same day, no streak change
                pass
            elif (today_date - last_date).days == 1:
                # Consecutive day, increment streak
                progress["streak_days"] = progress.get("streak_days", 0) + 1
                progress["longest_streak"] = max(
                    progress.get("longest_streak", 0),
                    progress["streak_days"]
                )
            else:
                # Streak broken
                progress["streak_days"] = 1
        else:
            progress["streak_days"] = 1
        
        progress["last_activity_date"] = datetime.utcnow().isoformat()
        
        # Add to activity log
        activity = {
            "type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        if user_id not in self._activity_cache:
            self._activity_cache[user_id] = []
        self._activity_cache[user_id].insert(0, activity)
        self._activity_cache[user_id] = self._activity_cache[user_id][:50]  # Keep last 50
        
        await self._save_user_progress(user_id, progress)
        
        return {
            "recorded": True,
            "streak_days": progress["streak_days"],
            "xp_bonus": progress["streak_days"] * XP_STREAK_BONUS,
        }
    
    async def get_achievements(self, user_id: str) -> list[dict]:
        """Get all achievements for a student."""
        return await self._get_user_achievements(user_id)
    
    async def get_leaderboard(self, limit: int = 10) -> list[dict]:
        """Get top students by XP."""
        # In production, this would query the database
        leaderboard = []
        for uid, progress in self._progress_cache.items():
            leaderboard.append({
                "user_id": uid,
                "total_xp": progress.get("total_xp", 0),
                "level": progress.get("level", 1),
                "streak_days": progress.get("streak_days", 0),
            })
        
        leaderboard.sort(key=lambda x: x["total_xp"], reverse=True)
        return leaderboard[:limit]
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Handle progress-related chat requests."""
        # Get user progress
        progress = await self._get_user_progress(request.user_id)
        
        # Generate personalized response
        response_text = await self._generate_progress_summary(request.user_id, progress)
        
        return ChatResponse(
            success=True,
            response=response_text,
            agent_type=AgentType.PROGRESS,
            session_id=request.session_id or str(uuid4()),
        )
    
    async def handle_learning_event(self, event: dict) -> None:
        """Handle learning events from Kafka."""
        event_type = event.get("event_type")
        user_id = event.get("user_id")
        
        if not user_id:
            return
        
        if event_type == "concept_explained":
            await self.record_activity(user_id, "learning", {"topic": event.get("topic")})
        elif event_type == "chat_completed":
            await self.record_activity(user_id, "chat", {})
    
    async def handle_exercise_event(self, event: dict) -> None:
        """Handle exercise events from Kafka."""
        event_type = event.get("event_type")
        user_id = event.get("user_id")
        
        if not user_id:
            return
        
        if event_type == "exercise_graded":
            score = event.get("score", 0)
            exercise_id = event.get("exercise_id")
            # Update mastery based on exercise score
            # Topic would be determined from exercise metadata
            await self.record_activity(user_id, "exercise", {
                "exercise_id": exercise_id,
                "score": score,
            })
    
    # Private helper methods
    
    async def _get_user_progress(self, user_id: str) -> dict:
        """Get or initialize user progress."""
        if user_id not in self._progress_cache:
            # Try to load from Dapr state store
            try:
                state = await self.dapr.get_state(f"progress_{user_id}")
                if state:
                    self._progress_cache[user_id] = state
                else:
                    self._progress_cache[user_id] = self._initialize_progress(user_id)
            except Exception:
                self._progress_cache[user_id] = self._initialize_progress(user_id)
        
        return self._progress_cache[user_id]
    
    def _initialize_progress(self, user_id: str) -> dict:
        """Initialize progress for a new user."""
        topics = [
            {"topic_id": "basics", "topic_name": "Python Basics", "mastery_score": 0},
            {"topic_id": "control_flow", "topic_name": "Control Flow", "mastery_score": 0},
            {"topic_id": "data_structures", "topic_name": "Data Structures", "mastery_score": 0},
            {"topic_id": "functions", "topic_name": "Functions", "mastery_score": 0},
            {"topic_id": "oop", "topic_name": "Object-Oriented Programming", "mastery_score": 0},
            {"topic_id": "files", "topic_name": "File Handling", "mastery_score": 0},
            {"topic_id": "errors", "topic_name": "Error Handling", "mastery_score": 0},
            {"topic_id": "libraries", "topic_name": "Libraries", "mastery_score": 0},
        ]
        
        return {
            "user_id": user_id,
            "overall_mastery": 0,
            "streak_days": 0,
            "longest_streak": 0,
            "total_xp": 0,
            "level": 1,
            "topics": topics,
            "achievements": [],
            "recent_exercises": [],
            "created_at": datetime.utcnow().isoformat(),
        }
    
    def _get_topic_data(self, progress: dict, topic_id: str) -> dict:
        """Get or create topic data."""
        for topic in progress.get("topics", []):
            if topic["topic_id"] == topic_id:
                return topic
        
        # Create new topic
        new_topic = {
            "topic_id": topic_id,
            "topic_name": topic_id.replace("_", " ").title(),
            "mastery_score": 0,
        }
        progress.setdefault("topics", []).append(new_topic)
        return new_topic
    
    def _update_average(self, current_avg: float, count: int, new_value: float) -> float:
        """Update running average."""
        if count == 0:
            return new_value
        return ((current_avg * count) + new_value) / (count + 1)
    
    async def _update_overall_mastery(self, progress: dict) -> None:
        """Update overall mastery from topic scores."""
        topics = progress.get("topics", [])
        if not topics:
            progress["overall_mastery"] = 0
            return
        
        total = sum(t.get("mastery_score", 0) for t in topics)
        progress["overall_mastery"] = total / len(topics)
    
    async def _save_user_progress(self, user_id: str, progress: dict) -> None:
        """Save user progress to cache and state store."""
        self._progress_cache[user_id] = progress
        
        try:
            await self.dapr.save_state(f"progress_{user_id}", progress)
        except Exception as e:
            logger.warning("failed_to_save_progress", error=str(e))
    
    async def _get_recent_activity(self, user_id: str) -> list[dict]:
        """Get recent activity for a user."""
        return self._activity_cache.get(user_id, [])[:10]
    
    async def _get_user_achievements(self, user_id: str) -> list[dict]:
        """Get achievements for a user."""
        progress = await self._get_user_progress(user_id)
        achievement_ids = progress.get("achievements", [])
        
        all_achievements = self._get_all_achievements()
        return [a for a in all_achievements if a["id"] in achievement_ids]
    
    def _get_all_achievements(self) -> list[dict]:
        """Get all possible achievements."""
        return [
            {"id": "first_exercise", "name": "First Steps", "description": "Complete your first exercise", "xp": 100},
            {"id": "streak_3", "name": "On a Roll", "description": "Maintain a 3-day streak", "xp": 150},
            {"id": "streak_7", "name": "Week Warrior", "description": "Maintain a 7-day streak", "xp": 300},
            {"id": "mastery_basics", "name": "Python Basics Master", "description": "Achieve 90% mastery in Basics", "xp": 500},
            {"id": "mastery_loops", "name": "Loop Legend", "description": "Achieve 90% mastery in Control Flow", "xp": 500},
            {"id": "level_5", "name": "Rising Star", "description": "Reach level 5", "xp": 200},
            {"id": "level_10", "name": "Python Pro", "description": "Reach level 10", "xp": 500},
            {"id": "perfect_score", "name": "Perfectionist", "description": "Get 100% on an exercise", "xp": 100},
        ]
    
    async def _check_achievements(self, user_id: str, progress: dict, topic_data: dict) -> list[str]:
        """Check and award new achievements."""
        unlocked = []
        current_achievements = set(progress.get("achievements", []))
        
        # First exercise
        if "first_exercise" not in current_achievements:
            if topic_data.get("exercises_completed", 0) >= 1:
                unlocked.append("first_exercise")
        
        # Streak achievements
        streak = progress.get("streak_days", 0)
        if "streak_3" not in current_achievements and streak >= 3:
            unlocked.append("streak_3")
        if "streak_7" not in current_achievements and streak >= 7:
            unlocked.append("streak_7")
        
        # Mastery achievements
        if topic_data.get("mastery_score", 0) >= 90:
            if topic_data["topic_id"] == "basics" and "mastery_basics" not in current_achievements:
                unlocked.append("mastery_basics")
            if topic_data["topic_id"] == "control_flow" and "mastery_loops" not in current_achievements:
                unlocked.append("mastery_loops")
        
        # Level achievements
        level = progress.get("level", 1)
        if "level_5" not in current_achievements and level >= 5:
            unlocked.append("level_5")
        if "level_10" not in current_achievements and level >= 10:
            unlocked.append("level_10")
        
        # Add unlocked achievements
        if unlocked:
            progress["achievements"] = list(current_achievements | set(unlocked))
            # Add XP for achievements
            all_achievements = {a["id"]: a for a in self._get_all_achievements()}
            for aid in unlocked:
                if aid in all_achievements:
                    progress["total_xp"] = progress.get("total_xp", 0) + all_achievements[aid]["xp"]
        
        return unlocked
    
    async def _generate_recommendations(self, progress: dict) -> list[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        topics = progress.get("topics", [])
        
        # Find weakest topics
        weak_topics = sorted(topics, key=lambda t: t.get("mastery_score", 0))[:2]
        for topic in weak_topics:
            if topic.get("mastery_score", 0) < 50:
                recommendations.append(f"Practice more {topic['topic_name']} exercises")
        
        # Streak recommendation
        if progress.get("streak_days", 0) == 0:
            recommendations.append("Start a learning streak by practicing daily!")
        elif progress.get("streak_days", 0) < 7:
            recommendations.append(f"Keep your {progress['streak_days']}-day streak going!")
        
        # Level-based recommendation
        level = progress.get("level", 1)
        if level < 5:
            recommendations.append("Complete more exercises to level up faster")
        
        return recommendations[:3]
    
    async def _generate_progress_summary(self, user_id: str, progress: dict) -> str:
        """Generate a conversational progress summary."""
        overall = progress.get("overall_mastery", 0)
        level = progress.get("level", 1)
        streak = progress.get("streak_days", 0)
        xp = progress.get("total_xp", 0)
        
        # Find best and weakest topics
        topics = progress.get("topics", [])
        if topics:
            best = max(topics, key=lambda t: t.get("mastery_score", 0))
            weakest = min(topics, key=lambda t: t.get("mastery_score", 0))
        else:
            best = weakest = None
        
        summary = f"📊 **Your Progress Summary**\n\n"
        summary += f"**Level:** {level} ({xp} XP)\n"
        summary += f"**Overall Mastery:** {overall:.1f}%\n"
        summary += f"**Current Streak:** {streak} days 🔥\n\n"
        
        if best:
            summary += f"**Strongest Topic:** {best['topic_name']} ({best.get('mastery_score', 0):.1f}%)\n"
        if weakest and weakest.get("mastery_score", 0) < 70:
            summary += f"**Focus Area:** {weakest['topic_name']} ({weakest.get('mastery_score', 0):.1f}%)\n"
        
        summary += "\nKeep up the great work! 🚀"
        
        return summary
    
    async def _publish_progress_event(
        self,
        user_id: str,
        topic_id: str,
        mastery: float,
        xp_earned: int,
    ) -> None:
        """Publish progress update event."""
        try:
            await self.dapr.publish_event(
                topic=settings.kafka_topic_learning,
                data={
                    "event_type": "mastery_updated",
                    "user_id": user_id,
                    "topic_id": topic_id,
                    "mastery": mastery,
                    "xp_earned": xp_earned,
                },
            )
        except Exception as e:
            logger.warning("failed_to_publish_event", error=str(e))
