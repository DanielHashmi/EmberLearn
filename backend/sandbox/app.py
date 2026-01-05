"""
Sandbox Service - FastAPI endpoint for secure code execution.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import structlog

from .executor import execute_code, ExecutionResult

logger = structlog.get_logger()

app = FastAPI(
    title="EmberLearn Sandbox",
    description="Secure Python code execution service",
    version="1.0.0",
)


class CodeExecutionRequest(BaseModel):
    code: str = Field(..., description="Python code to execute", max_length=10000)
    student_id: str = Field(..., description="Student identifier for logging")
    timeout_ms: Optional[int] = Field(
        default=5000,
        description="Execution timeout in milliseconds (max 5000)",
        ge=100,
        le=5000,
    )


class CodeExecutionResponse(BaseModel):
    output: str
    error: Optional[str]
    execution_time_ms: int
    memory_used_bytes: Optional[int]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "sandbox"}


@app.post("/api/sandbox/execute", response_model=CodeExecutionResponse)
async def execute_python_code(request: CodeExecutionRequest) -> CodeExecutionResponse:
    """
    Execute Python code in a secure sandbox.

    Limits:
    - 5 second timeout
    - 50MB memory limit
    - No filesystem access
    - No network access
    - Python standard library only
    """
    logger.info(
        "code_execution_request",
        student_id=request.student_id,
        code_length=len(request.code),
        timeout_ms=request.timeout_ms,
    )

    try:
        result: ExecutionResult = execute_code(
            code=request.code,
            timeout_ms=request.timeout_ms or 5000,
        )

        # Log execution result
        logger.info(
            "code_execution_complete",
            student_id=request.student_id,
            execution_time_ms=result.execution_time_ms,
            timed_out=result.timed_out,
            validation_failed=result.validation_failed,
            has_error=result.error is not None,
        )

        return CodeExecutionResponse(
            output=result.output,
            error=result.error,
            execution_time_ms=result.execution_time_ms,
            memory_used_bytes=result.memory_used_bytes,
        )

    except Exception as e:
        logger.error(
            "code_execution_error",
            student_id=request.student_id,
            error=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
