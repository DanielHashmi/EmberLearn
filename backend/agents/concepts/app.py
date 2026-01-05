"""Concepts Agent - Explains Python programming concepts."""

import structlog
from fastapi import HTTPException

from agents import Runner
from shared.models import QueryRequest, QueryResponse
from shared.correlation import get_correlation_id
from shared.dapr_client import publish_event, get_state
from agents.base_agent import create_agent_app
from agents.agent_factory import create_agent

logger = structlog.get_logger()

app = create_agent_app(
    service_name="concepts_agent",
    title="Concepts Agent Service",
    description="Explains Python programming concepts with adaptive examples",
)

concepts_agent = create_agent("concepts")


@app.post("/explain", response_model=QueryResponse)
async def explain_concept(request: QueryRequest):
    """Explain a Python concept to the student."""
    correlation_id = get_correlation_id()
    logger.info(
        "concepts_query_received",
        student_id=request.student_id,
        topic=request.topic,
    )

    try:
        # Get student's current level from state
        student_state = await get_state(f"student:{request.student_id}:level")
        level = student_state.get("level", "beginner") if student_state else "beginner"

        # Build context-aware prompt
        prompt = f"""Student level: {level}
Topic: {request.topic or 'general Python'}
Question: {request.query}

Provide a clear explanation appropriate for this student's level."""

        result = await Runner.run(concepts_agent, input=prompt)
        response_text = result.final_output

        # Publish response event
        await publish_event(
            topic="learning.response",
            data={
                "student_id": request.student_id,
                "query": request.query,
                "response": response_text,
                "agent": "concepts",
                "topic": request.topic,
            },
            partition_key=request.student_id,
        )

        logger.info(
            "concepts_explanation_sent",
            student_id=request.student_id,
            response_length=len(response_text),
        )

        return QueryResponse(
            response=response_text,
            agent="concepts",
            correlation_id=correlation_id,
        )

    except Exception as e:
        logger.error("concepts_query_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
