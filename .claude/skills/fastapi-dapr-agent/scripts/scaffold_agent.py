#!/usr/bin/env python3
"""Scaffold a new FastAPI + Dapr + OpenAI Agent microservice."""

import argparse
import os
from pathlib import Path


MAIN_PY_TEMPLATE = '''"""
{agent_name} - FastAPI + Dapr + OpenAI Agents SDK microservice.

This agent {description}.
"""

import os
from contextlib import asynccontextmanager

import structlog
from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
from agents import Agent, Runner

from shared.logging_config import configure_logging
from shared.correlation import CorrelationIdMiddleware, get_correlation_id
from shared.dapr_client import publish_event, get_state, save_state
from shared.models import QueryRequest, QueryResponse


# Configure logging
configure_logging("{service_name}")
logger = structlog.get_logger()

# OpenAI client
openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Define the agent
{agent_name_lower}_agent = Agent(
    name="{agent_name}",
    instructions="""You are the {agent_name} for EmberLearn, an AI-powered Python tutoring platform.

{agent_instructions}

Always be encouraging and supportive while maintaining accuracy.""",
    model="gpt-4o-mini",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("{service_name}_starting")
    yield
    logger.info("{service_name}_stopping")


app = FastAPI(
    title="{agent_name} Service",
    description="{description}",
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


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes."""
    return {{"status": "healthy", "service": "{service_name}"}}


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Handle incoming query and generate response."""
    correlation_id = get_correlation_id()
    logger.info(
        "query_received",
        student_id=request.student_id,
        topic=request.topic,
        correlation_id=correlation_id,
    )

    try:
        # Run the agent
        result = await Runner.run(
            {agent_name_lower}_agent,
            input=request.query,
        )

        response_text = result.final_output

        # Publish event
        await publish_event(
            topic="{publish_topic}",
            data={{
                "student_id": request.student_id,
                "query": request.query,
                "response": response_text,
                "agent": "{agent_name_lower}",
            }},
            partition_key=request.student_id,
        )

        logger.info(
            "query_processed",
            student_id=request.student_id,
            response_length=len(response_text),
        )

        return QueryResponse(
            response=response_text,
            agent="{agent_name_lower}",
            correlation_id=correlation_id,
        )

    except Exception as e:
        logger.error("query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dapr/subscribe")
async def subscribe():
    """Dapr subscription configuration."""
    return [
        {{
            "pubsubname": "kafka-pubsub",
            "topic": "{subscribe_topic}",
            "route": "/events/{subscribe_topic}",
        }}
    ]


@app.post("/events/{subscribe_topic}")
async def handle_event(request: Request):
    """Handle incoming Dapr pub/sub events."""
    event = await request.json()
    logger.info("event_received", topic="{subscribe_topic}", event=event)

    # Process event based on type
    data = event.get("data", {{}})
    # Add event processing logic here

    return {{"status": "SUCCESS"}}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''


DOCKERFILE_TEMPLATE = '''FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared module
COPY shared/ ./shared/

# Copy agent code
COPY {service_name}/ ./{service_name}/

# Set working directory to agent
WORKDIR /app/{service_name}

# Run the service
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''


REQUIREMENTS_TEMPLATE = '''fastapi>=0.110.0
uvicorn[standard]>=0.27.0
openai-agents>=0.0.3
openai>=1.12.0
dapr>=1.13.0
structlog>=24.1.0
orjson>=3.9.0
pydantic>=2.6.0
httpx>=0.27.0
'''


AGENT_CONFIGS = {
    "triage": {
        "name": "TriageAgent",
        "description": "Routes student queries to appropriate specialist agents",
        "instructions": """Your role is to analyze student queries and route them to the appropriate specialist:
    - Concepts questions -> concepts_agent
    - Code review requests -> code_review_agent
    - Debugging help -> debug_agent
    - Exercise requests -> exercise_agent
    - Progress inquiries -> progress_agent

Analyze the query intent and respond with the appropriate routing decision.""",
        "subscribe_topic": "learning.query",
        "publish_topic": "learning.routed",
    },
    "concepts": {
        "name": "ConceptsAgent",
        "description": "Explains Python concepts with adaptive examples",
        "instructions": """Your role is to explain Python programming concepts clearly and adaptively.
    - Assess the student's current understanding level
    - Provide clear explanations with relevant examples
    - Use analogies appropriate to the student's background
    - Include code snippets that demonstrate the concept
    - Suggest related topics for further learning""",
        "subscribe_topic": "learning.routed",
        "publish_topic": "learning.response",
    },
    "code_review": {
        "name": "CodeReviewAgent",
        "description": "Analyzes code for PEP 8 compliance and efficiency",
        "instructions": """Your role is to review Python code and provide constructive feedback.
    - Check for PEP 8 style compliance
    - Identify potential bugs or issues
    - Suggest performance improvements
    - Recommend better patterns or idioms
    - Be encouraging while being thorough""",
        "subscribe_topic": "code.submitted",
        "publish_topic": "code.reviewed",
    },
    "debug": {
        "name": "DebugAgent",
        "description": "Parses errors and provides debugging hints",
        "instructions": """Your role is to help students debug their Python code.
    - Parse error messages and explain what they mean
    - Identify the likely cause of the error
    - Provide step-by-step debugging guidance
    - Suggest fixes without giving away the complete solution
    - Help students learn debugging strategies""",
        "subscribe_topic": "code.error",
        "publish_topic": "learning.response",
    },
    "exercise": {
        "name": "ExerciseAgent",
        "description": "Generates and auto-grades coding challenges",
        "instructions": """Your role is to create and grade Python coding exercises.
    - Generate exercises appropriate to the student's level
    - Create clear problem statements with examples
    - Define test cases for validation
    - Provide helpful feedback on submissions
    - Track exercise completion for mastery calculation""",
        "subscribe_topic": "exercise.request",
        "publish_topic": "exercise.created",
    },
    "progress": {
        "name": "ProgressAgent",
        "description": "Tracks mastery scores and learning progress",
        "instructions": """Your role is to track and report on student learning progress.
    - Calculate mastery scores based on exercises, quizzes, and code quality
    - Identify areas where students are struggling
    - Suggest topics for review or advancement
    - Generate progress reports and visualizations
    - Detect struggle patterns and alert teachers""",
        "subscribe_topic": "progress.query",
        "publish_topic": "progress.response",
    },
}


def scaffold_agent(agent_type: str, output_dir: Path) -> None:
    """Scaffold a new agent service."""
    if agent_type not in AGENT_CONFIGS:
        print(f"✗ Unknown agent type: {agent_type}")
        print(f"  Available types: {', '.join(AGENT_CONFIGS.keys())}")
        return

    config = AGENT_CONFIGS[agent_type]
    service_name = f"{agent_type}_agent"
    agent_dir = output_dir / service_name

    # Create directory
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Generate main.py
    main_content = MAIN_PY_TEMPLATE.format(
        agent_name=config["name"],
        agent_name_lower=agent_type,
        service_name=service_name,
        description=config["description"],
        agent_instructions=config["instructions"],
        subscribe_topic=config["subscribe_topic"],
        publish_topic=config["publish_topic"],
    )
    (agent_dir / "main.py").write_text(main_content)
    print(f"✓ Created {agent_dir}/main.py")

    # Generate Dockerfile
    dockerfile_content = DOCKERFILE_TEMPLATE.format(service_name=service_name)
    (agent_dir / "Dockerfile").write_text(dockerfile_content)
    print(f"✓ Created {agent_dir}/Dockerfile")

    # Generate requirements.txt
    (agent_dir / "requirements.txt").write_text(REQUIREMENTS_TEMPLATE)
    print(f"✓ Created {agent_dir}/requirements.txt")

    # Create __init__.py
    (agent_dir / "__init__.py").write_text(f'"""{config["name"]} service."""\n')
    print(f"✓ Created {agent_dir}/__init__.py")

    print(f"\n✓ Agent '{agent_type}' scaffolded at {agent_dir}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold FastAPI + Dapr + OpenAI Agent")
    parser.add_argument("agent_type", choices=list(AGENT_CONFIGS.keys()),
                        help="Type of agent to scaffold")
    parser.add_argument("--output", "-o", type=Path, default=Path("backend"),
                        help="Output directory (default: backend)")
    args = parser.parse_args()

    scaffold_agent(args.agent_type, args.output)


if __name__ == "__main__":
    main()
