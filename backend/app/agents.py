"""AI Agents for EmberLearn"""

import json
from typing import Dict, Any, Optional
import structlog

from openai import OpenAI, APIError

from app.config import settings

logger = structlog.get_logger()

# Initialize OpenAI client
client = None
if settings.openai_api_key:
    client = OpenAI(api_key=settings.openai_api_key)


# ============================================================================
# Triage Agent - Routes queries to specialists
# ============================================================================

async def triage_agent(query: str, student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Triage agent - analyzes query and routes to appropriate specialist
    Returns: {agent, explanation, response}
    """
    if not client:
        return {
            "agent": "concepts",
            "explanation": "Demo mode: routing to concepts agent",
            "response": "OpenAI API key not configured. Set OPENAI_API_KEY environment variable.",
        }

    try:
        system_prompt = """You are a triage agent for an AI Python tutoring platform.
Analyze the student's query and determine which specialist can best help:
- CONCEPTS: Questions about Python concepts, syntax, theory, or how things work
- CODE_REVIEW: Requests for code feedback, style improvements, bug spotting, or PEP 8
- DEBUG: Help finding and fixing errors, tracebacks, or runtime issues
- EXERCISE: Requests for coding challenges, practice problems, or hands-on practice
- PROGRESS: Questions about learning progress, mastery scores, or streaks

Respond with ONLY valid JSON (no markdown, no extra text):
{"agent": "...", "explanation": "...", "response": "..."}"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=300
        )

        content = response.choices[0].message.content or ""

        # Try to parse JSON response
        try:
            result = json.loads(content)
            agent = result.get("agent", "concepts").lower()

            # Validate agent choice
            valid_agents = ["concepts", "code_review", "debug", "exercise", "progress"]
            if agent not in valid_agents:
                agent = "concepts"

            return {
                "agent": agent,
                "explanation": result.get("explanation", "Routing to specialist"),
                "response": result.get("response", ""),
            }
        except json.JSONDecodeError:
            # Fallback: parse from text
            content_upper = content.upper()
            if "CONCEPTS" in content_upper or "CONCEPT" in content_upper:
                agent = "concepts"
            elif "CODE_REVIEW" in content_upper or "REVIEW" in content_upper:
                agent = "code_review"
            elif "DEBUG" in content_upper:
                agent = "debug"
            elif "EXERCISE" in content_upper:
                agent = "exercise"
            elif "PROGRESS" in content_upper:
                agent = "progress"
            else:
                agent = "concepts"

            return {
                "agent": agent,
                "explanation": f"Routing to {agent} agent",
                "response": content,
            }

    except APIError as e:
        logger.error("openai_api_error", error=str(e))
        return {
            "agent": "concepts",
            "explanation": "Error in triage (using default)",
            "response": f"API Error: {str(e)}",
        }
    except Exception as e:
        logger.error("triage_error", error=str(e))
        raise


# ============================================================================
# Concepts Agent - Explains Python concepts
# ============================================================================

async def concepts_agent(query: str, student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Concepts agent - explains Python concepts with examples
    Returns: {response, examples, concepts}
    """
    if not client:
        return {
            "response": "Demo mode: Python concepts explained. Set OPENAI_API_KEY for real AI responses.",
            "examples": ["print('Hello')", "x = 5"],
            "concepts": ["variables", "functions"],
        }

    try:
        system_prompt = """You are an expert Python concepts teacher.
Your job is to:
1. Explain Python concepts clearly and simply
2. Use real-world analogies
3. Provide 2-3 concrete code examples
4. Make it engaging and not overwhelming

Format your response as:
**Explanation:** [Clear, simple explanation]
**Analogy:** [Real-world comparison]
**Examples:**
```python
[example 1]
```
```python
[example 2]
```
**Key Points:**
- Point 1
- Point 2
- Point 3"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content or ""

        return {
            "response": content,
            "examples": extract_code_blocks(content),
            "concepts": extract_concepts(query),
        }

    except Exception as e:
        logger.error("concepts_agent_error", error=str(e))
        raise


# ============================================================================
# Code Review Agent - Analyzes code quality
# ============================================================================

async def code_review_agent(query: str, student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Code review agent - analyzes code for correctness, style, and efficiency
    Returns: {response, suggestions, issues}
    """
    if not client:
        return {
            "response": "Demo mode: Code review feedback. Set OPENAI_API_KEY for real analysis.",
            "suggestions": ["Add docstrings", "Use type hints", "Simplify logic"],
            "issues": [],
        }

    try:
        system_prompt = """You are an expert Python code reviewer.
Analyze the provided code for:
1. Correctness and bugs
2. PEP 8 style compliance
3. Performance and efficiency
4. Best practices
5. Readability and maintainability

Format your response as:
**Overall Assessment:** [1-2 sentence summary]
**Issues Found:**
- [Issue 1]: [Explanation and fix]
- [Issue 2]: [Explanation and fix]
**Suggestions for Improvement:**
- [Suggestion 1]
- [Suggestion 2]
**Positive Aspects:**
- [What's good about this code]

Be constructive and encouraging!"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.5,
            max_tokens=1200
        )

        content = response.choices[0].message.content or ""

        return {
            "response": content,
            "suggestions": extract_suggestions(content),
            "issues": extract_issues(content),
        }

    except Exception as e:
        logger.error("code_review_error", error=str(e))
        raise


# ============================================================================
# Debug Agent - Helps fix errors
# ============================================================================

async def debug_agent(query: str, student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Debug agent - helps identify and fix errors
    Returns: {response, hints, root_cause}
    """
    if not client:
        return {
            "response": "Demo mode: Debugging help. Set OPENAI_API_KEY for real debugging.",
            "hints": ["Check line numbers", "Look for syntax errors", "Verify variable names"],
            "root_cause": "Unknown",
        }

    try:
        system_prompt = """You are an expert Python debugging expert.
When the student shares an error or problematic code:
1. Identify the root cause
2. Explain WHY the error occurred
3. Provide hints (don't just give the solution)
4. Guide them to the fix step-by-step

Format your response as:
**Error Analysis:** [What went wrong]
**Root Cause:** [Why it happened]
**Hints to Guide You:**
1. [Hint 1 - not the solution, but pointing direction]
2. [Hint 2]
3. [Hint 3]
**When you're stuck, the fix is:** [Only reveal if they ask]

Be a helpful guide, not a solution giver!"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.6,
            max_tokens=1200
        )

        content = response.choices[0].message.content or ""

        return {
            "response": content,
            "hints": extract_hints(content),
            "root_cause": extract_root_cause(content),
        }

    except Exception as e:
        logger.error("debug_error", error=str(e))
        raise


# ============================================================================
# Exercise Agent - Generates coding challenges
# ============================================================================

async def exercise_agent(query: str, student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Exercise agent - generates coding challenges and practice problems
    Returns: {response, difficulty, test_cases}
    """
    if not client:
        return {
            "response": "Demo mode: Write a function that reverses a string.",
            "difficulty": "easy",
            "test_cases": ["reverse('hello') == 'olleh'", "reverse('a') == 'a'"],
        }

    try:
        system_prompt = """You are an expert Python exercise generator.
Create coding challenges that:
1. Match the student's skill level
2. Teach a specific concept
3. Are achievable in 5-15 minutes
4. Include test cases

Format your response as:
**Exercise Title:** [Clear, descriptive name]
**Difficulty:** [easy/medium/hard]
**Description:** [What the student should build]
**Requirements:**
- Requirement 1
- Requirement 2
- Requirement 3
**Starter Code:** (if helpful)
```python
def solution():
    pass
```
**Test Cases:**
```
test_case_1: solution(input1) == expected_output1
test_case_2: solution(input2) == expected_output2
test_case_3: solution(input3) == expected_output3
```
**Hints (if stuck):**
- Hint 1
- Hint 2"""

        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.8,
            max_tokens=1200
        )

        content = response.choices[0].message.content or ""

        return {
            "response": content,
            "difficulty": extract_difficulty(content),
            "test_cases": extract_test_cases(content),
        }

    except Exception as e:
        logger.error("exercise_error", error=str(e))
        raise


# ============================================================================
# Progress Agent - Tracks learning progress
# ============================================================================

async def progress_agent(query: str, student_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Progress agent - tracks and reports learning progress
    Returns: {response, mastery_score, completed_exercises, streak_days}
    """
    # For MVP, return demo data (would connect to database in production)
    return {
        "response": f"""Great question! Here's your learning progress:

**Mastery Score:** 65% 🎯
You're doing well! Keep practicing to improve.

**This Week:**
- Completed exercises: 12 ✅
- Quiz score: 78% 📊
- Days active: 5 consecutive 🔥

**Recommended Next Steps:**
1. Practice more list operations (70% mastery)
2. Work on dictionary comprehensions (45% mastery)
3. Study exception handling (0% - new topic!)

**Streak:** You're on a 5-day learning streak! 🔥 Keep it up!""",
        "mastery_score": 65.0,
        "completed_exercises": 12,
        "streak_days": 5,
    }


# ============================================================================
# Helper Functions
# ============================================================================

def extract_code_blocks(text: str) -> list:
    """Extract Python code blocks from response"""
    import re
    pattern = r"```python\n(.*?)\n```"
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]


def extract_concepts(text: str) -> list:
    """Extract key concepts from query"""
    concepts = []
    keywords = ["function", "class", "loop", "list", "dict", "variable", "string", "error"]
    for keyword in keywords:
        if keyword.lower() in text.lower():
            concepts.append(keyword)
    return concepts


def extract_suggestions(text: str) -> list:
    """Extract improvement suggestions from review"""
    import re
    pattern = r"[-•]\s*([^:\n]+):?\s*([^\n]*)"
    matches = re.findall(pattern, text)
    return [f"{title}: {detail}".strip() for title, detail in matches[:5]]


def extract_issues(text: str) -> list:
    """Extract issues from code review"""
    import re
    lines = text.split("\n")
    issues = []
    for line in lines:
        if line.strip().startswith("- ") and ":" in line:
            issues.append(line.strip()[2:])
    return issues[:5]


def extract_hints(text: str) -> list:
    """Extract hints from debug response"""
    import re
    pattern = r"\d+\.\s*([^\n]+)"
    matches = re.findall(pattern, text)
    return [m.strip() for m in matches[:5]]


def extract_root_cause(text: str) -> str:
    """Extract root cause from debug response"""
    if "Root Cause:" in text:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "Root Cause:" in line:
                return lines[i].split("Root Cause:")[-1].strip()
    return "Check the response for details"


def extract_difficulty(text: str) -> str:
    """Extract difficulty level from exercise"""
    text_lower = text.lower()
    if "easy" in text_lower:
        return "easy"
    elif "hard" in text_lower or "advanced" in text_lower:
        return "hard"
    else:
        return "medium"


def extract_test_cases(text: str) -> list:
    """Extract test cases from exercise"""
    import re
    pattern = r"test_case.*?:\s*([^\n]+)"
    matches = re.findall(pattern, text, re.IGNORECASE)
    return matches[:5]
