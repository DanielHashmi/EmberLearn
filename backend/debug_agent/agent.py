"""
Debug Agent - Python Error Analysis and Debugging

Helps students debug Python errors by:
- Parsing error messages and tracebacks
- Identifying root causes
- Providing hints before solutions (pedagogical approach)
- Explaining common error patterns
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

DEBUG_PROMPT = """You are an expert Python debugging assistant for EmberLearn, a learning platform.
Your job is to help students understand and fix errors in their code.

IMPORTANT: Use a pedagogical approach - provide hints before solutions!
- hint_level 1: Give a hint about what's wrong (don't reveal the fix)
- hint_level 2: Give more detailed guidance (explain the concept)
- hint_level 3: Provide the solution with explanation

Analyze the error and code to identify:
1. **Error Type**: What kind of error is this?
2. **Root Cause**: Why did this error occur?
3. **Location**: Where in the code is the problem?
4. **Fix**: How to resolve it (based on hint_level)

Be encouraging! Errors are learning opportunities.

Respond with JSON:
{
    "error_type": "SyntaxError|NameError|TypeError|etc",
    "error_explanation": "What this error means in simple terms",
    "root_cause": "Why this specific error occurred in this code",
    "hint": "A hint to guide the student (always provided)",
    "solution": "The actual fix (only if hint_level >= 3)",
    "fixed_code": "Corrected code (only if hint_level >= 3)",
    "prevention_tips": ["How to avoid this error in the future"],
    "related_errors": ["Similar errors the student might encounter"]
}"""


class DebugResponse(BaseModel):
    """Response with debugging help."""
    success: bool = True
    error_type: str
    error_explanation: str
    root_cause: str
    hint: str
    solution: Optional[str] = None
    fixed_code: Optional[str] = None
    prevention_tips: list[str] = Field(default_factory=list)
    related_errors: list[str] = Field(default_factory=list)


class ParsedError(BaseModel):
    """Parsed error information."""
    error_type: str
    error_message: str
    line_number: Optional[int] = None
    file_name: Optional[str] = None
    traceback: Optional[str] = None


class DebugAgent:
    """Agent that helps debug Python errors with progressive hints."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dapr = get_dapr_client()
        self.model = settings.openai_model
        
        # Common error patterns for quick parsing
        self.error_patterns = {
            "SyntaxError": r"SyntaxError:\s*(.+)",
            "NameError": r"NameError:\s*name\s*'(\w+)'\s*is not defined",
            "TypeError": r"TypeError:\s*(.+)",
            "IndexError": r"IndexError:\s*(.+)",
            "KeyError": r"KeyError:\s*(.+)",
            "ValueError": r"ValueError:\s*(.+)",
            "AttributeError": r"AttributeError:\s*(.+)",
            "IndentationError": r"IndentationError:\s*(.+)",
            "ZeroDivisionError": r"ZeroDivisionError:\s*(.+)",
            "FileNotFoundError": r"FileNotFoundError:\s*(.+)",
            "ImportError": r"ImportError:\s*(.+)",
            "ModuleNotFoundError": r"ModuleNotFoundError:\s*(.+)",
        }
    
    async def debug(
        self,
        code: str,
        error_message: str,
        user_id: str,
        hint_level: int = 1,
    ) -> DebugResponse:
        """
        Debug an error with progressive hints.
        
        Args:
            code: The Python code that produced the error
            error_message: The error message/traceback
            user_id: Student's user ID
            hint_level: 1=hint, 2=detailed, 3=solution
            
        Returns:
            Debugging help with appropriate level of detail
        """
        # Parse the error first
        parsed = self.parse_error(error_message)
        
        # Build the debug prompt
        user_message = f"""Debug this Python error:

**Code:**
```python
{code}
```

**Error:**
```
{error_message}
```

**Hint Level:** {hint_level} (1=hint only, 2=detailed guidance, 3=full solution)

Provide debugging help appropriate for hint level {hint_level}."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": DEBUG_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.5,
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Publish debug event
            await self._publish_debug_event(user_id, parsed.error_type)
            
            # Filter response based on hint level
            return DebugResponse(
                error_type=result.get("error_type", parsed.error_type),
                error_explanation=result.get("error_explanation", "An error occurred"),
                root_cause=result.get("root_cause", "Unable to determine root cause"),
                hint=result.get("hint", "Check your code carefully"),
                solution=result.get("solution") if hint_level >= 3 else None,
                fixed_code=result.get("fixed_code") if hint_level >= 3 else None,
                prevention_tips=result.get("prevention_tips", []),
                related_errors=result.get("related_errors", []),
            )
            
        except Exception as e:
            logger.exception("debug_failed", error=str(e))
            return self._get_fallback_debug(parsed, hint_level)
    
    async def debug_from_chat(self, request: ChatRequest) -> ChatResponse:
        """
        Debug from a chat message.
        
        Extracts code and error from the message and provides help.
        """
        # Try to extract code and error from message
        code = self._extract_code(request.message)
        error = self._extract_error(request.message)
        
        if not code and not error:
            return ChatResponse(
                success=True,
                response=(
                    "I'd be happy to help you debug! Please share:\n\n"
                    "1. **Your code** - paste it in triple backticks (```)\n"
                    "2. **The error message** - the full error you're seeing\n\n"
                    "For example:\n"
                    "```python\n"
                    "x = 5\n"
                    "print(y)\n"
                    "```\n"
                    "Error: NameError: name 'y' is not defined"
                ),
                agent_type=AgentType.DEBUG,
                session_id=request.session_id or str(uuid4()),
            )
        
        # If we have code but no error, try to identify potential issues
        if code and not error:
            return ChatResponse(
                success=True,
                response=(
                    "I see your code! What error are you getting?\n\n"
                    "Please share the complete error message so I can help you debug it."
                ),
                agent_type=AgentType.DEBUG,
                session_id=request.session_id or str(uuid4()),
            )
        
        # Determine hint level from context
        hint_level = self._determine_hint_level(request)
        
        # Perform debugging
        debug_result = await self.debug(
            code=code or "# No code provided",
            error_message=error,
            user_id=request.user_id,
            hint_level=hint_level,
        )
        
        # Format as conversational response
        response_text = self._format_debug_response(debug_result, hint_level)
        
        return ChatResponse(
            success=True,
            response=response_text,
            agent_type=AgentType.DEBUG,
            session_id=request.session_id or str(uuid4()),
            code_examples=[debug_result.fixed_code] if debug_result.fixed_code else [],
            suggestions=debug_result.prevention_tips[:3],
        )
    
    def parse_error(self, error_message: str) -> ParsedError:
        """
        Parse an error message to extract structured information.
        
        Quick analysis without AI for fast feedback.
        """
        error_type = "UnknownError"
        error_msg = error_message
        line_number = None
        file_name = None
        
        # Try to match known error patterns
        for err_type, pattern in self.error_patterns.items():
            match = re.search(pattern, error_message)
            if match:
                error_type = err_type
                error_msg = match.group(1) if match.groups() else error_message
                break
        
        # Extract line number
        line_match = re.search(r'line\s+(\d+)', error_message, re.IGNORECASE)
        if line_match:
            line_number = int(line_match.group(1))
        
        # Extract file name
        file_match = re.search(r'File\s+"([^"]+)"', error_message)
        if file_match:
            file_name = file_match.group(1)
        
        return ParsedError(
            error_type=error_type,
            error_message=error_msg,
            line_number=line_number,
            file_name=file_name,
            traceback=error_message if "Traceback" in error_message else None,
        )
    
    def _extract_code(self, message: str) -> Optional[str]:
        """Extract code from a message."""
        # Try to find code in triple backticks
        pattern = r"```(?:python)?\n?(.*?)```"
        matches = re.findall(pattern, message, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # Check if part of the message looks like code
        lines = message.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Heuristics for code detection
            if any(kw in line for kw in ['def ', 'class ', 'import ', 'from ', 'for ', 'while ', 'if ', 'print(']):
                in_code = True
            if in_code and (line.strip() or line.startswith(' ')):
                code_lines.append(line)
            elif in_code and not line.strip() and code_lines:
                # Empty line might end code block
                if any(kw in message.lower() for kw in ['error', 'traceback', 'exception']):
                    break
        
        if code_lines:
            return '\n'.join(code_lines)
        
        return None
    
    def _extract_error(self, message: str) -> Optional[str]:
        """Extract error message from text."""
        # Look for common error patterns
        error_keywords = [
            'Error:', 'Exception:', 'Traceback', 'error:', 
            'SyntaxError', 'NameError', 'TypeError', 'ValueError',
            'IndexError', 'KeyError', 'AttributeError', 'IndentationError'
        ]
        
        lines = message.split('\n')
        error_lines = []
        capturing = False
        
        for line in lines:
            if any(kw in line for kw in error_keywords):
                capturing = True
            if capturing:
                error_lines.append(line)
        
        if error_lines:
            return '\n'.join(error_lines)
        
        # Check if the whole message after code might be an error
        if '```' in message:
            parts = message.split('```')
            if len(parts) >= 3:
                after_code = parts[-1].strip()
                if any(kw in after_code for kw in error_keywords):
                    return after_code
        
        return None
    
    def _determine_hint_level(self, request: ChatRequest) -> int:
        """Determine appropriate hint level from context."""
        message_lower = request.message.lower()
        
        # Check for explicit requests
        if any(phrase in message_lower for phrase in ['give me the answer', 'just tell me', 'show me the fix', 'solution']):
            return 3
        if any(phrase in message_lower for phrase in ['more help', 'still stuck', 'don\'t understand', 'explain more']):
            return 2
        
        # Check history for repeated struggles
        if request.history:
            debug_count = sum(1 for msg in request.history if msg.agent_type == AgentType.DEBUG)
            if debug_count >= 3:
                return 3
            elif debug_count >= 1:
                return 2
        
        return 1
    
    def _format_debug_response(self, debug: DebugResponse, hint_level: int) -> str:
        """Format debug response as conversational text."""
        # Error type emoji
        emoji_map = {
            "SyntaxError": "📝",
            "NameError": "🔍",
            "TypeError": "🔄",
            "IndexError": "📊",
            "KeyError": "🔑",
            "ValueError": "⚠️",
            "AttributeError": "🎯",
            "IndentationError": "↔️",
        }
        emoji = emoji_map.get(debug.error_type, "🐛")
        
        response = f"{emoji} **{debug.error_type}**\n\n"
        response += f"**What happened:** {debug.error_explanation}\n\n"
        response += f"**Why:** {debug.root_cause}\n\n"
        
        # Hint (always shown)
        response += f"💡 **Hint:** {debug.hint}\n\n"
        
        # Solution (only at level 3)
        if hint_level >= 3 and debug.solution:
            response += f"✅ **Solution:** {debug.solution}\n\n"
            
            if debug.fixed_code:
                response += "**Fixed code:**\n"
                response += f"```python\n{debug.fixed_code}\n```\n\n"
        elif hint_level < 3:
            response += "_Need more help? Ask me again and I'll give you more details!_\n\n"
        
        # Prevention tips
        if debug.prevention_tips:
            response += "**Tips to avoid this error:**\n"
            for tip in debug.prevention_tips[:3]:
                response += f"- {tip}\n"
        
        return response
    
    async def _publish_debug_event(self, user_id: str, error_type: str) -> None:
        """Publish debug event for tracking."""
        try:
            await self.dapr.publish_event(
                topic=settings.kafka_topic_code,
                data={
                    "event_type": "debug_requested",
                    "user_id": user_id,
                    "error_type": error_type,
                },
            )
        except Exception as e:
            logger.warning("failed_to_publish_event", error=str(e))
    
    def _get_fallback_debug(self, parsed: ParsedError, hint_level: int) -> DebugResponse:
        """Fallback debug response when AI is unavailable."""
        # Provide basic help based on error type
        fallback_hints = {
            "SyntaxError": {
                "explanation": "Python couldn't understand your code's structure",
                "hint": "Check for missing colons, parentheses, or quotes",
                "tips": ["Use an IDE with syntax highlighting", "Check line endings"],
            },
            "NameError": {
                "explanation": "You're using a variable or function that doesn't exist",
                "hint": "Make sure you've defined the variable before using it",
                "tips": ["Check for typos in variable names", "Verify imports"],
            },
            "TypeError": {
                "explanation": "You're using the wrong type of data for an operation",
                "hint": "Check what types your variables are (use type())",
                "tips": ["Convert types explicitly when needed", "Check function arguments"],
            },
            "IndexError": {
                "explanation": "You're trying to access a list position that doesn't exist",
                "hint": "Remember: list indices start at 0, not 1",
                "tips": ["Check list length with len()", "Use negative indices for end"],
            },
            "KeyError": {
                "explanation": "You're trying to access a dictionary key that doesn't exist",
                "hint": "Use .get() method or check if key exists first",
                "tips": ["Use dict.get(key, default)", "Check keys with 'in' operator"],
            },
        }
        
        info = fallback_hints.get(parsed.error_type, {
            "explanation": "An error occurred in your code",
            "hint": "Review the error message carefully for clues",
            "tips": ["Read the full traceback", "Check the line number mentioned"],
        })
        
        return DebugResponse(
            error_type=parsed.error_type,
            error_explanation=info["explanation"],
            root_cause=f"Error on line {parsed.line_number}" if parsed.line_number else "Check your code",
            hint=info["hint"],
            solution="AI analysis temporarily unavailable" if hint_level >= 3 else None,
            prevention_tips=info["tips"],
            related_errors=[],
        )
