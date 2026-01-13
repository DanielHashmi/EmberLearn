"""
Pydantic Models and Schemas

Shared data models used across all AI agent microservices.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ==================== Enums ====================

class MasteryLevel(str, Enum):
    """Student mastery level for a topic."""
    BEGINNER = "beginner"      # 0-40%
    LEARNING = "learning"      # 41-70%
    PROFICIENT = "proficient"  # 71-90%
    MASTERED = "mastered"      # 91-100%
    
    @classmethod
    def from_score(cls, score: float) -> "MasteryLevel":
        """Get mastery level from percentage score."""
        if score <= 40:
            return cls.BEGINNER
        elif score <= 70:
            return cls.LEARNING
        elif score <= 90:
            return cls.PROFICIENT
        return cls.MASTERED


class AgentType(str, Enum):
    """Types of AI agents in the system."""
    TRIAGE = "triage"
    CONCEPTS = "concepts"
    CODE_REVIEW = "code_review"
    DEBUG = "debug"
    EXERCISE = "exercise"
    PROGRESS = "progress"


class Difficulty(str, Enum):
    """Exercise difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MessageRole(str, Enum):
    """Chat message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ==================== Base Models ====================

class BaseResponse(BaseModel):
    """Base response model with common fields."""
    success: bool = True
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ==================== Chat Models ====================

class ChatMessage(BaseModel):
    """A single chat message."""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_type: Optional[AgentType] = None
    metadata: Optional[dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Request to chat with an AI agent."""
    message: str = Field(..., min_length=1, max_length=10000)
    user_id: str
    session_id: Optional[str] = None
    context: Optional[dict[str, Any]] = None
    history: list[ChatMessage] = Field(default_factory=list)
    target_agent: Optional[AgentType] = None


class ChatResponse(BaseResponse):
    """Response from an AI agent chat."""
    response: str
    agent_type: AgentType
    session_id: str
    suggestions: list[str] = Field(default_factory=list)
    related_topics: list[str] = Field(default_factory=list)
    code_examples: list[str] = Field(default_factory=list)


# ==================== Code Execution Models ====================

class CodeExecutionRequest(BaseModel):
    """Request to execute Python code in sandbox."""
    code: str = Field(..., min_length=1, max_length=50000)
    user_id: str
    exercise_id: Optional[str] = None
    test_cases: list[dict[str, Any]] = Field(default_factory=list)
    timeout_seconds: int = Field(default=5, ge=1, le=30)


class TestCaseResult(BaseModel):
    """Result of a single test case execution."""
    name: str
    passed: bool
    input: str
    expected_output: str
    actual_output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None


class CodeExecutionResponse(BaseResponse):
    """Response from code execution."""
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: int
    memory_used_mb: Optional[float] = None
    test_results: list[TestCaseResult] = Field(default_factory=list)
    passed_count: int = 0
    total_count: int = 0
    score: Optional[float] = None


# ==================== Exercise Models ====================

class TestCase(BaseModel):
    """A test case for an exercise."""
    id: str
    name: str
    input: str
    expected_output: str
    hidden: bool = False


class ExerciseRequest(BaseModel):
    """Request to generate or get an exercise."""
    topic: str
    difficulty: Difficulty = Difficulty.MEDIUM
    user_id: str
    mastery_score: Optional[float] = None
    previous_exercises: list[str] = Field(default_factory=list)


class Exercise(BaseModel):
    """An exercise/challenge."""
    id: str
    title: str
    description: str
    instructions: str
    starter_code: str
    topic: str
    difficulty: Difficulty
    estimated_time_minutes: int
    hints: list[str] = Field(default_factory=list)
    test_cases: list[TestCase] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExerciseResponse(BaseResponse):
    """Response containing an exercise."""
    exercise: Exercise


class ExerciseSubmission(BaseModel):
    """A student's submission for an exercise."""
    id: str
    user_id: str
    exercise_id: str
    code: str
    score: float
    passed: bool
    test_results: list[TestCaseResult]
    feedback: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


# ==================== Progress Models ====================

class TopicProgress(BaseModel):
    """Progress for a single topic."""
    topic_id: str
    topic_name: str
    mastery_score: float = Field(ge=0, le=100)
    mastery_level: MasteryLevel
    exercises_completed: int = 0
    exercises_total: int = 0
    quiz_average: Optional[float] = None
    code_quality_average: Optional[float] = None
    last_activity: Optional[datetime] = None


class ProgressData(BaseModel):
    """Complete progress data for a student."""
    user_id: str
    overall_mastery: float = Field(ge=0, le=100)
    overall_level: MasteryLevel
    streak_days: int = 0
    total_xp: int = 0
    level: int = 1
    topics: list[TopicProgress] = Field(default_factory=list)
    recent_exercises: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProgressUpdateRequest(BaseModel):
    """Request to update student progress."""
    user_id: str
    topic_id: str
    exercise_score: Optional[float] = None
    quiz_score: Optional[float] = None
    code_quality_score: Optional[float] = None


# ==================== Struggle Detection Models ====================

class StruggleTrigger(str, Enum):
    """Types of struggle triggers."""
    REPEATED_ERROR = "repeated_error"        # Same error 3+ times
    STUCK_TOO_LONG = "stuck_too_long"        # >10 min on exercise
    LOW_QUIZ_SCORE = "low_quiz_score"        # <50% quiz score
    EXPLICIT_STATEMENT = "explicit_statement" # "I don't understand"
    FAILED_EXECUTIONS = "failed_executions"  # 5+ failed runs


class StruggleAlert(BaseModel):
    """Alert when a student is struggling."""
    id: str
    user_id: str
    trigger: StruggleTrigger
    topic: str
    exercise_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    severity: int = Field(ge=1, le=5, default=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


# ==================== Event Models ====================

class LearningEvent(BaseModel):
    """Event published when learning activity occurs."""
    event_type: str
    user_id: str
    topic: Optional[str] = None
    exercise_id: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CodeEvent(BaseModel):
    """Event published when code is executed."""
    user_id: str
    exercise_id: Optional[str] = None
    success: bool
    error_type: Optional[str] = None
    execution_time_ms: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
