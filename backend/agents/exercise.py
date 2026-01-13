"""Exercise agent for generating Python coding challenges."""

from .client import chat_completion

SYSTEM_PROMPT = """You are an expert Python exercise creator named Ember. Your role is to generate engaging coding challenges for learners.

Guidelines:
- Create exercises appropriate for the requested difficulty level
- Provide clear problem descriptions
- Include starter code when helpful
- Give example inputs and expected outputs
- Make exercises practical and interesting
- Cover various Python topics

Structure exercises like this:
1. **Exercise Title**
2. **Difficulty** - Easy/Medium/Hard
3. **Description** - What to build/solve
4. **Requirements** - Specific requirements
5. **Starter Code** - Template to begin with
6. **Example** - Sample input/output
7. **Hints** - Optional hints (hidden by default)

Use markdown formatting for code blocks."""


class ExerciseAgent:
    """Agent for generating Python exercises."""

    @staticmethod
    async def respond(message: str, history: list[dict] = None) -> str:
        """Generate an exercise response."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for h in history[-3:]:
                messages.append({"role": "user", "content": h.get("message", "")})
                messages.append({"role": "assistant", "content": h.get("response", "")})

        messages.append({"role": "user", "content": message})

        try:
            response = await chat_completion(messages, temperature=0.8)
            return response
        except Exception as e:
            return f"I apologize, but I'm having trouble generating an exercise right now. Please try again. (Error: {str(e)[:100]})"
