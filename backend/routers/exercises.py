"""Exercise API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from database.config import get_db
from models.exercise import Exercise, ExerciseAttempt
from services.sandbox import SandboxService
from services.progress import ProgressService, XP_PER_EXERCISE
from routers.auth import get_current_user, get_optional_current_user

router = APIRouter(prefix="/api/exercises", tags=["exercises"])


# Response models
class ExerciseResponse(BaseModel):
    """Exercise details response."""
    id: str
    title: str
    description: str
    difficulty: str
    topic_slug: str
    topic_name: str
    starter_code: str
    estimated_time: int
    completed: bool = False
    best_score: int = 0

    class Config:
        from_attributes = True


class ExerciseDetailResponse(ExerciseResponse):
    """Detailed exercise response with solution (for completed exercises)."""
    solution: Optional[str] = None
    test_cases: List[dict] = []


class SubmitCodeRequest(BaseModel):
    """Request to submit code for an exercise."""
    code: str


class TestCaseResultResponse(BaseModel):
    """Result of a single test case."""
    input_data: str
    expected: str
    actual: str
    passed: bool


class SubmitCodeResponse(BaseModel):
    """Response from code submission."""
    success: bool
    score: int
    passed: bool
    output: str
    error: Optional[str] = None
    xp_earned: int = 0
    test_results: List[TestCaseResultResponse] = []


class ExerciseListResponse(BaseModel):
    """List of exercises grouped by topic."""
    topic_slug: str
    topic_name: str
    exercises: List[ExerciseResponse]


# Endpoints
@router.get("", response_model=List[ExerciseResponse])
async def list_exercises(
    topic: Optional[str] = None,
    current_user=Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all exercises with user completion status.
    
    Optionally filter by topic slug.
    Authentication is optional - if not logged in, all exercises show as incomplete.
    """
    # Build query
    query = select(Exercise)
    if topic:
        query = query.where(Exercise.topic_slug == topic)
    query = query.order_by(Exercise.topic_slug, Exercise.difficulty)
    
    result = await db.execute(query)
    exercises = result.scalars().all()
    
    # Get user's attempts to determine completion status (only if logged in)
    attempts = []
    if current_user:
        attempts_query = select(ExerciseAttempt).where(
            ExerciseAttempt.user_id == current_user.id
        )
        attempts_result = await db.execute(attempts_query)
        attempts = attempts_result.scalars().all()
    
    # Create lookup for best scores
    best_scores = {}
    completed = set()
    for attempt in attempts:
        ex_id = str(attempt.exercise_id)
        if ex_id not in best_scores or attempt.score > best_scores[ex_id]:
            best_scores[ex_id] = attempt.score
        if attempt.passed:
            completed.add(ex_id)
    
    # Build response
    response = []
    for ex in exercises:
        ex_id = str(ex.id)
        response.append(ExerciseResponse(
            id=ex_id,
            title=ex.title,
            description=ex.description,
            difficulty=ex.difficulty,
            topic_slug=ex.topic_slug,
            topic_name=ex.topic_name,
            starter_code=ex.starter_code,
            estimated_time=ex.estimated_time,
            completed=ex_id in completed,
            best_score=best_scores.get(ex_id, 0)
        ))
    
    return response


@router.get("/by-topic", response_model=List[ExerciseListResponse])
async def list_exercises_by_topic(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all exercises grouped by topic.
    """
    exercises = await list_exercises(None, current_user, db)
    
    # Group by topic
    topics = {}
    for ex in exercises:
        if ex.topic_slug not in topics:
            topics[ex.topic_slug] = {
                "topic_slug": ex.topic_slug,
                "topic_name": ex.topic_name,
                "exercises": []
            }
        topics[ex.topic_slug]["exercises"].append(ex)
    
    return [ExerciseListResponse(**t) for t in topics.values()]


@router.get("/{exercise_id}", response_model=ExerciseDetailResponse)
async def get_exercise(
    exercise_id: str,
    current_user=Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get exercise details by ID.

    Authentication is optional. Solution is only returned if user has completed the exercise.
    """
    try:
        ex_uuid = uuid.UUID(exercise_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exercise ID format"
        )
    
    # Get exercise
    result = await db.execute(
        select(Exercise).where(Exercise.id == ex_uuid)
    )
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    # Check if user has completed this exercise (only if logged in)
    attempts = []
    if current_user:
        attempts_result = await db.execute(
            select(ExerciseAttempt).where(
                and_(
                    ExerciseAttempt.user_id == current_user.id,
                    ExerciseAttempt.exercise_id == ex_uuid
                )
            )
        )
        attempts = attempts_result.scalars().all()

    completed = any(a.passed for a in attempts)
    best_score = max((a.score for a in attempts), default=0)
    
    return ExerciseDetailResponse(
        id=str(exercise.id),
        title=exercise.title,
        description=exercise.description,
        difficulty=exercise.difficulty,
        topic_slug=exercise.topic_slug,
        topic_name=exercise.topic_name,
        starter_code=exercise.starter_code,
        estimated_time=exercise.estimated_time,
        completed=completed,
        best_score=best_score,
        solution=exercise.solution if completed else None,
        test_cases=exercise.test_cases if completed else []
    )


@router.post("/{exercise_id}/submit", response_model=SubmitCodeResponse)
async def submit_exercise(
    exercise_id: str,
    request: SubmitCodeRequest,
    current_user=Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit code for an exercise.
    
    Runs test cases. If authenticated, updates user progress.
    """
    try:
        ex_uuid = uuid.UUID(exercise_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid exercise ID format"
        )
    
    # Get exercise
    result = await db.execute(
        select(Exercise).where(Exercise.id == ex_uuid)
    )
    exercise = result.scalar_one_or_none()
    
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exercise not found"
        )
    
    # Validate code
    is_valid, error_msg = SandboxService.validate_code(request.code)
    if not is_valid:
        return SubmitCodeResponse(
            success=False,
            score=0,
            passed=False,
            output="",
            error=f"Code validation failed: {error_msg}",
            xp_earned=0,
            test_results=[]
        )
    
    # Run test cases
    test_result = SandboxService.run_tests(request.code, exercise.test_cases)
    
    # Calculate score
    score = test_result.score
    passed = score == 100
    
    xp_earned = 0
    
    # Only save progress if user is logged in
    if current_user:
        # Create attempt record
        attempt = ExerciseAttempt(
            user_id=current_user.id,
            exercise_id=ex_uuid,
            code=request.code,
            score=score,
            passed=passed,
            output=str(test_result.results),
            error=None
        )
        db.add(attempt)
        
        # Update progress if passed
        if passed:
            # Check if this is first time passing
            prev_attempts = await db.execute(
                select(ExerciseAttempt).where(
                    and_(
                        ExerciseAttempt.user_id == current_user.id,
                        ExerciseAttempt.exercise_id == ex_uuid,
                        ExerciseAttempt.passed == True
                    )
                )
            )
            first_pass = prev_attempts.scalar_one_or_none() is None
            
            if first_pass:
                # Update mastery and award XP
                await ProgressService.update_mastery(
                    db, current_user.id, exercise.topic_slug, exercise_completed=True
                )
                total_xp = await ProgressService.add_xp(db, current_user.id, XP_PER_EXERCISE)
                xp_earned = XP_PER_EXERCISE
                
                # Update streak
                await ProgressService.update_streak(db, current_user.id)
        
        await db.commit()
    
    # Build test results response
    test_results = [
        TestCaseResultResponse(
            input_data=r.input_data,
            expected=r.expected,
            actual=r.actual,
            passed=r.passed
        )
        for r in test_result.results
    ]
    
    return SubmitCodeResponse(
        success=True,
        score=score,
        passed=passed,
        output=f"Passed {test_result.passed}/{test_result.total} test cases",
        error=None,
        xp_earned=xp_earned,
        test_results=test_results
    )
