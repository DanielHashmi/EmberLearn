"""Code execution API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
from datetime import datetime

from database.config import get_db
from services.sandbox import SandboxService, ExecutionResult
from routers.auth import get_current_user, get_optional_current_user

router = APIRouter(prefix="/api/execute", tags=["execute"])


# Request/Response models
class ExecuteCodeRequest(BaseModel):
    """Request to execute Python code."""
    code: str


class ExecuteCodeResponse(BaseModel):
    """Response from code execution."""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time_ms: int = 0


# Endpoints
@router.post("", response_model=ExecuteCodeResponse)
async def execute_code(
    request: ExecuteCodeRequest,
    current_user=Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Execute Python code in a sandboxed environment.
    
    Constraints:
    - 5-second timeout
    - 50MB memory limit
    - Standard library only
    - No file/network access
    """
    # Validate code for dangerous patterns
    is_valid, error_msg = SandboxService.validate_code(request.code)
    if not is_valid:
        return ExecuteCodeResponse(
            success=False,
            output="",
            error=f"Code validation failed: {error_msg}",
            execution_time_ms=0
        )
    
    # Execute the code
    result = SandboxService.execute(request.code)
    
    # Log execution attempt (optional - could store in DB)
    # For now, just return the result
    
    return ExecuteCodeResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        execution_time_ms=result.execution_time_ms
    )


@router.post("/validate", response_model=dict)
async def validate_code(
    request: ExecuteCodeRequest,
    current_user=Depends(get_optional_current_user),
):
    """
    Validate Python code without executing it.
    
    Checks for dangerous patterns and syntax errors.
    """
    # Check for dangerous patterns
    is_valid, error_msg = SandboxService.validate_code(request.code)
    
    if not is_valid:
        return {
            "valid": False,
            "error": error_msg
        }
    
    # Check for syntax errors
    try:
        compile(request.code, '<string>', 'exec')
        return {
            "valid": True,
            "error": None
        }
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax error at line {e.lineno}: {e.msg}"
        }
