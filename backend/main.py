"""
EmberLearn Backend - Main FastAPI Application
Production-grade Python tutoring platform with AI agents
"""

import os
from contextlib import asynccontextmanager
from datetime import timedelta

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from app.config import settings
from app.database import init_db, get_db
from app.auth import AuthService, create_access_token, verify_token
from app.schemas import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
    QueryRequest, TriageResponse, ChatResponse
)
from app.agents import (
    triage_agent, concepts_agent, code_review_agent,
    debug_agent, exercise_agent, progress_agent
)

# Configure logging
logger = structlog.get_logger()

# Security
security = HTTPBearer()
auth_service = AuthService()


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting EmberLearn API")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down EmberLearn API")


# Initialize FastAPI
app = FastAPI(
    title="EmberLearn Backend",
    description="AI-powered Python tutoring platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health & Status Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "service": "emberlearn-api",
        "version": "0.1.0"
    }


@app.get("/api/status")
async def status():
    """Get API status"""
    return {
        "status": "running",
        "agents": {
            "triage": "ready",
            "concepts": "ready",
            "code_review": "ready",
            "debug": "ready",
            "exercise": "ready",
            "progress": "ready",
        },
        "auth": "enabled",
    }


# ============================================================================
# Authentication Endpoints
# ============================================================================

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db=Depends(get_db)):
    """Register new user"""
    try:
        user = await auth_service.register_user(
            db=db,
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )

        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=timedelta(hours=24)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("registration_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, db=Depends(get_db)):
    """Login user"""
    try:
        user = await auth_service.authenticate_user(
            db=db,
            email=request.email,
            password=request.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.id, "email": user.email},
            expires_delta=timedelta(hours=24)
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("login_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
):
    """Get current user info"""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = await auth_service.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("token_verification_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============================================================================
# Agent Endpoints
# ============================================================================

@app.post("/api/triage", response_model=TriageResponse)
async def triage(request: QueryRequest):
    """Route query to appropriate agent"""
    try:
        result = await triage_agent(request.query, request.student_id)
        return result
    except Exception as e:
        logger.error("triage_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Triage failed"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: QueryRequest):
    """Chat endpoint - routes through triage to appropriate agent"""
    try:
        # Get triage routing
        triage_result = await triage_agent(request.query, request.student_id)

        # Route to appropriate agent
        agent_map = {
            "concepts": concepts_agent,
            "code_review": code_review_agent,
            "debug": debug_agent,
            "exercise": exercise_agent,
            "progress": progress_agent,
        }

        agent_fn = agent_map.get(triage_result.agent, concepts_agent)
        agent_response = await agent_fn(request.query, request.student_id)

        return ChatResponse(
            routed_to=triage_result.agent,
            explanation=triage_result.explanation,
            response=agent_response.get("response", ""),
            metadata=agent_response
        )
    except Exception as e:
        logger.error("chat_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat failed"
        )


@app.post("/api/concepts")
async def concepts(request: QueryRequest):
    """Explain Python concepts"""
    try:
        result = await concepts_agent(request.query, request.student_id)
        return result
    except Exception as e:
        logger.error("concepts_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/code_review")
async def code_review(request: QueryRequest):
    """Review Python code"""
    try:
        result = await code_review_agent(request.query, request.student_id)
        return result
    except Exception as e:
        logger.error("code_review_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/debug")
async def debug(request: QueryRequest):
    """Debug Python errors"""
    try:
        result = await debug_agent(request.query, request.student_id)
        return result
    except Exception as e:
        logger.error("debug_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/exercise")
async def exercise(request: QueryRequest):
    """Generate coding exercises"""
    try:
        result = await exercise_agent(request.query, request.student_id)
        return result
    except Exception as e:
        logger.error("exercise_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/progress")
async def progress(request: QueryRequest):
    """Track learning progress"""
    try:
        result = await progress_agent(request.query, request.student_id)
        return result
    except Exception as e:
        logger.error("progress_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting EmberLearn API on http://localhost:{port}")
    print(f"Docs: http://localhost:{port}/docs")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
