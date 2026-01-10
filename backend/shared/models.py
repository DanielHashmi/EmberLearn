"""
Pydantic models for API request/response validation.

Auto-generated from OpenAPI contract specifications.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    student_id: int  # Example: 42
    message: str  # Example: How do for loops work in Python?
    correlation_id: Optional[UUID] = None  # Optional correlation ID for distributed tracing

class QueryResponse(BaseModel):
    correlation_id: Optional[UUID] = None
    status: Optional[str] = None
    response: Optional[str] = None  # Example: A for loop in Python iterates over a sequence...
    agent_used: Optional[str] = None

class CodeExecutionRequest(BaseModel):
    student_id: int
    code: str  # Example: for i in range(10):
    print(i)

    correlation_id: Optional[UUID] = None

class CodeExecutionResponse(BaseModel):
    correlation_id: Optional[UUID] = None
    success: Optional[bool] = None
    stdout: Optional[str] = None  # Example: 0
1
2
3
4
5
6
7
8
9

    stderr: Optional[str] = None
    returncode: Optional[int] = None
    execution_time_ms: Optional[int] = None
    error: Optional[str] = None  # Error message if execution failed

class ExerciseGenerationRequest(BaseModel):
    topic_id: int  # Example: 2
    difficulty: str
    student_id: Optional[int] = None  # For personalization based on student history

class ExerciseResponse(BaseModel):
    exercise_id: Optional[int] = None
    uuid: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    starter_code: Optional[str] = None
    difficulty: Optional[str] = None
    test_cases: Optional[list[dict]] = None

class MasteryCalculationResponse(BaseModel):
    student_id: Optional[int] = None
    topic_id: Optional[int] = None
    mastery_score: Optional[float] = None  # Example: 75.5
    mastery_level: Optional[str] = None
    breakdown: Optional[dict] = None

class Error(BaseModel):
    error: Optional[str] = None
    detail: Optional[str] = None
    correlation_id: Optional[UUID] = None

