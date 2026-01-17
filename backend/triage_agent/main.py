"""
Triage Agent - FastAPI Service

Routes incoming queries to the appropriate specialist agent:
- Concepts Agent: explanations, "what is", "how does"
- Code Review Agent: code analysis, "review my code"
- Debug Agent: errors, exceptions, "why doesn't this work"
- Exercise Agent: practice, challenges, "give me an exercise"
- Progress Agent: progress, mastery, "how am I doing"
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import setup_logging, get_logger
from shared.correlation import CorrelationMiddleware
from shared.models import ChatRequest, ChatResponse, AgentType, ErrorResponse
from shared.dapr_client import get_dapr_client

from .agent import TriageAgent

# Setup logging
setup_logging(service_name="triage-agent")
logger = get_logger(__name__)

# Initialize agent
triage_agent: Optional[TriageAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global triage_agent
    
    logger.info("Starting Triage Agent service...")
    
    # Initialize agent
    triage_agent = TriageAgent()
    
    logger.info("Triage Agent service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Triage Agent service...")
    dapr = get_dapr_client()
    await dapr.close()
    logger.info("Triage Agent service stopped")


# Create FastAPI app
app = FastAPI(
    title="EmberLearn Triage Agent",
    description="Routes queries to specialist AI agents",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(CorrelationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Health Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "triage-agent"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    # Check Dapr sidecar
    dapr = get_dapr_client()
    dapr_healthy = await dapr.health_check()
    
    if not dapr_healthy:
        raise HTTPException(status_code=503, detail="Dapr sidecar not ready")
    
    return {"status": "ready", "service": "triage-agent"}


# ==================== Chat Endpoints ====================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and route to appropriate agent.
    
    The triage agent analyzes the message and determines which
    specialist agent should handle it.
    """
    global triage_agent
    
    if not triage_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "processing_chat_request",
            user_id=request.user_id,
            message_length=len(request.message),
        )
        
        # Process with triage agent
        response = await triage_agent.process(request)
        
        logger.info(
            "chat_request_processed",
            user_id=request.user_id,
            routed_to=response.agent_type,
        )
        
        return response
        
    except Exception as e:
        logger.exception("chat_request_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/classify")
async def classify_query(request: ChatRequest):
    """
    Classify a query without routing to specialist.
    
    Returns the classification result showing which agent
    would handle this query.
    """
    global triage_agent
    
    if not triage_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        classification = await triage_agent.classify(request.message)
        
        return {
            "message": request.message,
            "classification": classification,
            "agent_type": classification["agent_type"],
            "confidence": classification["confidence"],
        }
        
    except Exception as e:
        logger.exception("classification_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Dapr Subscription Endpoints ====================

@app.post("/dapr/subscribe")
async def dapr_subscribe():
    """Dapr pubsub subscription configuration."""
    return [
        {
            "pubsubname": settings.dapr_pubsub_name,
            "topic": settings.kafka_topic_learning,
            "route": "/events/learning",
        }
    ]


@app.post("/events/learning")
async def handle_learning_event(event: dict):
    """Handle learning events from Kafka."""
    logger.info("received_learning_event", event_type=event.get("type"))
    
    # Process event (e.g., update context, trigger proactive help)
    # For now, just acknowledge
    return {"status": "SUCCESS"}


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
