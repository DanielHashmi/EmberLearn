"""
ExerciseAgent - FastAPI + Dapr + OpenAI Agents SDK microservice.

Generates coding challenges and provides auto-grading
"""

import os
from contextlib import asynccontextmanager
from typing import Optional

import structlog
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from agents import Agent, Runner
from pydantic import BaseModel

import sys
sys.path.append('../..')

from shared.logging_config import configure_logging
from shared.correlation import CorrelationIdMiddleware, get_correlation_id
from shared.dapr_client import publish_event, get_state, save_state


# Configure logging
configure_logging("exercise_agent")
logger = structlog.get_logger()

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# Agent tools

async def generate_test_cases(query: str) -> str:
    """Tool: generate_test_cases"""
    # TODO: Implement generate_test_cases logic
    logger.info("generate_test_cases_called", query=query)
    return f"Result from generate_test_cases"

async def grade_submission(query: str) -> str:
    """Tool: grade_submission"""
    # TODO: Implement grade_submission logic
    logger.info("grade_submission_called", query=query)
    return f"Result from grade_submission"


# Define the agent
exercise_agent = Agent(
    name="ExerciseAgent",
    instructions="""Generate appropriate coding exercises based on:
1. Student's current topic and mastery level
2. Recently struggled concepts
3. Progressive difficulty (slightly above comfort zone)
Create test cases and evaluation criteria.""",
    model="gpt-4o-mini",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("exercise_agent_starting")
    yield
    logger.info("exercise_agent_stopping")


app = FastAPI(
    title="ExerciseAgent Service",
    description="Generates coding challenges and provides auto-grading",
    version="1.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class QueryRequest(BaseModel):
    student_id: int
    message: str
    correlation_id: Optional[str] = None


class QueryResponse(BaseModel):
    correlation_id: str
    status: str
    response: str
    agent_used: str


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {"status": "healthy", "service": "exercise_agent"}


@app.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies."""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return {"status": "not_ready", "reason": "Missing OPENAI_API_KEY"}, 503
    return {"status": "ready", "service": "exercise_agent"}


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle incoming query and generate response using OpenAI Agent."""
    correlation_id = request.correlation_id or get_correlation_id()

    logger.info(
        "query_received",
        student_id=request.student_id,
        message_preview=request.message[:50],
        correlation_id=correlation_id,
    )

    try:
        # Run the agent
        result = await Runner.run(
            exercise_agent,
            input=request.message,
        )

        response_text = result.final_output

        # Publish event to Kafka via Dapr
        event_data = {
            "student_id": request.student_id,
            "agent": "exercise",
            "query": request.message,
            "response": response_text,
            "correlation_id": correlation_id,
        }

        for topic in ['exercise.requests', 'code.submissions']:
            await publish_event(
                pubsub_name="kafka-pubsub",
                topic=topic,
                data=event_data
            )

        logger.info(
            "query_completed",
            student_id=request.student_id,
            correlation_id=correlation_id,
        )

        return QueryResponse(
            correlation_id=correlation_id,
            status="success",
            response=response_text,
            agent_used="exercise"
        )

    except Exception as e:
        logger.error(
            "query_failed",
            student_id=request.student_id,
            error=str(e),
            correlation_id=correlation_id,
        )

        # Return fallback response
        return QueryResponse(
            correlation_id=correlation_id,
            status="error",
            response="I'm having trouble processing your request right now. Please try again.",
            agent_used="exercise"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
