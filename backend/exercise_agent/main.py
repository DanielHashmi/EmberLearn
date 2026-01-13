"""
Exercise Agent - FastAPI Service

Generates and grades Python coding exercises by:
- Creating exercises tailored to student mastery level
- Generating test cases for validation
- Auto-grading submissions
- Providing feedback on solutions
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
    Exercise, ExerciseRequest, ExerciseResponse,
    Difficulty, TestCase, TestCaseResult
)
from shared.dapr_client import get_dapr_client

from .agent import ExerciseAgent

setup_logging(service_name="exercise-agent")
logger = get_logger(__name__)

exercise_agent: Optional[ExerciseAgent] = None


class GradeRequest(BaseModel):
    """Request to grade a code submission."""
    exercise_id: str
    user_id: str
    code: str = Field(..., min_length=1, max_length=50000)
    test_cases: list[dict] = Field(default_factory=list)


class GradeResponse(BaseModel):
    """Response with grading results."""
    success: bool = True
    score: float = Field(ge=0, le=100)
    passed: bool
    test_results: list[TestCaseResult]
    feedback: str
    hints: list[str] = Field(default_factory=list)
    improved_code: Optional[str] = None


class GenerateRequest(BaseModel):
    """Request to generate an exercise."""
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM
    user_id: str
    mastery_score: Optional[float] = None
    previous_exercises: list[str] = Field(default_factory=list)
    specific_concept: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global exercise_agent
    logger.info("Starting Exercise Agent service...")
    exercise_agent = ExerciseAgent()
    logger.info("Exercise Agent service started successfully")
    yield
    logger.info("Shutting down Exercise Agent service...")
    dapr = get_dapr_client()
    await dapr.close()


app = FastAPI(
    title="EmberLearn Exercise Agent",
    description="Generates and grades Python coding exercises",
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
    return {"status": "healthy", "service": "exercise-agent"}


@app.get("/ready")
async def readiness_check():
    dapr = get_dapr_client()
    if not await dapr.health_check():
        raise HTTPException(status_code=503, detail="Dapr sidecar not ready")
    return {"status": "ready", "service": "exercise-agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Handle exercise-related chat requests.
    
    Can generate exercises or provide hints based on conversation.
    """
    global exercise_agent
    
    if not exercise_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info("processing_exercise_chat", user_id=request.user_id)
        response = await exercise_agent.chat(request)
        return response
    except Exception as e:
        logger.exception("exercise_chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate", response_model=ExerciseResponse)
async def generate_exercise(request: GenerateRequest):
    """
    Generate a new exercise based on topic and difficulty.
    
    Adapts to student's mastery level and avoids repeating exercises.
    """
    global exercise_agent
    
    if not exercise_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "generating_exercise",
            user_id=request.user_id,
            topic=request.topic,
            difficulty=request.difficulty,
        )
        
        exercise = await exercise_agent.generate(
            topic=request.topic,
            difficulty=request.difficulty,
            user_id=request.user_id,
            mastery_score=request.mastery_score,
            previous_exercises=request.previous_exercises,
            specific_concept=request.specific_concept,
        )
        
        logger.info(
            "exercise_generated",
            user_id=request.user_id,
            exercise_id=exercise.id,
        )
        
        return ExerciseResponse(exercise=exercise)
    except Exception as e:
        logger.exception("generate_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/grade", response_model=GradeResponse)
async def grade_submission(request: GradeRequest):
    """
    Grade a code submission against test cases.
    
    Provides detailed feedback and hints for improvement.
    """
    global exercise_agent
    
    if not exercise_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "grading_submission",
            user_id=request.user_id,
            exercise_id=request.exercise_id,
        )
        
        result = await exercise_agent.grade(
            exercise_id=request.exercise_id,
            user_id=request.user_id,
            code=request.code,
            test_cases=request.test_cases,
        )
        
        logger.info(
            "grading_complete",
            user_id=request.user_id,
            exercise_id=request.exercise_id,
            score=result.score,
            passed=result.passed,
        )
        
        return result
    except Exception as e:
        logger.exception("grading_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/topics")
async def get_topics():
    """Get available exercise topics."""
    return {
        "topics": [
            {"id": "basics", "name": "Python Basics", "subtopics": ["variables", "data_types", "operators", "input_output"]},
            {"id": "control_flow", "name": "Control Flow", "subtopics": ["conditionals", "for_loops", "while_loops", "break_continue"]},
            {"id": "data_structures", "name": "Data Structures", "subtopics": ["lists", "tuples", "dictionaries", "sets"]},
            {"id": "functions", "name": "Functions", "subtopics": ["defining", "parameters", "return_values", "scope"]},
            {"id": "oop", "name": "Object-Oriented Programming", "subtopics": ["classes", "objects", "inheritance", "encapsulation"]},
            {"id": "files", "name": "File Handling", "subtopics": ["reading", "writing", "csv", "json"]},
            {"id": "errors", "name": "Error Handling", "subtopics": ["try_except", "exception_types", "custom_exceptions"]},
            {"id": "libraries", "name": "Libraries", "subtopics": ["importing", "standard_library", "virtual_environments"]},
        ]
    }


@app.get("/exercise/{exercise_id}")
async def get_exercise(exercise_id: str):
    """Get an exercise by ID."""
    global exercise_agent
    
    if not exercise_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    exercise = await exercise_agent.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    return ExerciseResponse(exercise=exercise)


@app.post("/hint")
async def get_hint(exercise_id: str, user_id: str, attempt_count: int = 1):
    """Get a hint for an exercise based on attempt count."""
    global exercise_agent
    
    if not exercise_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    hint = await exercise_agent.get_hint(exercise_id, user_id, attempt_count)
    return {"hint": hint, "attempt_count": attempt_count}


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    return [
        {
            "pubsubname": settings.dapr_pubsub_name,
            "topic": settings.kafka_topic_exercise,
            "route": "/events/exercise",
        }
    ]


@app.post("/events/exercise")
async def handle_exercise_event(event: dict):
    logger.info("received_exercise_event", event_type=event.get("type"))
    return {"status": "SUCCESS"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=8005, reload=settings.debug)
