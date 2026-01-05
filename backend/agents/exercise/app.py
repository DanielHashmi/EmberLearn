"""Exercise Agent - Generates and grades coding challenges."""

import structlog
from fastapi import HTTPException
from pydantic import BaseModel

from agents import Runner
from shared.correlation import get_correlation_id
from shared.dapr_client import publish_event, get_state
from agents.base_agent import create_agent_app
from agents.agent_factory import create_agent

logger = structlog.get_logger()

app = create_agent_app(
    service_name="exercise_agent",
    title="Exercise Agent Service",
    description="Generates and grades Python coding challenges",
)

exercise_agent = create_agent("exercise")


class GenerateExerciseRequest(BaseModel):
    student_id: str
    topic: str
    difficulty: str | None = None


class Exercise(BaseModel):
    id: str
    title: str
    description: str
    examples: list[dict]
    test_cases: list[dict]
    hints: list[str]
    difficulty: str


class SubmitExerciseRequest(BaseModel):
    student_id: str
    exercise_id: str
    code: str


class SubmissionResult(BaseModel):
    passed: bool
    tests_passed: int
    tests_total: int
    feedback: str
    code_quality_score: int
    correlation_id: str


@app.post("/generate", response_model=Exercise)
async def generate_exercise(request: GenerateExerciseRequest):
    """Generate a new exercise for the student."""
    correlation_id = get_correlation_id()
    logger.info(
        "exercise_generation_requested",
        student_id=request.student_id,
        topic=request.topic,
    )

    try:
        # Get student's mastery level for this topic
        mastery_key = f"student:{request.student_id}:mastery:{request.topic}"
        mastery = await get_state(mastery_key) or {"score": 0.5}

        # Determine difficulty based on mastery
        if request.difficulty:
            difficulty = request.difficulty
        elif mastery["score"] < 0.4:
            difficulty = "beginner"
        elif mastery["score"] < 0.7:
            difficulty = "intermediate"
        else:
            difficulty = "advanced"

        prompt = f"""Generate a Python coding exercise:
Topic: {request.topic}
Difficulty: {difficulty}
Student mastery: {mastery['score']:.0%}

Create an exercise with:
1. Clear title
2. Problem description
3. Input/output examples
4. Test cases
5. Hints (without giving away the solution)"""

        result = await Runner.run(exercise_agent, input=prompt)

        import uuid
        exercise = Exercise(
            id=str(uuid.uuid4()),
            title=f"{request.topic.title()} Challenge",
            description=result.final_output,
            examples=[{"input": "example", "output": "result"}],
            test_cases=[{"input": "test", "expected": "output"}],
            hints=["Think about the problem step by step"],
            difficulty=difficulty,
        )

        # Publish exercise created event
        await publish_event(
            topic="exercise.created",
            data={
                "student_id": request.student_id,
                "exercise_id": exercise.id,
                "topic": request.topic,
                "difficulty": difficulty,
            },
            partition_key=request.student_id,
        )

        logger.info(
            "exercise_generated",
            student_id=request.student_id,
            exercise_id=exercise.id,
        )

        return exercise

    except Exception as e:
        logger.error("exercise_generation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit", response_model=SubmissionResult)
async def submit_exercise(request: SubmitExerciseRequest):
    """Submit and grade an exercise solution."""
    correlation_id = get_correlation_id()
    logger.info(
        "exercise_submission_received",
        student_id=request.student_id,
        exercise_id=request.exercise_id,
    )

    try:
        # In production, this would execute the code in a sandbox
        # and run test cases

        prompt = f"""Grade this Python code submission:

```python
{request.code}
```

Evaluate:
1. Does it solve the problem correctly?
2. Code quality (style, efficiency, readability)
3. Provide constructive feedback"""

        result = await Runner.run(exercise_agent, input=prompt)

        submission_result = SubmissionResult(
            passed=True,  # Would be determined by test execution
            tests_passed=3,
            tests_total=3,
            feedback=result.final_output,
            code_quality_score=80,
            correlation_id=correlation_id,
        )

        # Publish completion event
        await publish_event(
            topic="exercise.completed",
            data={
                "student_id": request.student_id,
                "exercise_id": request.exercise_id,
                "passed": submission_result.passed,
                "score": submission_result.code_quality_score,
            },
            partition_key=request.student_id,
        )

        logger.info(
            "exercise_graded",
            student_id=request.student_id,
            passed=submission_result.passed,
        )

        return submission_result

    except Exception as e:
        logger.error("exercise_submission_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
