"""Progress Agent - Tracks mastery scores and learning progress."""

import structlog
from fastapi import HTTPException
from pydantic import BaseModel

from agents import Runner
from shared.correlation import get_correlation_id
from shared.dapr_client import publish_event, get_state, save_state
from agents.base_agent import create_agent_app
from agents.agent_factory import create_agent

logger = structlog.get_logger()

app = create_agent_app(
    service_name="progress_agent",
    title="Progress Agent Service",
    description="Tracks mastery scores and learning progress",
)

progress_agent = create_agent("progress")


class ProgressRequest(BaseModel):
    student_id: str


class TopicProgress(BaseModel):
    topic_id: str
    topic_name: str
    mastery_score: float
    mastery_level: str
    exercises_completed: int
    quiz_score: float
    code_quality_avg: float
    streak_days: int


class DashboardResponse(BaseModel):
    student_id: str
    overall_mastery: float
    overall_level: str
    topics: list[TopicProgress]
    recommendations: list[str]
    correlation_id: str


def get_mastery_level(score: float) -> str:
    """Convert mastery score to level name."""
    if score < 0.4:
        return "red"
    elif score < 0.7:
        return "yellow"
    elif score < 0.9:
        return "green"
    return "blue"


def get_mastery_label(level: str) -> str:
    """Get human-readable label for mastery level."""
    labels = {
        "red": "Needs Practice",
        "yellow": "Developing",
        "green": "Proficient",
        "blue": "Mastered",
    }
    return labels.get(level, "Unknown")


PYTHON_TOPICS = [
    ("variables", "Variables and Data Types"),
    ("control_flow", "Control Flow"),
    ("functions", "Functions"),
    ("data_structures", "Data Structures"),
    ("oop", "Object-Oriented Programming"),
    ("file_io", "File I/O"),
    ("error_handling", "Error Handling"),
    ("modules", "Modules and Packages"),
]


@app.post("/calculate")
async def calculate_mastery(request: ProgressRequest):
    """Calculate mastery score for a student."""
    correlation_id = get_correlation_id()
    logger.info("mastery_calculation_requested", student_id=request.student_id)

    try:
        # Get component scores from state
        exercise_key = f"student:{request.student_id}:exercises"
        quiz_key = f"student:{request.student_id}:quizzes"
        quality_key = f"student:{request.student_id}:code_quality"
        streak_key = f"student:{request.student_id}:streak"

        exercises = await get_state(exercise_key) or {"score": 0.5}
        quizzes = await get_state(quiz_key) or {"score": 0.5}
        quality = await get_state(quality_key) or {"score": 0.5}
        streak = await get_state(streak_key) or {"days": 0}

        # Calculate weighted mastery score
        # Exercise: 40%, Quiz: 30%, Code Quality: 20%, Streak: 10%
        streak_bonus = min(streak["days"] / 10, 1.0)  # Max 10 days
        mastery_score = (
            exercises["score"] * 0.4 +
            quizzes["score"] * 0.3 +
            quality["score"] * 0.2 +
            streak_bonus * 0.1
        )

        # Save calculated mastery
        await save_state(
            f"student:{request.student_id}:mastery",
            {"score": mastery_score, "level": get_mastery_level(mastery_score)},
        )

        return {
            "student_id": request.student_id,
            "mastery_score": round(mastery_score, 3),
            "mastery_level": get_mastery_level(mastery_score),
            "components": {
                "exercise_score": exercises["score"],
                "quiz_score": quizzes["score"],
                "code_quality_score": quality["score"],
                "streak_bonus": streak_bonus,
            },
            "correlation_id": correlation_id,
        }

    except Exception as e:
        logger.error("mastery_calculation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dashboard", response_model=DashboardResponse)
async def get_dashboard(request: ProgressRequest):
    """Get comprehensive progress dashboard for a student."""
    correlation_id = get_correlation_id()
    logger.info("dashboard_requested", student_id=request.student_id)

    try:
        topics = []
        total_mastery = 0.0

        for topic_id, topic_name in PYTHON_TOPICS:
            # Get topic-specific progress
            topic_key = f"student:{request.student_id}:topic:{topic_id}"
            topic_data = await get_state(topic_key) or {
                "mastery": 0.5,
                "exercises": 0,
                "quiz": 0.5,
                "quality": 0.5,
                "streak": 0,
            }

            mastery = topic_data.get("mastery", 0.5)
            total_mastery += mastery

            topics.append(TopicProgress(
                topic_id=topic_id,
                topic_name=topic_name,
                mastery_score=mastery,
                mastery_level=get_mastery_level(mastery),
                exercises_completed=topic_data.get("exercises", 0),
                quiz_score=topic_data.get("quiz", 0.5),
                code_quality_avg=topic_data.get("quality", 0.5),
                streak_days=topic_data.get("streak", 0),
            ))

        overall_mastery = total_mastery / len(PYTHON_TOPICS)
        overall_level = get_mastery_level(overall_mastery)

        # Generate recommendations using agent
        weak_topics = [t for t in topics if t.mastery_score < 0.4]
        prompt = f"""Student progress summary:
Overall mastery: {overall_mastery:.0%}
Weak topics: {[t.topic_name for t in weak_topics]}

Provide 3 specific, actionable recommendations to help this student improve."""

        result = await Runner.run(progress_agent, input=prompt)
        recommendations = [result.final_output]

        # Publish progress event
        await publish_event(
            topic="progress.response",
            data={
                "student_id": request.student_id,
                "overall_mastery": overall_mastery,
                "overall_level": overall_level,
            },
            partition_key=request.student_id,
        )

        logger.info(
            "dashboard_generated",
            student_id=request.student_id,
            overall_mastery=overall_mastery,
        )

        return DashboardResponse(
            student_id=request.student_id,
            overall_mastery=overall_mastery,
            overall_level=overall_level,
            topics=topics,
            recommendations=recommendations,
            correlation_id=correlation_id,
        )

    except Exception as e:
        logger.error("dashboard_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
