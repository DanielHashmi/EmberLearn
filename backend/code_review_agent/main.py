"""
Code Review Agent - FastAPI Service

Analyzes Python code for:
- PEP 8 style compliance
- Code efficiency and best practices
- Readability and maintainability
- Specific improvement suggestions
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
from shared.models import ChatRequest, ChatResponse, AgentType
from shared.dapr_client import get_dapr_client

from .agent import CodeReviewAgent

# Setup logging
setup_logging(service_name="code-review-agent")
logger = get_logger(__name__)

# Initialize agent
code_review_agent: Optional[CodeReviewAgent] = None


class CodeReviewRequest(BaseModel):
    """Request for code review."""
    code: str = Field(..., min_length=1, max_length=50000)
    user_id: str
    context: Optional[str] = None  # What the code is supposed to do
    focus_areas: list[str] = Field(default_factory=list)  # style, efficiency, readability


class CodeReviewResponse(BaseModel):
    """Response from code review."""
    success: bool = True
    overall_score: float = Field(ge=0, le=100)
    summary: str
    style_score: float = Field(ge=0, le=100)
    efficiency_score: float = Field(ge=0, le=100)
    readability_score: float = Field(ge=0, le=100)
    issues: list[dict]
    suggestions: list[str]
    improved_code: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global code_review_agent
    
    logger.info("Starting Code Review Agent service...")
    code_review_agent = CodeReviewAgent()
    logger.info("Code Review Agent service started successfully")
    
    yield
    
    logger.info("Shutting down Code Review Agent service...")
    dapr = get_dapr_client()
    await dapr.close()
    logger.info("Code Review Agent service stopped")


app = FastAPI(
    title="EmberLearn Code Review Agent",
    description="Analyzes Python code for style, efficiency, and best practices",
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
    return {"status": "healthy", "service": "code-review-agent"}


@app.get("/ready")
async def readiness_check():
    dapr = get_dapr_client()
    if not await dapr.health_check():
        raise HTTPException(status_code=503, detail="Dapr sidecar not ready")
    return {"status": "ready", "service": "code-review-agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Review code from a chat message.
    
    Extracts code from the message and provides feedback.
    """
    global code_review_agent
    
    if not code_review_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info("processing_chat_review", user_id=request.user_id)
        response = await code_review_agent.review_from_chat(request)
        return response
        
    except Exception as e:
        logger.exception("chat_review_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
    """
    Perform detailed code review.
    
    Returns scores and specific suggestions for improvement.
    """
    global code_review_agent
    
    if not code_review_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "processing_code_review",
            user_id=request.user_id,
            code_length=len(request.code),
        )
        
        review = await code_review_agent.review(
            code=request.code,
            user_id=request.user_id,
            context=request.context,
            focus_areas=request.focus_areas,
        )
        
        logger.info(
            "code_review_complete",
            user_id=request.user_id,
            overall_score=review.overall_score,
        )
        
        return review
        
    except Exception as e:
        logger.exception("code_review_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quick-check")
async def quick_check(code: str):
    """
    Quick syntax and style check without detailed analysis.
    """
    global code_review_agent
    
    if not code_review_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        result = await code_review_agent.quick_check(code)
        return result
        
    except Exception as e:
        logger.exception("quick_check_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dapr/subscribe")
async def dapr_subscribe():
    return [
        {
            "pubsubname": settings.dapr_pubsub_name,
            "topic": settings.kafka_topic_code,
            "route": "/events/code",
        }
    ]


@app.post("/events/code")
async def handle_code_event(event: dict):
    logger.info("received_code_event", event_type=event.get("type"))
    return {"status": "SUCCESS"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=8003, reload=settings.debug)
