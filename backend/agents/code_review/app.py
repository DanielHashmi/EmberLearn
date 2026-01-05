"""Code Review Agent - Analyzes code for correctness, style, and efficiency."""

import structlog
from fastapi import HTTPException
from pydantic import BaseModel

from agents import Runner
from shared.models import QueryResponse
from shared.correlation import get_correlation_id
from shared.dapr_client import publish_event
from agents.base_agent import create_agent_app
from agents.agent_factory import create_agent

logger = structlog.get_logger()

app = create_agent_app(
    service_name="code_review_agent",
    title="Code Review Agent Service",
    description="Analyzes Python code for correctness, style, and efficiency",
)

code_review_agent = create_agent("code_review")


class CodeReviewRequest(BaseModel):
    student_id: str
    code: str
    context: str | None = None


class CodeReviewResponse(BaseModel):
    rating: int
    issues: list[dict]
    suggestions: list[str]
    positive_feedback: list[str]
    summary: str
    correlation_id: str


@app.post("/analyze", response_model=CodeReviewResponse)
async def analyze_code(request: CodeReviewRequest):
    """Analyze submitted code and provide feedback."""
    correlation_id = get_correlation_id()
    logger.info(
        "code_review_received",
        student_id=request.student_id,
        code_length=len(request.code),
    )

    try:
        prompt = f"""Review this Python code:

```python
{request.code}
```

Context: {request.context or 'General code review'}

Provide:
1. Overall rating (0-100)
2. Issues found (with line numbers if applicable)
3. Suggestions for improvement
4. Positive aspects"""

        result = await Runner.run(code_review_agent, input=prompt)
        response_text = result.final_output

        # Parse response into structured format
        # In production, use structured output from the agent
        review_result = CodeReviewResponse(
            rating=75,  # Would be parsed from agent response
            issues=[],
            suggestions=[response_text],
            positive_feedback=["Code submitted for review"],
            summary=response_text,
            correlation_id=correlation_id,
        )

        # Publish review event
        await publish_event(
            topic="code.reviewed",
            data={
                "student_id": request.student_id,
                "rating": review_result.rating,
                "summary": review_result.summary,
            },
            partition_key=request.student_id,
        )

        logger.info(
            "code_review_completed",
            student_id=request.student_id,
            rating=review_result.rating,
        )

        return review_result

    except Exception as e:
        logger.error("code_review_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
