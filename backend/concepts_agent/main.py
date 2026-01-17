"""
Concepts Agent - FastAPI Service

Explains Python concepts with adaptive examples based on student mastery level.
Provides clear explanations, code examples, and related topic suggestions.
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import setup_logging, get_logger
from shared.correlation import CorrelationMiddleware
from shared.models import ChatRequest, ChatResponse, AgentType, ErrorResponse
from shared.dapr_client import get_dapr_client

from .agent import ConceptsAgent

# Setup logging
setup_logging(service_name="concepts-agent")
logger = get_logger(__name__)

# Initialize agent
concepts_agent: Optional[ConceptsAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global concepts_agent
    
    logger.info("Starting Concepts Agent service...")
    
    # Initialize agent
    concepts_agent = ConceptsAgent()
    
    logger.info("Concepts Agent service started successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Concepts Agent service...")
    dapr = get_dapr_client()
    await dapr.close()
    logger.info("Concepts Agent service stopped")


# Create FastAPI app
app = FastAPI(
    title="EmberLearn Concepts Agent",
    description="Explains Python concepts with adaptive examples",
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
    return {"status": "healthy", "service": "concepts-agent"}


@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint."""
    dapr = get_dapr_client()
    dapr_healthy = await dapr.health_check()
    
    if not dapr_healthy:
        raise HTTPException(status_code=503, detail="Dapr sidecar not ready")
    
    return {"status": "ready", "service": "concepts-agent"}


# ==================== Chat Endpoints ====================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Explain a Python concept.
    
    Adapts explanation complexity based on student's mastery level.
    Includes code examples and related topic suggestions.
    """
    global concepts_agent
    
    if not concepts_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "processing_concept_request",
            user_id=request.user_id,
            message_length=len(request.message),
        )
        
        response = await concepts_agent.explain(request)
        
        logger.info(
            "concept_explained",
            user_id=request.user_id,
            topic=response.related_topics[0] if response.related_topics else None,
        )
        
        return response
        
    except Exception as e:
        logger.exception("concept_explanation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain-topic")
async def explain_topic(topic: str, mastery_level: str = "beginner"):
    """
    Get a structured explanation of a specific topic.
    
    Args:
        topic: Python topic to explain (e.g., "for loops", "list comprehension")
        mastery_level: Student's level (beginner, learning, proficient, mastered)
    """
    global concepts_agent
    
    if not concepts_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        explanation = await concepts_agent.explain_topic(topic, mastery_level)
        return explanation
        
    except Exception as e:
        logger.exception("topic_explanation_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/topics")
async def list_topics():
    """Get list of available Python topics."""
    return {
        "topics": [
            {"slug": "basics", "name": "Basics", "subtopics": ["variables", "data-types", "input-output", "operators"]},
            {"slug": "control-flow", "name": "Control Flow", "subtopics": ["if-else", "for-loops", "while-loops", "break-continue"]},
            {"slug": "data-structures", "name": "Data Structures", "subtopics": ["lists", "tuples", "dictionaries", "sets"]},
            {"slug": "functions", "name": "Functions", "subtopics": ["defining-functions", "parameters", "return-values", "scope"]},
            {"slug": "oop", "name": "OOP", "subtopics": ["classes", "objects", "inheritance", "encapsulation"]},
            {"slug": "files", "name": "Files", "subtopics": ["reading-files", "writing-files", "csv", "json"]},
            {"slug": "errors", "name": "Errors", "subtopics": ["try-except", "exception-types", "custom-exceptions", "debugging"]},
            {"slug": "libraries", "name": "Libraries", "subtopics": ["pip", "virtual-environments", "apis", "popular-packages"]},
        ]
    }


# ==================== Dapr Subscription ====================

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
    """Handle learning events."""
    logger.info("received_learning_event", event_type=event.get("type"))
    return {"status": "SUCCESS"}


# ==================== Run Server ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=8002,
        reload=settings.debug,
    )
