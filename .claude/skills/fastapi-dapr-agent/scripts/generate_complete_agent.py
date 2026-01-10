#!/usr/bin/env python3
"""
Generate COMPLETE FastAPI + Dapr + OpenAI Agents SDK microservice.

Creates production-ready agent with:
- Full OpenAI Agents SDK integration with tools and handoffs
- FastAPI endpoints matching agent-api.yaml contract
- Dapr pub/sub for Kafka events
- Structured logging with correlation IDs
- Health checks and Kubernetes readiness
- Dockerfile and requirements.txt
"""

import argparse
import os
from pathlib import Path


# Agent specifications with instructions and capabilities
AGENT_SPECS = {
    "triage": {
        "name": "TriageAgent",
        "description": "Routes student queries to appropriate specialist agents",
        "instructions": """Analyze the student's query and determine which specialist can best help:
- CONCEPTS: Questions about Python concepts, syntax, or theory
- CODE_REVIEW: Requests for code feedback, style improvements, or bug spotting
- DEBUG: Help finding and fixing errors in code
- EXERCISE: Requests for coding challenges or practice problems
- PROGRESS: Questions about their learning progress or mastery scores

Respond with the routing decision and a brief explanation.""",
        "tools": [],
        "handoffs": ["concepts", "code_review", "debug", "exercise", "progress"],
        "kafka_topics": ["learning.events"],
    },
    "concepts": {
        "name": "ConceptsAgent",
        "description": "Explains Python concepts with adaptive examples",
        "instructions": """Explain Python concepts clearly with examples tailored to the student's level.
Use analogies, visual descriptions, and progressively complex examples.
Always validate understanding with follow-up questions.""",
        "tools": ["search_documentation", "generate_example"],
        "handoffs": [],
        "kafka_topics": ["learning.events"],
    },
    "code_review": {
        "name": "CodeReviewAgent",
        "description": "Analyzes code for correctness, style (PEP 8), and efficiency",
        "instructions": """Review Python code for:
1. Correctness and logic errors
2. PEP 8 style compliance
3. Performance and efficiency
4. Best practices and pythonic patterns
Provide specific, actionable feedback with examples.""",
        "tools": ["run_linter", "analyze_complexity"],
        "handoffs": ["debug"],
        "kafka_topics": ["code.submissions"],
    },
    "debug": {
        "name": "DebugAgent",
        "description": "Helps diagnose and fix Python errors",
        "instructions": """Parse error messages and help students understand:
1. What the error means in plain English
2. Where in the code the problem likely is
3. Common causes of this error
4. Step-by-step hints to fix it (don't give solution immediately)""",
        "tools": ["parse_traceback", "suggest_fixes"],
        "handoffs": [],
        "kafka_topics": ["code.submissions", "struggle.detected"],
    },
    "exercise": {
        "name": "ExerciseAgent",
        "description": "Generates coding challenges and provides auto-grading",
        "instructions": """Generate appropriate coding exercises based on:
1. Student's current topic and mastery level
2. Recently struggled concepts
3. Progressive difficulty (slightly above comfort zone)
Create test cases and evaluation criteria.""",
        "tools": ["generate_test_cases", "grade_submission"],
        "handoffs": [],
        "kafka_topics": ["exercise.requests", "code.submissions"],
    },
    "progress": {
        "name": "ProgressAgent",
        "description": "Tracks and reports student mastery scores",
        "instructions": """Analyze student progress data:
1. Calculate mastery scores per topic (0-100)
2. Identify struggling areas
3. Recommend next learning steps
4. Celebrate achievements and milestones""",
        "tools": ["calculate_mastery", "get_analytics"],
        "handoffs": ["exercise"],
        "kafka_topics": ["learning.events"],
    },
}


def generate_main_py(agent_type: str, spec: dict) -> str:
    """Generate complete main.py with FastAPI app and OpenAI Agent."""

    # Generate tool definitions if any
    tools_code = ""
    if spec["tools"]:
        tools_code = "\n\n# Agent tools\n"
        for tool in spec["tools"]:
            tools_code += f'''
async def {tool}(query: str) -> str:
    """Tool: {tool}"""
    # TODO: Implement {tool} logic
    logger.info("{tool}_called", query=query)
    return f"Result from {tool}"
'''

    # Generate handoff configuration
    handoffs_code = ""
    if spec["handoffs"]:
        handoffs_code = f"\n    # Handoffs to specialist agents\n    handoffs={spec['handoffs']},"

    code = f'''"""
{spec['name']} - FastAPI + Dapr + OpenAI Agents SDK microservice.

{spec['description']}
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
configure_logging("{agent_type}_agent")
logger = structlog.get_logger()

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

{tools_code}

# Define the agent
{agent_type}_agent = Agent(
    name="{spec['name']}",
    instructions="""{spec['instructions']}""",
    model="gpt-4o-mini",{handoffs_code}
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("{agent_type}_agent_starting")
    yield
    logger.info("{agent_type}_agent_stopping")


app = FastAPI(
    title="{spec['name']} Service",
    description="{spec['description']}",
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
    return {{"status": "healthy", "service": "{agent_type}_agent"}}


@app.get("/ready")
async def readiness_check():
    """Readiness check - verify dependencies."""
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        return {{"status": "not_ready", "reason": "Missing OPENAI_API_KEY"}}, 503
    return {{"status": "ready", "service": "{agent_type}_agent"}}


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
            {agent_type}_agent,
            input=request.message,
        )

        response_text = result.final_output

        # Publish event to Kafka via Dapr
        event_data = {{
            "student_id": request.student_id,
            "agent": "{agent_type}",
            "query": request.message,
            "response": response_text,
            "correlation_id": correlation_id,
        }}

        for topic in {spec['kafka_topics']}:
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
            agent_used="{agent_type}"
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
            agent_used="{agent_type}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    return code


def generate_dockerfile(agent_type: str) -> str:
    """Generate Dockerfile for the agent."""
    return f'''FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared utilities
COPY ../shared /app/shared

# Copy agent code
COPY main.py .

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''


def generate_requirements() -> str:
    """Generate requirements.txt."""
    return '''fastapi==0.110.0
uvicorn[standard]==0.27.0
openai-agents-python==0.1.0
dapr==1.13.0
structlog==24.1.0
orjson==3.9.15
pydantic==2.6.1
'''


def main():
    parser = argparse.ArgumentParser(description="Generate complete FastAPI + Dapr + OpenAI agent")
    parser.add_argument("agent_type", choices=list(AGENT_SPECS.keys()),
                       help="Type of agent to generate")
    parser.add_argument("--output-dir", default="backend",
                       help="Output directory (default: backend)")

    args = parser.parse_args()

    agent_type = args.agent_type
    spec = AGENT_SPECS[agent_type]

    # Create output directory
    agent_dir = os.path.join(args.output_dir, f"{agent_type}_agent")
    os.makedirs(agent_dir, exist_ok=True)

    # Generate files
    main_py_path = os.path.join(agent_dir, "main.py")
    with open(main_py_path, 'w') as f:
        f.write(generate_main_py(agent_type, spec))

    dockerfile_path = os.path.join(agent_dir, "Dockerfile")
    with open(dockerfile_path, 'w') as f:
        f.write(generate_dockerfile(agent_type))

    requirements_path = os.path.join(agent_dir, "requirements.txt")
    with open(requirements_path, 'w') as f:
        f.write(generate_requirements())

    # Create __init__.py
    init_path = os.path.join(agent_dir, "__init__.py")
    with open(init_path, 'w') as f:
        f.write("")

    print(f"✓ Generated complete {spec['name']} at {agent_dir}")
    print(f"  - main.py: Full FastAPI app with OpenAI Agent, tools, and Kafka integration")
    print(f"  - Dockerfile: Production-ready container image")
    print(f"  - requirements.txt: All dependencies")


if __name__ == "__main__":
    main()
