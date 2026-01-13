"""Triage agent for routing messages to appropriate specialists."""


class TriageAgent:
    """Routes user messages to the appropriate specialist agent."""

    KEYWORDS = {
        "concepts": [
            "explain", "what is", "how does", "concept", "learn", "understand",
            "tell me about", "describe", "definition", "meaning", "tutorial",
            "teach", "help me understand", "basics", "introduction"
        ],
        "code_review": [
            "review", "check my code", "improve", "feedback", "optimize",
            "refactor", "better way", "code quality", "pep8", "style",
            "clean up", "suggestions"
        ],
        "debug": [
            "error", "bug", "fix", "debug", "doesn't work", "exception",
            "traceback", "failing", "broken", "issue", "problem", "wrong",
            "not working", "crash", "help me fix"
        ],
        "exercise": [
            "exercise", "practice", "challenge", "quiz", "test me",
            "give me a problem", "coding challenge", "assignment", "task"
        ],
    }

    @classmethod
    def route(cls, message: str) -> str:
        """Route a message to the appropriate agent type."""
        message_lower = message.lower()

        # Check each agent's keywords
        for agent_type, keywords in cls.KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return agent_type

        # Default to concepts agent for general questions
        return "concepts"
