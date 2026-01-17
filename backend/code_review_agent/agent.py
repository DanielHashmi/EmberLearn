"""
Code Review Agent - Python Code Analysis

Analyzes code for PEP 8 compliance, efficiency, readability,
and provides specific improvement suggestions.
"""

import json
import re
from typing import Optional
from uuid import uuid4

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import get_logger
from shared.models import ChatRequest, ChatResponse, AgentType
from shared.dapr_client import get_dapr_client

logger = get_logger(__name__)

CODE_REVIEW_PROMPT = """You are an expert Python code reviewer for EmberLearn, a learning platform.
Your job is to review student code and provide constructive, educational feedback.

Review the code for:
1. **PEP 8 Style**: Naming conventions, indentation, line length, whitespace
2. **Efficiency**: Algorithm complexity, unnecessary operations, better alternatives
3. **Readability**: Clear variable names, comments, code organization
4. **Best Practices**: Pythonic idioms, error handling, type hints

Be encouraging but honest. Focus on teaching, not just criticizing.
For each issue, explain WHY it matters and HOW to fix it.

Respond with JSON:
{
    "overall_score": 0-100,
    "summary": "Brief overall assessment",
    "style_score": 0-100,
    "efficiency_score": 0-100,
    "readability_score": 0-100,
    "issues": [
        {
            "type": "style|efficiency|readability|bug",
            "severity": "info|warning|error",
            "line": line_number_or_null,
            "message": "What's wrong",
            "suggestion": "How to fix it"
        }
    ],
    "suggestions": ["General improvement suggestions"],
    "improved_code": "Improved version of the code (if significant changes needed)"
}"""


class CodeReviewResponse(BaseModel):
    success: bool = True
    overall_score: float = Field(ge=0, le=100)
    summary: str
    style_score: float = Field(ge=0, le=100)
    efficiency_score: float = Field(ge=0, le=100)
    readability_score: float = Field(ge=0, le=100)
    issues: list[dict]
    suggestions: list[str]
    improved_code: Optional[str] = None


class CodeReviewAgent:
    """Agent that reviews Python code for quality and best practices."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dapr = get_dapr_client()
        self.model = settings.openai_model
    
    async def review(
        self,
        code: str,
        user_id: str,
        context: Optional[str] = None,
        focus_areas: list[str] = None,
    ) -> CodeReviewResponse:
        """
        Perform detailed code review.
        
        Args:
            code: Python code to review
            user_id: Student's user ID
            context: What the code is supposed to do
            focus_areas: Specific areas to focus on
            
        Returns:
            Detailed review with scores and suggestions
        """
        # Build the review prompt
        user_message = f"Review this Python code:\n\n```python\n{code}\n```"
        
        if context:
            user_message += f"\n\nContext: {context}"
        
        if focus_areas:
            user_message += f"\n\nFocus especially on: {', '.join(focus_areas)}"
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": CODE_REVIEW_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.5,
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Publish review event
            await self._publish_review_event(user_id, result["overall_score"])
            
            return CodeReviewResponse(
                overall_score=result.get("overall_score", 70),
                summary=result.get("summary", "Review complete"),
                style_score=result.get("style_score", 70),
                efficiency_score=result.get("efficiency_score", 70),
                readability_score=result.get("readability_score", 70),
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", []),
                improved_code=result.get("improved_code"),
            )
            
        except Exception as e:
            logger.exception("review_failed", error=str(e))
            return self._get_fallback_review(code)
    
    async def review_from_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Review code from a chat message.
        
        Extracts code from the message and provides conversational feedback.
        """
        # Extract code from message
        code = self._extract_code(request.message)
        
        if not code:
            return ChatResponse(
                success=True,
                response=(
                    "I'd be happy to review your code! Please share the Python code "
                    "you'd like me to look at. You can paste it directly or wrap it "
                    "in triple backticks (```)."
                ),
                agent_type=AgentType.CODE_REVIEW,
                session_id=request.session_id or str(uuid4()),
            )
        
        # Perform review
        review = await self.review(code, request.user_id)
        
        # Format as conversational response
        response_text = self._format_review_response(review)
        
        return ChatResponse(
            success=True,
            response=response_text,
            agent_type=AgentType.CODE_REVIEW,
            session_id=request.session_id or str(uuid4()),
            code_examples=[review.improved_code] if review.improved_code else [],
            suggestions=review.suggestions[:3],
        )
    
    async def quick_check(self, code: str) -> dict:
        """
        Quick syntax and basic style check.
        
        Faster than full review, good for real-time feedback.
        """
        issues = []
        
        # Check for common issues without AI
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Line length
            if len(line) > 79:
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "line": i,
                    "message": f"Line exceeds 79 characters ({len(line)})",
                })
            
            # Trailing whitespace
            if line != line.rstrip():
                issues.append({
                    "type": "style",
                    "severity": "info",
                    "line": i,
                    "message": "Trailing whitespace",
                })
            
            # Mixed tabs and spaces
            if '\t' in line and '    ' in line:
                issues.append({
                    "type": "style",
                    "severity": "warning",
                    "line": i,
                    "message": "Mixed tabs and spaces",
                })
        
        # Check for syntax errors
        try:
            compile(code, '<string>', 'exec')
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            issues.append({
                "type": "bug",
                "severity": "error",
                "line": e.lineno,
                "message": f"Syntax error: {e.msg}",
            })
        
        return {
            "syntax_valid": syntax_valid,
            "issues": issues,
            "issue_count": len(issues),
        }
    
    def _extract_code(self, message: str) -> Optional[str]:
        """Extract code from a message."""
        # Try to find code in triple backticks
        pattern = r"```(?:python)?\n?(.*?)```"
        matches = re.findall(pattern, message, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Check if the whole message looks like code
        code_indicators = ['def ', 'class ', 'import ', 'for ', 'while ', 'if ', '=', 'print(']
        if any(indicator in message for indicator in code_indicators):
            # Likely code without backticks
            return message.strip()
        
        return None
    
    def _format_review_response(self, review: CodeReviewResponse) -> str:
        """Format review as conversational response."""
        # Score emoji
        if review.overall_score >= 90:
            emoji = "🌟"
            verdict = "Excellent work!"
        elif review.overall_score >= 75:
            emoji = "👍"
            verdict = "Good job!"
        elif review.overall_score >= 60:
            emoji = "📝"
            verdict = "Nice effort, with room for improvement."
        else:
            emoji = "💪"
            verdict = "Keep practicing! Here's how to improve."
        
        response = f"{emoji} **Code Review Score: {review.overall_score}/100**\n\n"
        response += f"{verdict}\n\n"
        response += f"**Summary:** {review.summary}\n\n"
        
        # Scores breakdown
        response += "**Scores:**\n"
        response += f"- Style (PEP 8): {review.style_score}/100\n"
        response += f"- Efficiency: {review.efficiency_score}/100\n"
        response += f"- Readability: {review.readability_score}/100\n\n"
        
        # Issues
        if review.issues:
            response += "**Issues Found:**\n"
            for issue in review.issues[:5]:  # Limit to 5
                severity_icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(
                    issue.get("severity", "info"), "ℹ️"
                )
                line_info = f" (line {issue['line']})" if issue.get("line") else ""
                response += f"{severity_icon} {issue['message']}{line_info}\n"
                if issue.get("suggestion"):
                    response += f"   → {issue['suggestion']}\n"
            response += "\n"
        
        # Improved code
        if review.improved_code:
            response += "**Improved Version:**\n"
            response += f"```python\n{review.improved_code}\n```\n"
        
        return response
    
    async def _publish_review_event(self, user_id: str, score: float) -> None:
        """Publish code review event."""
        try:
            await self.dapr.publish_event(
                topic=settings.kafka_topic_code,
                data={
                    "event_type": "code_reviewed",
                    "user_id": user_id,
                    "score": score,
                },
            )
        except Exception as e:
            logger.warning("failed_to_publish_event", error=str(e))
    
    def _get_fallback_review(self, code: str) -> CodeReviewResponse:
        """Fallback review when AI is unavailable."""
        quick = self.quick_check(code) if hasattr(self, 'quick_check') else {"issues": [], "syntax_valid": True}
        
        return CodeReviewResponse(
            overall_score=70 if quick.get("syntax_valid", True) else 40,
            summary="Basic review completed. AI analysis temporarily unavailable.",
            style_score=70,
            efficiency_score=70,
            readability_score=70,
            issues=quick.get("issues", []),
            suggestions=[
                "Run your code through pylint for detailed style feedback",
                "Consider adding docstrings to functions",
                "Use meaningful variable names",
            ],
        )
