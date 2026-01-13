"""Concepts agent for explaining Python concepts."""

from .client import chat_completion

SYSTEM_PROMPT = """You are an expert Python tutor named Ember. Your role is to explain Python concepts clearly and helpfully.

Guidelines:
- Explain concepts in a clear, beginner-friendly way
- Use practical code examples to illustrate points
- Break down complex topics into digestible parts
- Encourage the learner and be supportive
- If asked about non-Python topics, gently redirect to Python
- Use markdown formatting for code blocks and emphasis
- Keep responses focused and not too long (aim for 200-400 words unless more detail is needed)

Always format code examples like this:
```python
# Your code here
```"""


class ConceptsAgent:
    """Agent for explaining Python concepts."""

    @staticmethod
    async def respond(message: str, history: list[dict] = None) -> str:
        """Generate a response explaining Python concepts."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history if provided
        if history:
            for h in history[-5:]:  # Last 5 messages for context
                messages.append({"role": "user", "content": h.get("message", "")})
                messages.append({"role": "assistant", "content": h.get("response", "")})

        messages.append({"role": "user", "content": message})

        try:
            response = await chat_completion(messages, temperature=0.7)
            return response
        except Exception as e:
            return f"I apologize, but I'm having trouble connecting right now. Please try again in a moment. (Error: {str(e)[:100]})"
