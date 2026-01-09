"""Pydantic schemas for request/response validation"""

from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ============================================================================
# Auth Schemas
# ============================================================================

class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    """Registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str


class UserResponse(BaseModel):
    """User response (no password)"""
    id: str
    email: str
    full_name: str
    created_at: datetime
    mastery_score: float = 0.0

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============================================================================
# Agent Schemas
# ============================================================================

class QueryRequest(BaseModel):
    """Query request to agents"""
    query: str
    student_id: Optional[str] = "anonymous"
    context: Optional[Dict[str, Any]] = None


class TriageResponse(BaseModel):
    """Triage routing response"""
    agent: str = Field(..., description="Target agent: triage, concepts, code_review, debug, exercise, progress")
    explanation: str = Field(..., description="Why this agent was selected")
    response: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat endpoint response"""
    routed_to: str
    explanation: str
    response: str
    metadata: Optional[Dict[str, Any]] = None


class ConceptsResponse(BaseModel):
    """Concepts agent response"""
    response: str
    examples: Optional[list] = None
    concepts: Optional[list] = None


class CodeReviewResponse(BaseModel):
    """Code review agent response"""
    response: str
    suggestions: Optional[list] = None
    issues: Optional[list] = None


class DebugResponse(BaseModel):
    """Debug agent response"""
    response: str
    hints: Optional[list] = None
    root_cause: Optional[str] = None


class ExerciseResponse(BaseModel):
    """Exercise agent response"""
    response: str
    difficulty: Optional[str] = None
    test_cases: Optional[list] = None


class ProgressResponse(BaseModel):
    """Progress agent response"""
    response: str
    mastery_score: float = 0.0
    completed_exercises: int = 0
    streak_days: int = 0
