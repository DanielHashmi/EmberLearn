"""
Triage Agent - Query Classification and Routing

Uses OpenAI to classify incoming queries and route them
to the appropriate specialist agent.
"""

import json
from typing import Optional
from uuid import uuid4

from openai import AsyncOpenAI

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import get_logger
from shared.models import (
    ChatRequest,
    ChatResponse,
    AgentType,
    ChatMessage,
    MessageRole,
)
from shared.dapr_client import get_dapr_client

logger = get_logger(__name__)

# Classification prompt
CLASSIFICATION_PROMPT = """You are a triage agent for EmberLearn, a Python tutoring platform.
Your job is to classify student queries and route them to the appropriate specialist agent.

Available agents:
1. CONCEPTS - Explains Python concepts, answers "what is", "how does", "explain" questions
2. CODE_REVIEW - Reviews code for style, efficiency, best practices
3. DEBUG - Helps with errors, exceptions, debugging "why doesn't this work"
4. EXERCISE - Generates practice exercises, challenges, quizzes
5. PROGRESS - Reports on student progress, mastery levels, achievements

Analyze the student's message and respond with a JSON object:
{
    "agent_type": "CONCEPTS" | "CODE_REVIEW" | "DEBUG" | "EXERCISE" | "PROGRESS",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of classification",
    "keywords": ["detected", "keywords"]
}

Rules:
- If the message contains code with an error/exception, route to DEBUG
- If the message asks to review/check code without errors, route to CODE_REVIEW
- If asking for practice/exercise/challenge, route to EXERCISE
- If asking about progress/mastery/how am I doing, route to PROGRESS
- Default to CONCEPTS for general Python questions
- Be confident (>0.8) when keywords clearly match an agent
"""

# Agent routing map
AGENT_ROUTES = {
    AgentType.CONCEPTS: "concepts-agent",
    AgentType.CODE_REVIEW: "code-review-agent",
    AgentType.DEBUG: "debug-agent",
    AgentType.EXERCISE: "exercise-agent",
    AgentType.PROGRESS: "progress-agent",
}


class TriageAgent:
    """
    Triage agent that classifies and routes queries.
    
    Uses OpenAI for intelligent classification and Dapr
    for service invocation to specialist agents.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dapr = get_dapr_client()
        self.model = settings.openai_model
    
    async def classify(self, message: str) -> dict:
        """
        Classify a message to determine the target agent.
        
        Args:
            message: The user's message
            
        Returns:
            Classification result with agent_type, confidence, reasoning
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CLASSIFICATION_PROMPT},
                    {"role": "user", "content": message},
                ],
                temperature=0.3,  # Lower temperature for consistent classification
                max_tokens=200,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Normalize agent type
            agent_type_str = result.get("agent_type", "CONCEPTS").upper()
            result["agent_type"] = AgentType(agent_type_str.lower())
            
            logger.debug(
                "query_classified",
                agent_type=result["agent_type"],
                confidence=result.get("confidence"),
            )
            
            return result
            
        except Exception as e:
            logger.error("classification_failed", error=str(e))
            # Default to concepts agent on error
            return {
                "agent_type": AgentType.CONCEPTS,
                "confidence": 0.5,
                "reasoning": "Classification failed, defaulting to concepts",
                "keywords": [],
            }
    
    async def route_to_agent(
        self,
        agent_type: AgentType,
        request: ChatRequest,
    ) -> ChatResponse:
        """
        Route request to the appropriate specialist agent.
        
        Args:
            agent_type: Target agent type
            request: Original chat request
            
        Returns:
            Response from the specialist agent
        """
        app_id = AGENT_ROUTES.get(agent_type, "concepts-agent")
        
        try:
            # Invoke specialist agent via Dapr
            response_data = await self.dapr.invoke_service(
                app_id=app_id,
                method="chat",
                data=request.model_dump(),
            )
            
            return ChatResponse(**response_data)
            
        except Exception as e:
            logger.error(
                "agent_invocation_failed",
                agent_type=agent_type,
                app_id=app_id,
                error=str(e),
            )
            
            # Return fallback response
            return ChatResponse(
                success=False,
                message=f"Failed to reach {agent_type} agent",
                response=self._get_fallback_response(agent_type, request.message),
                agent_type=AgentType.TRIAGE,
                session_id=request.session_id or str(uuid4()),
            )
    
    async def process(self, request: ChatRequest) -> ChatResponse:
        """
        Process a chat request: classify and route.
        
        Args:
            request: Chat request from user
            
        Returns:
            Response from the appropriate specialist agent
        """
        # Check if target agent is specified
        if request.target_agent:
            agent_type = request.target_agent
            classification = {
                "agent_type": agent_type,
                "confidence": 1.0,
                "reasoning": "Explicitly specified by user",
            }
        else:
            # Classify the query
            classification = await self.classify(request.message)
            agent_type = classification["agent_type"]
        
        # Publish routing event
        await self._publish_routing_event(request, classification)
        
        # Route to specialist agent
        response = await self.route_to_agent(agent_type, request)
        
        # Add triage metadata
        if not response.success:
            response.message = f"Routed to {agent_type.value} agent"
        
        return response
    
    async def _publish_routing_event(
        self,
        request: ChatRequest,
        classification: dict,
    ) -> None:
        """Publish routing event to Kafka for analytics."""
        try:
            event = {
                "event_type": "query_routed",
                "user_id": request.user_id,
                "session_id": request.session_id,
                "agent_type": classification["agent_type"].value,
                "confidence": classification.get("confidence", 0),
                "message_preview": request.message[:100],
            }
            
            await self.dapr.publish_event(
                topic=settings.kafka_topic_learning,
                data=event,
            )
            
        except Exception as e:
            # Don't fail the request if event publishing fails
            logger.warning("failed_to_publish_routing_event", error=str(e))
    
    def _get_fallback_response(self, agent_type: AgentType, message: str) -> str:
        """Get a fallback response when agent is unavailable."""
        fallbacks = {
            AgentType.CONCEPTS: (
                "I'm having trouble connecting to the concepts specialist. "
                "In the meantime, you can check the Python documentation at "
                "https://docs.python.org for help with your question."
            ),
            AgentType.CODE_REVIEW: (
                "The code review agent is temporarily unavailable. "
                "Try running your code through a linter like pylint or flake8 "
                "for immediate feedback on code style."
            ),
            AgentType.DEBUG: (
                "I can't reach the debug specialist right now. "
                "Try reading the error message carefully - it often contains "
                "the line number and type of error. Check for typos and "
                "missing colons or parentheses."
            ),
            AgentType.EXERCISE: (
                "The exercise generator is temporarily offline. "
                "You can practice with exercises from the curriculum "
                "or try coding challenges on sites like LeetCode or HackerRank."
            ),
            AgentType.PROGRESS: (
                "I can't fetch your progress data right now. "
                "Check back in a few minutes, or continue practicing "
                "to keep building your skills!"
            ),
        }
        
        return fallbacks.get(
            agent_type,
            "I'm having trouble processing your request. Please try again."
        )
