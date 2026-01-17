"""
Concepts Agent - Python Concept Explanations

Provides adaptive explanations of Python concepts based on
student mastery level. Generates code examples and suggests
related topics for further learning.
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
    MasteryLevel,
)
from shared.dapr_client import get_dapr_client

logger = get_logger(__name__)

# System prompt for concept explanations
CONCEPTS_SYSTEM_PROMPT = """You are an expert Python tutor for EmberLearn, specializing in explaining programming concepts clearly and engagingly.

Your role:
1. Explain Python concepts at the appropriate level for the student
2. Provide clear, runnable code examples
3. Use analogies and real-world comparisons when helpful
4. Suggest related topics for further learning
5. Be encouraging and supportive

Student mastery levels:
- BEGINNER (0-40%): Use simple language, basic examples, lots of analogies
- LEARNING (41-70%): More technical terms, practical examples, some edge cases
- PROFICIENT (71-90%): Advanced patterns, best practices, performance considerations
- MASTERED (91-100%): Expert tips, advanced use cases, common pitfalls

Always structure your response with:
1. A clear explanation of the concept
2. At least one code example (properly formatted)
3. A practical use case or analogy
4. 2-3 related topics to explore next

Keep responses focused and concise. Use markdown formatting for code blocks."""

# Topic-specific prompts
TOPIC_PROMPTS = {
    "for-loops": "Explain Python for loops, including iteration over sequences, range(), and enumerate().",
    "list-comprehension": "Explain Python list comprehensions, including syntax, conditions, and nested comprehensions.",
    "functions": "Explain Python functions, including def, parameters, return values, and docstrings.",
    "classes": "Explain Python classes, including __init__, self, attributes, and methods.",
    "try-except": "Explain Python exception handling with try/except, including multiple exceptions and finally.",
    "dictionaries": "Explain Python dictionaries, including creation, access, methods, and iteration.",
}


class ConceptsAgent:
    """
    Agent that explains Python concepts with adaptive complexity.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dapr = get_dapr_client()
        self.model = settings.openai_model
    
    async def get_student_mastery(self, user_id: str, topic: Optional[str] = None) -> str:
        """
        Get student's mastery level from progress data.
        
        Args:
            user_id: Student's user ID
            topic: Optional specific topic
            
        Returns:
            Mastery level string
        """
        try:
            # Try to get from Dapr state store
            key = f"progress:{user_id}"
            if topic:
                key = f"progress:{user_id}:{topic}"
            
            progress = await self.dapr.get_state(key)
            
            if progress and "mastery_level" in progress:
                return progress["mastery_level"]
            
        except Exception as e:
            logger.warning("failed_to_get_mastery", error=str(e))
        
        # Default to beginner
        return "beginner"
    
    async def explain(self, request: ChatRequest) -> ChatResponse:
        """
        Explain a concept based on the student's question.
        
        Args:
            request: Chat request with the question
            
        Returns:
            Explanation response
        """
        # Get student's mastery level
        mastery_level = await self.get_student_mastery(request.user_id)
        
        # Build context from history
        messages = [
            {"role": "system", "content": CONCEPTS_SYSTEM_PROMPT},
            {
                "role": "system",
                "content": f"Student mastery level: {mastery_level.upper()}. Adapt your explanation accordingly.",
            },
        ]
        
        # Add conversation history
        for msg in request.history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })
        
        # Add current question
        messages.append({
            "role": "user",
            "content": request.message,
        })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=settings.openai_max_tokens,
            )
            
            explanation = response.choices[0].message.content
            
            # Extract code examples from response
            code_examples = self._extract_code_blocks(explanation)
            
            # Get related topics
            related_topics = await self._get_related_topics(request.message)
            
            # Publish learning event
            await self._publish_learning_event(request.user_id, request.message)
            
            return ChatResponse(
                success=True,
                response=explanation,
                agent_type=AgentType.CONCEPTS,
                session_id=request.session_id or str(uuid4()),
                code_examples=code_examples,
                related_topics=related_topics,
                suggestions=[
                    "Try running the code example",
                    "Ask me to explain any part in more detail",
                    "Request a practice exercise on this topic",
                ],
            )
            
        except Exception as e:
            logger.exception("explanation_failed", error=str(e))
            return ChatResponse(
                success=False,
                message="Failed to generate explanation",
                response=self._get_fallback_explanation(request.message),
                agent_type=AgentType.CONCEPTS,
                session_id=request.session_id or str(uuid4()),
            )
    
    async def explain_topic(self, topic: str, mastery_level: str = "beginner") -> dict:
        """
        Get a structured explanation of a specific topic.
        
        Args:
            topic: Topic slug or name
            mastery_level: Student's mastery level
            
        Returns:
            Structured explanation with sections
        """
        # Get topic-specific prompt or use generic
        topic_prompt = TOPIC_PROMPTS.get(
            topic.lower().replace(" ", "-"),
            f"Explain the Python concept: {topic}",
        )
        
        messages = [
            {"role": "system", "content": CONCEPTS_SYSTEM_PROMPT},
            {
                "role": "system",
                "content": f"Student mastery level: {mastery_level.upper()}. Provide a structured explanation.",
            },
            {
                "role": "user",
                "content": f"{topic_prompt}\n\nProvide your response as JSON with these fields:\n"
                           "- title: Topic title\n"
                           "- summary: One-sentence summary\n"
                           "- explanation: Detailed explanation\n"
                           "- code_example: A complete, runnable code example\n"
                           "- analogy: Real-world analogy\n"
                           "- common_mistakes: List of common mistakes\n"
                           "- related_topics: List of related topics",
            },
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"},
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.exception("topic_explanation_failed", error=str(e))
            return {
                "title": topic,
                "summary": "Explanation temporarily unavailable",
                "explanation": "Please try again or ask a specific question about this topic.",
                "code_example": "",
                "analogy": "",
                "common_mistakes": [],
                "related_topics": [],
            }
    
    async def _get_related_topics(self, question: str) -> list[str]:
        """Extract related topics from the question."""
        # Simple keyword-based topic detection
        topic_keywords = {
            "variables": ["variable", "assign", "value", "name"],
            "loops": ["loop", "for", "while", "iterate", "repeat"],
            "functions": ["function", "def", "return", "parameter", "argument"],
            "lists": ["list", "array", "append", "index", "slice"],
            "dictionaries": ["dict", "dictionary", "key", "value", "mapping"],
            "classes": ["class", "object", "oop", "method", "attribute"],
            "exceptions": ["error", "exception", "try", "except", "raise"],
            "files": ["file", "read", "write", "open", "close"],
        }
        
        question_lower = question.lower()
        related = []
        
        for topic, keywords in topic_keywords.items():
            if any(kw in question_lower for kw in keywords):
                related.append(topic)
        
        # Always suggest at least one related topic
        if not related:
            related = ["Python basics", "Practice exercises"]
        
        return related[:3]  # Max 3 related topics
    
    def _extract_code_blocks(self, text: str) -> list[str]:
        """Extract code blocks from markdown text."""
        import re
        
        # Match ```python ... ``` or ``` ... ```
        pattern = r"```(?:python)?\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        return [match.strip() for match in matches]
    
    async def _publish_learning_event(self, user_id: str, question: str) -> None:
        """Publish learning event for analytics."""
        try:
            event = {
                "event_type": "concept_explained",
                "user_id": user_id,
                "question_preview": question[:100],
            }
            
            await self.dapr.publish_event(
                topic=settings.kafka_topic_learning,
                data=event,
            )
            
        except Exception as e:
            logger.warning("failed_to_publish_event", error=str(e))
    
    def _get_fallback_explanation(self, question: str) -> str:
        """Get a fallback explanation when AI is unavailable."""
        return (
            "I'm having trouble generating a detailed explanation right now. "
            "Here are some resources that might help:\n\n"
            "1. **Python Official Documentation**: https://docs.python.org/3/\n"
            "2. **Python Tutorial**: https://docs.python.org/3/tutorial/\n"
            "3. **Real Python**: https://realpython.com/\n\n"
            "Please try asking your question again in a moment, or rephrase it "
            "to be more specific about what you'd like to learn."
        )
