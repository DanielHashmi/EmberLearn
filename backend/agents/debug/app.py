"""Debug Agent - Helps students fix Python errors."""

import structlog
from fastapi import HTTPException
from pydantic import BaseModel

from agents import Runner
from shared.models import QueryResponse
from shared.correlation import get_correlation_id
from shared.dapr_client import publish_event, get_state, save_state
from agents.base_agent import create_agent_app
from agents.agent_factory import create_agent

logger = structlog.get_logger()

app = create_agent_app(
    service_name="debug_agent",
    title="Debug Agent Service",
    description="Helps students understand and fix Python errors",
)

debug_agent = create_agent("debug")


class DebugRequest(BaseModel):
    student_id: str
    code: str
    error_message: str
    context: str | None = None


class DebugResponse(BaseModel):
    error_type: str
    explanation: str
    likely_cause: str
    suggestions: list[str]
    similar_errors_count: int
    correlation_id: str


@app.post("/analyze-error", response_model=DebugResponse)
async def analyze_error(request: DebugRequest):
    """Analyze an error and provide debugging guidance."""
    correlation_id = get_correlation_id()
    logger.info(
        "debug_request_received",
        student_id=request.student_id,
        error_preview=request.error_message[:100],
    )

    try:
        # Track error history for this student
        error_key = f"student:{request.student_id}:errors"
        error_history = await get_state(error_key) or {"count": 0, "types": []}
        error_history["count"] += 1

        # Extract error type
        error_type = "Unknown"
        if ":" in request.error_message:
            error_type = request.error_message.split(":")[0].strip()
        error_history["types"].append(error_type)

        # Save updated history
        await save_state(error_key, error_history)

        prompt = f"""Debug this Python error:

Code:
```python
{request.code}
```

Error message:
{request.error_message}

Context: {request.context or 'No additional context'}

This student has encountered {error_history['count']} errors so far.

Provide:
1. Error type identification
2. Simple explanation of what the error means
3. Likely cause
4. Step-by-step suggestions to fix (without giving the complete solution)"""

        result = await Runner.run(debug_agent, input=prompt)
        response_text = result.final_output

        debug_result = DebugResponse(
            error_type=error_type,
            explanation=response_text,
            likely_cause="See explanation above",
            suggestions=[],
            similar_errors_count=error_history["types"].count(error_type),
            correlation_id=correlation_id,
        )

        # Publish debug event
        await publish_event(
            topic="learning.response",
            data={
                "student_id": request.student_id,
                "error_type": error_type,
                "agent": "debug",
            },
            partition_key=request.student_id,
        )

        logger.info(
            "debug_analysis_completed",
            student_id=request.student_id,
            error_type=error_type,
        )

        return debug_result

    except Exception as e:
        logger.error("debug_analysis_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
