"""
ProgressAgent - FastAPI + Dapr + OpenAI Agents SDK microservice.

Tracks and reports student mastery scores
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
configure_logging("progress_agent")
logger = structlog.get_logger()

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# Agent tools

async def calculate_mastery(query: str) -> str:
    """Tool: calculate_mastery"""
    # TODO: Implement calculate_mastery logic
    logger.info("calculate_mastery_called", query=query)
    return f"Result from calculate_mastery"

async def get_analytics(query: str) -> str:
    """Tool: get_analytics"""
    # TODO: Implement get_analytics logic
    logger.info("get_analytics_called", query=query)
    return f"Result from get_analytics"


# Define the agent
progress_agent = Agent(
    name="ProgressAgent",
    instructions="""Analyze student progress data:
1. Calculate mastery scores per topic (0-100)
2. Identify struggling areas
3. Recommend next learning steps
4. Celebrate achievements and milestones""",
    model="gpt-4o-mini",
    # Handoffs to specialist agents
    handoffs=['exercise'],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("progress_agent_starting")
    yield
    logger.info("progress_agent_stopping")


app = FastAPI(
    title="ProgressAgent Service",
    description="Tracks and reports student mastery scores",
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
    return {"status": "healthy", "service": "progress_agent"}


@app.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies."""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return {"status": "not_ready", "reason": "Missing OPENAI_API_KEY"}, 503
    return {"status": "ready", "service": "progress_agent"}


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
            progress_agent,
            input=request.message,
        )

        response_text = result.final_output

        # Publish event to Kafka via Dapr
        event_data = {
            "student_id": request.student_id,
            "agent": "progress",
            "query": request.message,
            "response": response_text,
            "correlation_id": correlation_id,
        }

        for topic in ['learning.events']:
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
            agent_used="progress"
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
            agent_used="progress"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
