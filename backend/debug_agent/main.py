"""
Debug Agent - FastAPI Service

Helps students debug Python errors by:
- Parsing error messages and tracebacks
- Identifying root causes
- Providing hints before solutions (pedagogical approach)
- Explaining common error patterns
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

from .agent import DebugAgent

setup_logging(service_name="debug-agent")
logger = get_logger(__name__)

debug_agent: Optional[DebugAgent] = None


class DebugRequest(BaseModel):
    """Request for debugging help."""
    code: str = Field(..., min_length=1, max_length=50000)
    error_message: str = Field(..., min_length=1)
    user_id: str
    hint_level: int = Field(default=1, ge=1, le=3)  # 1=hint, 2=more detail, 3=solution


class DebugResponse(BaseModel):
    """Response with debugging help."""
    success: bool = True
    error_type: str
    error_explanation: str
    root_cause: str
    hint: str
    solution: Optional[str] = None  # Only if hint_level >= 3
    fixed_code: Optional[str] = None
    prevention_tips: list[str]
    related_errors: list[str]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global debug_agent
    logger.info("Starting Debug Agent service...")
    debug_agent = DebugAgent()
    logger.info("Debug Agent service started successfully")
    yield
    logger.info("Shutting down Debug Agent service...")
    dapr = get_dapr_client()
    await dapr.close()


app = FastAPI(
    title="EmberLearn Debug Agent",
    description="Helps debug Python errors with hints and explanations",
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
    return {"status": "healthy", "service": "debug-agent"}


@app.get("/ready")
async def readiness_check():
    dapr = get_dapr_client()
    if not await dapr.health_check():
        raise HTTPException(status_code=503, detail="Dapr sidecar not ready")
    return {"status": "ready", "service": "debug-agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Debug help from a chat message.
    
    Extracts code and error from the message and provides guidance.
    """
    global debug_agent
    
    if not debug_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info("processing_debug_chat", user_id=request.user_id)
        response = await debug_agent.debug_from_chat(request)
        return response
    except Exception as e:
        logger.exception("debug_chat_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug", response_model=DebugResponse)
async def debug_error(request: DebugRequest):
    """
    Debug a specific error with code context.
    
    Provides progressive hints based on hint_level.
    """
    global debug_agent
    
    if not debug_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        logger.info(
            "processing_debug_request",
            user_id=request.user_id,
            hint_level=request.hint_level,
        )
        
        result = await debug_agent.debug(
            code=request.code,
            error_message=request.error_message,
            user_id=request.user_id,
            hint_level=request.hint_level,
        )
        
        logger.info(
            "debug_complete",
            user_id=request.user_id,
            error_type=result.error_type,
        )
        
        return result
    except Exception as e:
        logger.exception("debug_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/parse-error")
async def parse_error(error_message: str):
    """
    Parse an error message to identify the error type.
    
    Quick analysis without full debugging context.
    """
    global debug_agent
    
    if not debug_agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    try:
        parsed = debug_agent.parse_error(error_message)
        return parsed
    except Exception as e:
        logger.exception("parse_error_failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/common-errors")
async def get_common_errors():
    """Get list of common Python errors with explanations."""
    return {
        "errors": [
            {
                "type": "SyntaxError",
                "description": "Invalid Python syntax",
                "common_causes": ["Missing colon", "Unmatched parentheses", "Invalid indentation"],
            },
            {
                "type": "NameError",
                "description": "Variable or function not defined",
                "common_causes": ["Typo in variable name", "Using before assignment", "Wrong scope"],
            },
            {
                "type": "TypeError",
                "description": "Operation on incompatible types",
                "common_causes": ["Adding string to int", "Calling non-callable", "Wrong argument count"],
            },
            {
                "type": "IndexError",
                "description": "List index out of range",
                "common_causes": ["Empty list access", "Off-by-one error", "Wrong loop bounds"],
            },
            {
                "type": "KeyError",
                "description": "Dictionary key not found",
                "common_causes": ["Typo in key", "Key not added yet", "Case sensitivity"],
            },
            {
                "type": "AttributeError",
                "description": "Object doesn't have attribute",
                "common_causes": ["Typo in method name", "Wrong object type", "None value"],
            },
            {
                "type": "IndentationError",
                "description": "Incorrect indentation",
                "common_causes": ["Mixed tabs/spaces", "Missing indent after colon", "Extra indent"],
            },
            {
                "type": "ValueError",
                "description": "Right type but wrong value",
                "common_causes": ["Invalid conversion", "Out of range", "Wrong format"],
            },
        ]
    }


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
    uvicorn.run("main:app", host=settings.host, port=8004, reload=settings.debug)
