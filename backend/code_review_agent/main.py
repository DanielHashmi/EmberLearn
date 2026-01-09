"""
CodeReviewAgent - FastAPI + Dapr + OpenAI Agents SDK microservice.

Analyzes code for correctness, style (PEP 8), and efficiency
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
configure_logging("code_review_agent")
logger = structlog.get_logger()

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# Agent tools

async def run_linter(query: str) -> str:
    """Tool: run_linter"""
    # TODO: Implement run_linter logic
    logger.info("run_linter_called", query=query)
    return f"Result from run_linter"

async def analyze_complexity(query: str) -> str:
    """Tool: analyze_complexity"""
    # TODO: Implement analyze_complexity logic
    logger.info("analyze_complexity_called", query=query)
    return f"Result from analyze_complexity"


# Define the agent
code_review_agent = Agent(
    name="CodeReviewAgent",
    instructions="""Review Python code for:
1. Correctness and logic errors
2. PEP 8 style compliance
3. Performance and efficiency
4. Best practices and pythonic patterns
Provide specific, actionable feedback with examples.""",
    model="gpt-4o-mini",
    # Handoffs to specialist agents
    handoffs=['debug'],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("code_review_agent_starting")
    yield
    logger.info("code_review_agent_stopping")


app = FastAPI(
    title="CodeReviewAgent Service",
    description="Analyzes code for correctness, style (PEP 8), and efficiency",
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
    return {"status": "healthy", "service": "code_review_agent"}


@app.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies."""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return {"status": "not_ready", "reason": "Missing OPENAI_API_KEY"}, 503
    return {"status": "ready", "service": "code_review_agent"}


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
            code_review_agent,
            input=request.message,
        )

        response_text = result.final_output

        # Publish event to Kafka via Dapr
        event_data = {
            "student_id": request.student_id,
            "agent": "code_review",
            "query": request.message,
            "response": response_text,
            "correlation_id": correlation_id,
        }

        for topic in ['code.submissions']:
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
            agent_used="code_review"
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
            agent_used="code_review"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
