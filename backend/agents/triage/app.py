"""Triage Agent - Routes student queries to specialist agents."""

import os
import structlog
from fastapi import HTTPException

from agents import Agent, Runner, function_tool
from shared.models import QueryRequest, QueryResponse
from shared.correlation import get_correlation_id
from shared.dapr_client import publish_event
from agents.base_agent import create_agent_app
from agents.agent_factory import create_agent, AGENT_CONFIGS

logger = structlog.get_logger()

app = create_agent_app(
    service_name="triage_agent",
    title="Triage Agent Service",
    description="Routes student queries to appropriate specialist agents",
)

# Create the triage agent with handoff capability
triage_agent = create_agent("triage")


@app.post("/query", response_model=QueryResponse)
async def handle_query(request: QueryRequest):
    """Analyze query and route to appropriate specialist."""
    correlation_id = get_correlation_id()
    logger.info(
        "triage_query_received",
        student_id=request.student_id,
        query_length=len(request.query),
    )

    try:
        # Run triage agent to determine routing
        result = await Runner.run(
            triage_agent,
            input=f"Student query: {request.query}\nTopic context: {request.topic or 'general'}",
        )

        response_text = result.final_output

        # Determine target agent from response
        target_agent = "concepts"  # default
        response_lower = response_text.lower()
        if "code_review" in response_lower or "review" in response_lower:
            target_agent = "code_review"
        elif "debug" in response_lower or "error" in response_lower:
            target_agent = "debug"
        elif "exercise" in response_lower or "challenge" in response_lower:
            target_agent = "exercise"
        elif "progress" in response_lower or "mastery" in response_lower:
            target_agent = "progress"

        # Publish routing event
        await publish_event(
            topic="learning.routed",
            data={
                "student_id": request.student_id,
                "query": request.query,
                "target_agent": target_agent,
                "triage_response": response_text,
            },
            partition_key=request.student_id,
        )

        logger.info(
            "triage_query_routed",
            student_id=request.student_id,
            target_agent=target_agent,
        )

        return QueryResponse(
            response=response_text,
            agent="triage",
            correlation_id=correlation_id,
        )

    except Exception as e:
        logger.error("triage_query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
