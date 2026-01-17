"""
OpenAI API Fallback - Graceful Degradation

Provides fallback responses when OpenAI API is unavailable:
1. Cached response retrieval
2. Predefined answer lookup
3. Graceful degradation messaging
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Optional, Any
from collections import OrderedDict

from .config import settings
from .logging_config import get_logger
from .models import AgentType

logger = get_logger(__name__)

# Cache settings
CACHE_MAX_SIZE = 1000
CACHE_TTL_HOURS = 24


class ResponseCache:
    """LRU cache for API responses."""
    
    def __init__(self, max_size: int = CACHE_MAX_SIZE):
        self.max_size = max_size
        self._cache: OrderedDict[str, dict] = OrderedDict()
    
    def _make_key(self, agent_type: str, query: str) -> str:
        """Create cache key from agent type and query."""
        normalized = query.lower().strip()
        content = f"{agent_type}:{normalized}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, agent_type: str, query: str) -> Optional[str]:
        """Get cached response if available and not expired."""
        key = self._make_key(agent_type, query)
        
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        
        # Check expiration
        if datetime.utcnow() > entry["expires_at"]:
            del self._cache[key]
            return None
        
        # Move to end (LRU)
        self._cache.move_to_end(key)
        
        logger.debug("cache_hit", agent_type=agent_type)
        return entry["response"]
    
    def set(self, agent_type: str, query: str, response: str, ttl_hours: int = CACHE_TTL_HOURS):
        """Cache a response."""
        key = self._make_key(agent_type, query)
        
        # Evict oldest if at capacity
        while len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        
        self._cache[key] = {
            "response": response,
            "expires_at": datetime.utcnow() + timedelta(hours=ttl_hours),
            "created_at": datetime.utcnow(),
        }
    
    def clear(self):
        """Clear all cached responses."""
        self._cache.clear()


# Predefined responses for common queries
PREDEFINED_RESPONSES = {
    AgentType.CONCEPTS: {
        "what is a variable": (
            "A **variable** in Python is like a labeled container that stores data. "
            "You create one by choosing a name and using the `=` sign:\n\n"
            "```python\n"
            "name = 'Alice'  # String variable\n"
            "age = 25        # Integer variable\n"
            "price = 19.99   # Float variable\n"
            "```\n\n"
            "Variables can be changed (they're 'variable'!) and Python automatically "
            "figures out what type of data you're storing."
        ),
        "what is a loop": (
            "A **loop** lets you repeat code multiple times. Python has two main types:\n\n"
            "**For Loop** - when you know how many times:\n"
            "```python\n"
            "for i in range(5):\n"
            "    print(i)  # Prints 0, 1, 2, 3, 4\n"
            "```\n\n"
            "**While Loop** - when you have a condition:\n"
            "```python\n"
            "count = 0\n"
            "while count < 5:\n"
            "    print(count)\n"
            "    count += 1\n"
            "```"
        ),
        "what is a function": (
            "A **function** is a reusable block of code that performs a specific task. "
            "You define it once and can call it many times:\n\n"
            "```python\n"
            "def greet(name):\n"
            "    return f'Hello, {name}!'\n\n"
            "# Call the function\n"
            "message = greet('Alice')\n"
            "print(message)  # Hello, Alice!\n"
            "```\n\n"
            "Functions help organize code and avoid repetition."
        ),
        "what is a list": (
            "A **list** is an ordered collection that can hold multiple items:\n\n"
            "```python\n"
            "fruits = ['apple', 'banana', 'cherry']\n\n"
            "# Access by index (starts at 0)\n"
            "print(fruits[0])  # apple\n\n"
            "# Add items\n"
            "fruits.append('date')\n\n"
            "# Loop through\n"
            "for fruit in fruits:\n"
            "    print(fruit)\n"
            "```\n\n"
            "Lists are mutable - you can change them after creation."
        ),
        "what is a dictionary": (
            "A **dictionary** stores key-value pairs, like a real dictionary:\n\n"
            "```python\n"
            "student = {\n"
            "    'name': 'Alice',\n"
            "    'age': 20,\n"
            "    'grade': 'A'\n"
            "}\n\n"
            "# Access by key\n"
            "print(student['name'])  # Alice\n\n"
            "# Add/update\n"
            "student['email'] = 'alice@example.com'\n"
            "```\n\n"
            "Use dictionaries when you need to look up values by a unique key."
        ),
        "what is a class": (
            "A **class** is a blueprint for creating objects. It bundles data and functions together:\n\n"
            "```python\n"
            "class Dog:\n"
            "    def __init__(self, name):\n"
            "        self.name = name\n"
            "    \n"
            "    def bark(self):\n"
            "        return f'{self.name} says woof!'\n\n"
            "# Create an object\n"
            "my_dog = Dog('Buddy')\n"
            "print(my_dog.bark())  # Buddy says woof!\n"
            "```\n\n"
            "Classes are the foundation of Object-Oriented Programming (OOP)."
        ),
    },
    AgentType.DEBUG: {
        "nameerror": (
            "**NameError** means Python can't find a variable or function you're trying to use.\n\n"
            "**Common causes:**\n"
            "1. Typo in the variable name\n"
            "2. Using a variable before defining it\n"
            "3. Variable defined in a different scope\n\n"
            "**Fix:** Check spelling and make sure you've defined the variable before using it."
        ),
        "typeerror": (
            "**TypeError** means you're using the wrong type of data for an operation.\n\n"
            "**Common causes:**\n"
            "1. Adding a string to a number: `'5' + 5`\n"
            "2. Calling something that isn't a function\n"
            "3. Wrong number of arguments to a function\n\n"
            "**Fix:** Check your data types with `type()` and convert if needed."
        ),
        "indexerror": (
            "**IndexError** means you're trying to access a list position that doesn't exist.\n\n"
            "**Common causes:**\n"
            "1. List is empty but you're accessing `list[0]`\n"
            "2. Off-by-one error (remember: indices start at 0!)\n"
            "3. Loop going past the end of the list\n\n"
            "**Fix:** Check list length with `len()` before accessing."
        ),
        "syntaxerror": (
            "**SyntaxError** means Python can't understand your code's structure.\n\n"
            "**Common causes:**\n"
            "1. Missing colon after `if`, `for`, `def`, `class`\n"
            "2. Unmatched parentheses or brackets\n"
            "3. Missing quotes around strings\n\n"
            "**Fix:** Check the line number in the error and look for typos."
        ),
        "keyerror": (
            "**KeyError** means you're trying to access a dictionary key that doesn't exist.\n\n"
            "**Common causes:**\n"
            "1. Typo in the key name\n"
            "2. Key hasn't been added yet\n"
            "3. Case sensitivity (`'Name'` vs `'name'`)\n\n"
            "**Fix:** Use `.get()` method or check with `if key in dict`."
        ),
    },
    AgentType.CODE_REVIEW: {
        "default": (
            "Here are some general Python best practices:\n\n"
            "1. **Use meaningful variable names** - `user_count` not `x`\n"
            "2. **Follow PEP 8** - 4 spaces for indentation, max 79 chars per line\n"
            "3. **Add docstrings** - Explain what functions do\n"
            "4. **Handle errors** - Use try/except for risky operations\n"
            "5. **Keep functions small** - Each should do one thing well\n\n"
            "Would you like me to review specific code?"
        ),
    },
    AgentType.TRIAGE: {
        "default": (
            "I can help you with:\n\n"
            "- **Learning concepts** - Ask me to explain any Python topic\n"
            "- **Debugging** - Share your error and I'll help fix it\n"
            "- **Code review** - Paste your code for feedback\n"
            "- **Practice** - Request exercises to test your skills\n"
            "- **Progress** - Check how you're doing\n\n"
            "What would you like help with?"
        ),
    },
}

# Graceful degradation messages
DEGRADATION_MESSAGES = {
    AgentType.CONCEPTS: (
        "I'm having trouble connecting to my knowledge base right now. "
        "Here's what I can tell you from my basic knowledge:\n\n"
        "{fallback_content}\n\n"
        "_For more detailed explanations, please try again in a few minutes._"
    ),
    AgentType.DEBUG: (
        "I'm experiencing some technical difficulties, but I can still help!\n\n"
        "{fallback_content}\n\n"
        "_For more specific debugging help, please try again shortly._"
    ),
    AgentType.CODE_REVIEW: (
        "My detailed analysis is temporarily unavailable. "
        "Here's a basic review:\n\n"
        "{fallback_content}\n\n"
        "_For comprehensive feedback, please try again in a few minutes._"
    ),
    AgentType.EXERCISE: (
        "I'm having trouble generating a custom exercise right now. "
        "Here's a practice problem you can try:\n\n"
        "{fallback_content}\n\n"
        "_For personalized exercises, please try again shortly._"
    ),
    AgentType.PROGRESS: (
        "I couldn't fetch your complete progress data. "
        "Here's what I have:\n\n"
        "{fallback_content}\n\n"
        "_For full progress details, please try again in a few minutes._"
    ),
    AgentType.TRIAGE: (
        "I'm experiencing some connectivity issues. "
        "Let me help you with what I can:\n\n"
        "{fallback_content}"
    ),
}


class FallbackHandler:
    """Handles fallback responses when OpenAI API is unavailable."""
    
    def __init__(self):
        self.cache = ResponseCache()
        self._api_status: dict[str, bool] = {}
        self._last_check: dict[str, datetime] = {}
    
    def get_fallback_response(
        self,
        agent_type: AgentType,
        query: str,
        context: Optional[dict] = None,
    ) -> str:
        """
        Get a fallback response for a query.
        
        Priority:
        1. Cached response (if available)
        2. Predefined response (if query matches)
        3. Generic degradation message
        """
        # Try cache first
        cached = self.cache.get(agent_type.value, query)
        if cached:
            return cached
        
        # Try predefined responses
        predefined = self._get_predefined_response(agent_type, query)
        if predefined:
            return self._wrap_with_degradation(agent_type, predefined)
        
        # Return generic fallback
        return self._get_generic_fallback(agent_type, context)
    
    def cache_response(self, agent_type: AgentType, query: str, response: str):
        """Cache a successful API response for future fallback."""
        self.cache.set(agent_type.value, query, response)
    
    def mark_api_status(self, agent_type: AgentType, is_available: bool):
        """Track API availability status."""
        self._api_status[agent_type.value] = is_available
        self._last_check[agent_type.value] = datetime.utcnow()
    
    def is_api_available(self, agent_type: AgentType) -> bool:
        """Check if API is currently available."""
        return self._api_status.get(agent_type.value, True)
    
    def _get_predefined_response(self, agent_type: AgentType, query: str) -> Optional[str]:
        """Look up predefined response for common queries."""
        responses = PREDEFINED_RESPONSES.get(agent_type, {})
        
        # Normalize query
        query_lower = query.lower().strip()
        
        # Direct match
        if query_lower in responses:
            return responses[query_lower]
        
        # Partial match
        for key, response in responses.items():
            if key in query_lower or query_lower in key:
                return response
        
        # Default response for agent type
        if "default" in responses:
            return responses["default"]
        
        return None
    
    def _wrap_with_degradation(self, agent_type: AgentType, content: str) -> str:
        """Wrap content with degradation message."""
        template = DEGRADATION_MESSAGES.get(
            agent_type,
            "Here's what I can help with:\n\n{fallback_content}"
        )
        return template.format(fallback_content=content)
    
    def _get_generic_fallback(self, agent_type: AgentType, context: Optional[dict]) -> str:
        """Get generic fallback when no specific response available."""
        fallbacks = {
            AgentType.CONCEPTS: (
                "I'd love to explain that concept, but I'm having technical difficulties. "
                "Try asking about: variables, loops, functions, lists, dictionaries, or classes."
            ),
            AgentType.DEBUG: (
                "I can help debug your code! Please share:\n"
                "1. Your code\n"
                "2. The error message\n\n"
                "Common errors I can help with: NameError, TypeError, IndexError, SyntaxError, KeyError."
            ),
            AgentType.CODE_REVIEW: (
                "I'd be happy to review your code! Please paste it and I'll provide feedback on:\n"
                "- Code style (PEP 8)\n"
                "- Efficiency\n"
                "- Readability\n"
                "- Best practices"
            ),
            AgentType.EXERCISE: (
                "Here's a quick exercise:\n\n"
                "**Sum of Numbers**\n"
                "Write a function that takes a list of numbers and returns their sum.\n\n"
                "```python\n"
                "def sum_numbers(numbers):\n"
                "    # Your code here\n"
                "    pass\n"
                "```\n\n"
                "Test: `sum_numbers([1, 2, 3, 4, 5])` should return `15`"
            ),
            AgentType.PROGRESS: (
                "I couldn't load your full progress. Keep practicing and check back soon!\n\n"
                "**Quick Tips:**\n"
                "- Complete exercises daily to build your streak\n"
                "- Review topics where you scored below 70%\n"
                "- Ask for help when stuck - that's how you learn!"
            ),
            AgentType.TRIAGE: PREDEFINED_RESPONSES[AgentType.TRIAGE]["default"],
        }
        
        return fallbacks.get(agent_type, "I'm temporarily unavailable. Please try again shortly.")


# Global instance
_fallback_handler: Optional[FallbackHandler] = None


def get_fallback_handler() -> FallbackHandler:
    """Get or create the global fallback handler instance."""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FallbackHandler()
    return _fallback_handler
