"""
Code Sandbox Service - FastAPI Service

Executes Python code in a secure sandboxed environment with:
- 5 second timeout
- 50MB memory limit
- No network access
- No filesystem access (except temp)
- Restricted imports (standard library only)
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import setup_logging, get_logger
from shared.correlation import CorrelationMiddleware
from shared.models import (
    CodeExecutionRequest, CodeExecutionResponse,
    TestCaseResult
)
from shared.dapr_client import get_dapr_client

from .executor import CodeExecutor
from .validator import CodeValidator

setup_logging(service_name="sandbox")
logger = get_logger(__name__)

executor: Optional[CodeExecutor] = None
validator: Optional[CodeValidator] = None


class ExecuteRequest(BaseModel):
    """Request to execute code."""
    code: str = Field(..., min_length=1, max_length=50000)
    user_id: str
    timeout_seconds: int = Field(default=5, ge=1, le=30)
    memory_limit_mb: int = Field(default=50, ge=10, le=100)


class ExecuteResponse(BaseModel):
    """Response from code execution."""
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: int
    memory_used_mb: Optional[float] = None
    timed_out: bool = False
    security_violation: Optional[str] = None


class ValidateRequest(BaseModel):
    """Request to validate code safety."""
    code: str = Field(..., min_length=1, max_length=50000)


class ValidateResponse(BaseModel):
    """Response from code validation."""
    safe: bool
    issues: list[dict] = Field(default_factory=list)
    blocked_imports: list[str] = Field(default_factory=list)
    blocked_operations: list[str] = Field(default_factory=list)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global executor, validator
    logger.info("Starting Code Sandbox service...")
    executor = CodeExecutor()
    validator = CodeValidator()
    logger.info("Code Sandbox service started successfully")
    yield
    logger.info("Shutting down Code Sandbox service...")
    dapr = get_dapr_client()
    await dapr.close()


app = FastAPI(
    title="EmberLearn Code Sandbox",
    description="Secure Python code execution environment",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(CorrelationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sandbox"}


@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "sandbox"}


@app.post("/execute", response_model=ExecuteResponse)
async def execute_code(request: ExecuteRequest):
    """
    Execute Python code in a sandboxed environment.
    
    Security constraints:
    - 5 second timeout (configurable up to 30s)
    - 50MB memory limit (configurable up to 100MB)
    - No network access
    - No filesystem access except temp
    - Standard library imports only
    """
    global executor, validator
    
    if not executor or not validator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(
            "executing_code",
            user_id=request.user_id,
            code_length=len(request.code),
            timeout=request.timeout_seconds,
        )
        
        # Validate code safety first
        validation = validator.validate(request.code)
        if not validation["safe"]:
            logger.warning(
                "code_validation_failed",
                user_id=request.user_id,
                issues=validation["issues"],
            )
            return ExecuteResponse(
                success=False,
                error="Code contains unsafe operations",
                execution_time_ms=0,
                security_violation="; ".join(
                    [i["message"] for i in validation["issues"][:3]]
                ),
            )
        
        # Execute code
        result = await executor.execute(
            code=request.code,
            timeout_seconds=request.timeout_seconds,
            memory_limit_mb=request.memory_limit_mb,
        )
        
        logger.info(
            "code_executed",
            user_id=request.user_id,
            success=result["success"],
            execution_time_ms=result["execution_time_ms"],
        )
        
        # Publish event
        await _publish_execution_event(
            request.user_id,
            result["success"],
            result["execution_time_ms"],
        )
        
        return ExecuteResponse(
            success=result["success"],
            output=result.get("output"),
            error=result.get("error"),
            execution_time_ms=result["execution_time_ms"],
            memory_used_mb=result.get("memory_used_mb"),
            timed_out=result.get("timed_out", False),
        )
        
    except Exception as e:
        logger.exception("execution_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/execute-with-tests", response_model=CodeExecutionResponse)
async def execute_with_tests(request: CodeExecutionRequest):
    """
    Execute code and run test cases.
    
    Returns detailed results for each test case.
    """
    global executor, validator
    
    if not executor or not validator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        logger.info(
            "executing_with_tests",
            user_id=request.user_id,
            test_count=len(request.test_cases),
        )
        
        # Validate code safety
        validation = validator.validate(request.code)
        if not validation["safe"]:
            return CodeExecutionResponse(
                success=False,
                error="Code contains unsafe operations",
                execution_time_ms=0,
            )
        
        # Run tests
        test_results = []
        total_time = 0
        passed_count = 0
        
        for tc in request.test_cases:
            result = await executor.execute_test(
                code=request.code,
                test_input=tc.get("input", ""),
                expected_output=tc.get("expected_output", ""),
                timeout_seconds=request.timeout_seconds,
            )
            
            test_results.append(TestCaseResult(
                name=tc.get("name", "Test"),
                passed=result["passed"],
                input=tc.get("input", ""),
                expected_output=tc.get("expected_output", ""),
                actual_output=result.get("actual_output"),
                error=result.get("error"),
                execution_time_ms=result.get("execution_time_ms", 0),
            ))
            
            total_time += result.get("execution_time_ms", 0)
            if result["passed"]:
                passed_count += 1
        
        # Calculate score
        total_count = len(test_results)
        score = (passed_count / total_count * 100) if total_count > 0 else 0
        
        return CodeExecutionResponse(
            success=True,
            execution_time_ms=total_time,
            test_results=test_results,
            passed_count=passed_count,
            total_count=total_count,
            score=score,
        )
        
    except Exception as e:
        logger.exception("test_execution_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate", response_model=ValidateResponse)
async def validate_code(request: ValidateRequest):
    """
    Validate code for safety without executing.
    
    Checks for:
    - Forbidden imports (os, sys, subprocess, etc.)
    - Dangerous operations (exec, eval, open, etc.)
    - Network access attempts
    - File system access attempts
    """
    global validator
    
    if not validator:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = validator.validate(request.code)
        return ValidateResponse(
            safe=result["safe"],
            issues=result["issues"],
            blocked_imports=result.get("blocked_imports", []),
            blocked_operations=result.get("blocked_operations", []),
        )
    except Exception as e:
        logger.exception("validation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/allowed-imports")
async def get_allowed_imports():
    """Get list of allowed imports in the sandbox."""
    return {
        "allowed_imports": settings.sandbox_allowed_imports_list,
        "description": "Only these standard library modules can be imported",
    }


@app.get("/limits")
async def get_limits():
    """Get sandbox resource limits."""
    return {
        "timeout_seconds": settings.sandbox_timeout_seconds,
        "memory_limit_mb": settings.sandbox_memory_limit_mb,
        "max_code_length": 50000,
        "network_access": False,
        "filesystem_access": "temp only",
    }


async def _publish_execution_event(
    user_id: str,
    success: bool,
    execution_time_ms: int,
) -> None:
    """Publish code execution event."""
    try:
        dapr = get_dapr_client()
        await dapr.publish_event(
            topic=settings.kafka_topic_code,
            data={
                "event_type": "code_executed",
                "user_id": user_id,
                "success": success,
                "execution_time_ms": execution_time_ms,
            },
        )
    except Exception as e:
        logger.warning("failed_to_publish_event", error=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=8007, reload=settings.debug)
