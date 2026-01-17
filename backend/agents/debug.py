"""Debug agent for helping fix Python errors."""

from .client import chat_completion

SYSTEM_PROMPT = """You are an expert Python debugger named Ember. Your role is to help users understand and fix errors in their Python code.

Guidelines:
- Analyze error messages and tracebacks carefully
- Explain what the error means in simple terms
- Identify the root cause of the problem
- Provide hints before giving the full solution
- Show the corrected code with explanations
- Teach debugging strategies and techniques
- Be patient and encouraging

Structure your response like this:
1. **Error Analysis** - What the error means
2. **Root Cause** - Why it's happening
3. **Hint** - A clue to help them fix it themselves
4. **Solution** - The fix with explanation

Use markdown formatting for code blocks and emphasis."""


class DebugAgent:
    """Agent for debugging Python code."""

    @staticmethod
    async def respond(message: str, history: list[dict] = None) -> str:
        """Generate a debugging response."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for h in history[-3:]:
                messages.append({"role": "user", "content": h.get("message", "")})
                messages.append({"role": "assistant", "content": h.get("response", "")})

        messages.append({"role": "user", "content": message})

        try:
            response = await chat_completion(messages, temperature=0.5)
            return response
        except Exception as e:
            return f"I apologize, but I'm having trouble analyzing your error right now. Please try again. (Error: {str(e)[:100]})"
