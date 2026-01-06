"""
ConceptsAgent - FastAPI + Dapr + OpenAI Agents SDK microservice.

Explains Python concepts with adaptive examples
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
configure_logging("concepts_agent")
logger = structlog.get_logger()

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))



# Agent tools

async def search_documentation(query: str) -> str:
    """Tool: search_documentation"""
    # TODO: Implement search_documentation logic
    logger.info("search_documentation_called", query=query)
    return f"Result from search_documentation"

async def generate_example(query: str) -> str:
    """Tool: generate_example"""
    # TODO: Implement generate_example logic
    logger.info("generate_example_called", query=query)
    return f"Result from generate_example"


# Define the agent
concepts_agent = Agent(
    name="ConceptsAgent",
    instructions="""Explain Python concepts clearly with examples tailored to the student's level.
Use analogies, visual descriptions, and progressively complex examples.
Always validate understanding with follow-up questions.""",
    model="gpt-4o-mini",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("concepts_agent_starting")
    yield
    logger.info("concepts_agent_stopping")


app = FastAPI(
    title="ConceptsAgent Service",
    description="Explains Python concepts with adaptive examples",
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
    return {"status": "healthy", "service": "concepts_agent"}


@app.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies."""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return {"status": "not_ready", "reason": "Missing OPENAI_API_KEY"}, 503
    return {"status": "ready", "service": "concepts_agent"}


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
            concepts_agent,
            input=request.message,
        )

        response_text = result.final_output

        # Publish event to Kafka via Dapr
        event_data = {
            "student_id": request.student_id,
            "agent": "concepts",
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
            agent_used="concepts"
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
            agent_used="concepts"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
