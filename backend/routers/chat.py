"""Chat API endpoints for AI conversation with history."""

import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_db
from models.chat import ChatMessage
from routers.auth import get_current_user
from agents.triage import TriageAgent
from agents.concepts import ConceptsAgent
from agents.code_review import CodeReviewAgent
from agents.debug import DebugAgent
from agents.exercise import ExerciseAgent

router = APIRouter(prefix="/api/chat", tags=["chat"])


# Request/Response models
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    id: str
    message: str
    response: str
    agent_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatHistoryResponse(BaseModel):
    messages: list[ChatResponse]
    total: int
    page: int
    page_size: int


# Agent dispatcher
AGENTS = {
    "concepts": ConceptsAgent,
    "code_review": CodeReviewAgent,
    "debug": DebugAgent,
    "exercise": ExerciseAgent,
}


async def get_recent_history(
    db: AsyncSession, user_id: uuid.UUID, limit: int = 5
) -> list[dict]:
    """Get recent chat history for context."""
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == user_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(limit)
    )
    messages = result.scalars().all()
    
    # Return in chronological order (oldest first)
    return [
        {"message": m.message, "response": m.response}
        for m in reversed(messages)
    ]


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a message and get AI response."""
    if not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )
    
    # Route to appropriate agent
    agent_type = TriageAgent.route(request.message)
    agent_class = AGENTS.get(agent_type, ConceptsAgent)
    
    # Get recent history for context
    history = await get_recent_history(db, current_user.id)
    
    # Get AI response
    try:
        response = await agent_class.respond(request.message, history)
    except Exception as e:
        # Log error but return user-friendly message
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)[:100]}",
        )
    
    # Store in database
    chat_message = ChatMessage(
        user_id=current_user.id,
        message=request.message,
        response=response,
        agent_type=agent_type,
    )
    db.add(chat_message)
    await db.commit()
    await db.refresh(chat_message)
    
    return ChatResponse(
        id=str(chat_message.id),
        message=chat_message.message,
        response=chat_message.response,
        agent_type=chat_message.agent_type,
        created_at=chat_message.created_at,
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get user's chat history with pagination."""
    # Get total count
    count_result = await db.execute(
        select(ChatMessage.id).where(ChatMessage.user_id == current_user.id)
    )
    total = len(count_result.all())
    
    # Get paginated messages
    offset = (page - 1) * page_size
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.user_id == current_user.id)
        .order_by(desc(ChatMessage.created_at))
        .offset(offset)
        .limit(page_size)
    )
    messages = result.scalars().all()
    
    return ChatHistoryResponse(
        messages=[
            ChatResponse(
                id=str(m.id),
                message=m.message,
                response=m.response,
                agent_type=m.agent_type,
                created_at=m.created_at,
            )
            for m in messages
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/history")
async def clear_chat_history(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear user's chat history."""
    result = await db.execute(
        select(ChatMessage).where(ChatMessage.user_id == current_user.id)
    )
    messages = result.scalars().all()
    
    for message in messages:
        await db.delete(message)
    
    await db.commit()
    
    return {"message": "Chat history cleared", "deleted_count": len(messages)}
