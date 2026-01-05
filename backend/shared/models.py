"""
Pydantic base schemas for API request/response models.

Per contracts/agent-api.yaml specification.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# Enums
class MasteryLevel(str, Enum):
    """Mastery level classification per FR-020."""
    BEGINNER = "beginner"      # 0-40%
    LEARNING = "learning"      # 41-70%
    PROFICIENT = "proficient"  # 71-90%
    MASTERED = "mastered"      # 91-100%


class UserRole(str, Enum):
    """User roles for authorization."""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class IssueCategory(str, Enum):
    """Code review issue categories."""
    CORRECTNESS = "correctness"
    STYLE = "style"
    EFFICIENCY = "efficiency"


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Base Models
class BaseRequest(BaseModel):
    """Base request with correlation tracking."""
    correlation_id: str | None = Field(None, description="Request correlation ID")


class BaseResponse(BaseModel):
    """Base response with metadata."""
    correlation_id: str = Field(..., description="Response correlation ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Triage Agent Models
class QueryRequest(BaseRequest):
    """Request to triage agent for query routing."""
    student_id: int = Field(..., description="Student identifier")
    query: str = Field(..., min_length=1, max_length=2000, description="Student query")
    topic_id: int | None = Field(None, description="Optional topic context")


class QueryResponse(BaseResponse):
    """Response from triage agent."""
    response: str = Field(..., description="Agent response text")
    agent_used: str = Field(..., description="Specialist agent that handled query")
    confidence: float = Field(..., ge=0, le=1, description="Response confidence score")


# Concepts Agent Models
class ConceptExplainRequest(BaseRequest):
    """Request to explain a Python concept."""
    student_id: int
    concept: str = Field(..., min_length=1, max_length=500)
    student_level: MasteryLevel = Field(default=MasteryLevel.BEGINNER)


class ConceptExplainResponse(BaseResponse):
    """Concept explanation response."""
    explanation: str
    examples: list[str] = Field(default_factory=list)
    related_concepts: list[str] = Field(default_factory=list)


# Code Review Agent Models
class CodeReviewRequest(BaseRequest):
    """Request to analyze code quality."""
    student_id: int
    code: str = Field(..., min_length=1, max_length=10000)
    topic_id: int | None = None


class CodeIssue(BaseModel):
    """Individual code issue found during review."""
    line: int
    category: IssueCategory
    message: str
    suggestion: str | None = None


class CodeReviewResponse(BaseResponse):
    """Code review analysis response."""
    rating: int = Field(..., ge=0, le=100, description="Overall code quality rating")
    issues: list[CodeIssue] = Field(default_factory=list)
    summary: str
    strengths: list[str] = Field(default_factory=list)


# Debug Agent Models
class ErrorAnalysisRequest(BaseRequest):
    """Request to analyze an error."""
    student_id: int
    error_message: str = Field(..., min_length=1, max_length=5000)
    code: str = Field(..., min_length=1, max_length=10000)
    topic_id: int | None = None


class ErrorAnalysisResponse(BaseResponse):
    """Error analysis response."""
    error_type: str
    root_cause: str
    hints: list[str] = Field(default_factory=list)
    severity: ErrorSeverity
    similar_errors_count: int = Field(default=0, description="Count of similar errors by student")


# Exercise Agent Models
class ExerciseGenerateRequest(BaseRequest):
    """Request to generate a coding exercise."""
    student_id: int
    topic_id: int
    difficulty: MasteryLevel = Field(default=MasteryLevel.BEGINNER)


class TestCase(BaseModel):
    """Test case for exercise validation."""
    input: str
    expected_output: str
    is_hidden: bool = False


class ExerciseGenerateResponse(BaseResponse):
    """Generated exercise response."""
    exercise_id: UUID
    title: str
    description: str
    starter_code: str
    test_cases: list[TestCase]
    hints: list[str] = Field(default_factory=list)


class ExerciseSubmitRequest(BaseRequest):
    """Request to submit exercise solution."""
    student_id: int
    exercise_id: UUID
    code: str = Field(..., min_length=1, max_length=10000)


class ExerciseSubmitResponse(BaseResponse):
    """Exercise submission result."""
    passed: bool
    tests_passed: int
    tests_total: int
    execution_time_ms: int
    feedback: str
    code_review: CodeReviewResponse | None = None


# Progress Agent Models
class MasteryCalculateRequest(BaseRequest):
    """Request to calculate mastery score."""
    student_id: int
    topic_id: int


class MasteryScore(BaseModel):
    """Mastery score for a topic."""
    topic_id: int
    topic_name: str
    score: float = Field(..., ge=0, le=100)
    level: MasteryLevel
    exercises_completed: int
    quiz_average: float
    code_quality_average: float
    streak_days: int


class MasteryCalculateResponse(BaseResponse):
    """Mastery calculation response."""
    mastery: MasteryScore


class DashboardRequest(BaseRequest):
    """Request for student dashboard."""
    student_id: int


class DashboardResponse(BaseResponse):
    """Student dashboard with all topic mastery."""
    student_id: int
    overall_mastery: float
    topics: list[MasteryScore]
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)


# Sandbox Models
class CodeExecutionRequest(BaseRequest):
    """Request to execute Python code in sandbox."""
    code: str = Field(..., min_length=1, max_length=10000)
    timeout_seconds: int = Field(default=5, ge=1, le=5)
    memory_limit_mb: int = Field(default=50, ge=1, le=50)


class CodeExecutionResponse(BaseResponse):
    """Code execution result."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    execution_time_ms: int
    memory_used_mb: float | None = None
    error: str | None = None


# Health Check Models
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    service: str
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
