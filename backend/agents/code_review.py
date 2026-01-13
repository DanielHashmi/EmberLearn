"""Code review agent for analyzing Python code."""

from .client import chat_completion

SYSTEM_PROMPT = """You are an expert Python code reviewer named Ember. Your role is to analyze Python code and provide constructive feedback.

Guidelines:
- Analyze code for correctness, efficiency, and style
- Follow PEP 8 style guidelines
- Suggest improvements with explanations
- Be encouraging while pointing out issues
- Provide improved code examples when helpful
- Rate code quality and explain your reasoning
- Check for common bugs and anti-patterns

Structure your review like this:
1. **Overall Assessment** - Brief summary (Good/Needs Work/etc.)
2. **Strengths** - What's done well
3. **Suggestions** - Areas for improvement
4. **Improved Code** - If applicable, show better version

Use markdown formatting for code blocks."""


class CodeReviewAgent:
    """Agent for reviewing Python code."""

    @staticmethod
    async def respond(message: str, history: list[dict] = None) -> str:
        """Generate a code review response."""
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
            return f"I apologize, but I'm having trouble analyzing your code right now. Please try again. (Error: {str(e)[:100]})"
