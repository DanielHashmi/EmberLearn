"""
Exercise Agent - Exercise Generation and Auto-Grading

Generates Python coding exercises tailored to student level
and provides automated grading with detailed feedback.
"""

import json
import re
import subprocess
import tempfile
import os
from typing import Optional
from uuid import uuid4
from datetime import datetime

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

import sys
sys.path.insert(0, '..')

from shared.config import settings
from shared.logging_config import get_logger
from shared.models import (
    ChatRequest, ChatResponse, AgentType,
    Exercise, Difficulty, TestCase, TestCaseResult
)
from shared.dapr_client import get_dapr_client

logger = get_logger(__name__)

EXERCISE_GENERATION_PROMPT = """You are an expert Python educator for EmberLearn.
Generate a coding exercise appropriate for the student's level.

Consider:
1. **Topic**: Focus on the specified Python concept
2. **Difficulty**: Match the difficulty level (easy/medium/hard)
3. **Mastery**: Adapt to student's current mastery score
4. **Variety**: Avoid exercises similar to previous ones

Create an exercise that:
- Has a clear, engaging problem statement
- Includes starter code with TODO comments
- Has 3-5 test cases (mix of visible and hidden)
- Provides helpful hints (progressive difficulty)

Respond with JSON:
{
    "title": "Exercise title",
    "description": "What the student will learn",
    "instructions": "Detailed problem statement",
    "starter_code": "def solution():\\n    # TODO: Implement\\n    pass",
    "estimated_time_minutes": 10,
    "hints": ["Hint 1 (easiest)", "Hint 2", "Hint 3 (most helpful)"],
    "test_cases": [
        {"name": "Test 1", "input": "input_value", "expected_output": "expected", "hidden": false},
        {"name": "Hidden Test", "input": "input", "expected_output": "output", "hidden": true}
    ],
    "solution": "Complete working solution code"
}"""

GRADING_PROMPT = """You are a Python code grader for EmberLearn.
Evaluate the student's code submission and provide constructive feedback.

Consider:
1. **Correctness**: Does it produce the right output?
2. **Code Quality**: Is it readable and well-structured?
3. **Efficiency**: Is the approach reasonable?
4. **Style**: Does it follow Python conventions?

Be encouraging! Focus on what they did well and how to improve.

Respond with JSON:
{
    "feedback": "Overall assessment of the submission",
    "strengths": ["What they did well"],
    "improvements": ["Specific suggestions for improvement"],
    "hints": ["Hints if they didn't pass all tests"],
    "improved_code": "Suggested improvements (only if helpful)"
}"""


class GradeResponse(BaseModel):
    """Response with grading results."""
    success: bool = True
    score: float = Field(ge=0, le=100)
    passed: bool
    test_results: list[TestCaseResult]
    feedback: str
    hints: list[str] = Field(default_factory=list)
    improved_code: Optional[str] = None


class ExerciseAgent:
    """Agent that generates and grades Python exercises."""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.dapr = get_dapr_client()
        self.model = settings.openai_model
        self._exercise_cache: dict[str, Exercise] = {}
    
    async def generate(
        self,
        topic: str,
        difficulty: Difficulty,
        user_id: str,
        mastery_score: Optional[float] = None,
        previous_exercises: list[str] = None,
        specific_concept: Optional[str] = None,
    ) -> Exercise:
        """
        Generate a new exercise tailored to the student.
        
        Args:
            topic: Python topic (e.g., "loops", "functions")
            difficulty: easy, medium, or hard
            user_id: Student's user ID
            mastery_score: Current mastery percentage
            previous_exercises: IDs of exercises already completed
            specific_concept: Specific concept to focus on
            
        Returns:
            Generated exercise with test cases
        """
        # Build generation prompt
        user_message = f"""Generate a Python exercise:

**Topic:** {topic}
**Difficulty:** {difficulty.value}
**Mastery Score:** {mastery_score or 'Unknown'}%
**Previous Exercises:** {len(previous_exercises or [])} completed
"""
        if specific_concept:
            user_message += f"**Focus On:** {specific_concept}\n"
        
        if previous_exercises:
            user_message += f"\nAvoid similar exercises to: {', '.join(previous_exercises[:5])}"

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXERCISE_GENERATION_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.8,  # More creativity for variety
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Create exercise object
            exercise_id = str(uuid4())
            exercise = Exercise(
                id=exercise_id,
                title=result.get("title", "Python Exercise"),
                description=result.get("description", "Practice your Python skills"),
                instructions=result.get("instructions", "Complete the function"),
                starter_code=result.get("starter_code", "def solution():\n    pass"),
                topic=topic,
                difficulty=difficulty,
                estimated_time_minutes=result.get("estimated_time_minutes", 10),
                hints=result.get("hints", []),
                test_cases=[
                    TestCase(
                        id=f"{exercise_id}-tc-{i}",
                        name=tc.get("name", f"Test {i+1}"),
                        input=str(tc.get("input", "")),
                        expected_output=str(tc.get("expected_output", "")),
                        hidden=tc.get("hidden", False),
                    )
                    for i, tc in enumerate(result.get("test_cases", []))
                ],
            )
            
            # Cache the exercise and solution
            self._exercise_cache[exercise_id] = exercise
            self._exercise_cache[f"{exercise_id}_solution"] = result.get("solution", "")
            
            # Publish event
            await self._publish_exercise_event(user_id, exercise_id, "generated")
            
            return exercise
            
        except Exception as e:
            logger.exception("exercise_generation_failed", error=str(e))
            return self._get_fallback_exercise(topic, difficulty)
    
    async def grade(
        self,
        exercise_id: str,
        user_id: str,
        code: str,
        test_cases: list[dict] = None,
    ) -> GradeResponse:
        """
        Grade a code submission.
        
        Args:
            exercise_id: ID of the exercise
            user_id: Student's user ID
            code: Submitted code
            test_cases: Test cases to run (or fetch from cache)
            
        Returns:
            Grading results with feedback
        """
        # Get test cases
        if not test_cases:
            exercise = self._exercise_cache.get(exercise_id)
            if exercise:
                test_cases = [
                    {"name": tc.name, "input": tc.input, "expected_output": tc.expected_output}
                    for tc in exercise.test_cases
                ]
            else:
                test_cases = []
        
        # Run tests
        test_results = await self._run_tests(code, test_cases)
        
        # Calculate score
        passed_count = sum(1 for r in test_results if r.passed)
        total_count = len(test_results)
        score = (passed_count / total_count * 100) if total_count > 0 else 0
        passed = passed_count == total_count
        
        # Get AI feedback
        feedback_data = await self._get_ai_feedback(code, test_results, passed)
        
        # Publish event
        await self._publish_exercise_event(
            user_id, exercise_id, "graded",
            {"score": score, "passed": passed}
        )
        
        return GradeResponse(
            score=score,
            passed=passed,
            test_results=test_results,
            feedback=feedback_data.get("feedback", "Submission graded"),
            hints=feedback_data.get("hints", []) if not passed else [],
            improved_code=feedback_data.get("improved_code"),
        )
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Handle exercise-related chat requests."""
        message_lower = request.message.lower()
        
        # Check for exercise generation request
        if any(kw in message_lower for kw in ['exercise', 'practice', 'challenge', 'problem']):
            # Extract topic and difficulty
            topic = self._extract_topic(request.message)
            difficulty = self._extract_difficulty(request.message)
            
            exercise = await self.generate(
                topic=topic,
                difficulty=difficulty,
                user_id=request.user_id,
            )
            
            response_text = self._format_exercise_response(exercise)
            
            return ChatResponse(
                success=True,
                response=response_text,
                agent_type=AgentType.EXERCISE,
                session_id=request.session_id or str(uuid4()),
                code_examples=[exercise.starter_code],
            )
        
        # Default response
        return ChatResponse(
            success=True,
            response=(
                "I can help you practice Python! Try asking:\n\n"
                "- \"Give me an easy exercise on loops\"\n"
                "- \"I want to practice functions\"\n"
                "- \"Challenge me with a hard data structures problem\"\n\n"
                "What would you like to work on?"
            ),
            agent_type=AgentType.EXERCISE,
            session_id=request.session_id or str(uuid4()),
        )
    
    async def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """Get an exercise by ID from cache."""
        return self._exercise_cache.get(exercise_id)
    
    async def get_hint(self, exercise_id: str, user_id: str, attempt_count: int) -> str:
        """Get a progressive hint based on attempt count."""
        exercise = self._exercise_cache.get(exercise_id)
        
        if not exercise or not exercise.hints:
            return "Try breaking down the problem into smaller steps."
        
        # Return hint based on attempt count (0-indexed)
        hint_index = min(attempt_count - 1, len(exercise.hints) - 1)
        return exercise.hints[hint_index]
    
    async def _run_tests(self, code: str, test_cases: list[dict]) -> list[TestCaseResult]:
        """Run code against test cases in a sandboxed environment."""
        results = []
        
        for tc in test_cases:
            result = await self._run_single_test(code, tc)
            results.append(result)
        
        return results
    
    async def _run_single_test(self, code: str, test_case: dict) -> TestCaseResult:
        """Run a single test case."""
        name = test_case.get("name", "Test")
        input_val = test_case.get("input", "")
        expected = test_case.get("expected_output", "")
        
        try:
            # Create a temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                # Wrap code to capture output
                test_code = f"""
{code}

# Test execution
import sys
from io import StringIO

# Capture stdout
old_stdout = sys.stdout
sys.stdout = StringIO()

try:
    # Try to call the main function with input
    result = None
    if 'solution' in dir():
        result = solution({input_val})
    elif 'main' in dir():
        result = main({input_val})
    
    output = sys.stdout.getvalue()
    if result is not None:
        print(result)
except Exception as e:
    print(f"Error: {{e}}")
finally:
    sys.stdout = old_stdout
    
# Print the captured output
print(sys.stdout.getvalue() if hasattr(sys.stdout, 'getvalue') else '')
"""
                f.write(test_code)
                temp_path = f.name
            
            # Run with timeout
            start_time = datetime.now()
            result = subprocess.run(
                ['python', temp_path],
                capture_output=True,
                text=True,
                timeout=settings.sandbox_timeout_seconds,
            )
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Clean up
            os.unlink(temp_path)
            
            actual_output = result.stdout.strip()
            error = result.stderr.strip() if result.stderr else None
            
            # Compare outputs
            passed = self._compare_outputs(actual_output, expected)
            
            return TestCaseResult(
                name=name,
                passed=passed,
                input=str(input_val),
                expected_output=expected,
                actual_output=actual_output,
                error=error,
                execution_time_ms=execution_time,
            )
            
        except subprocess.TimeoutExpired:
            return TestCaseResult(
                name=name,
                passed=False,
                input=str(input_val),
                expected_output=expected,
                actual_output=None,
                error="Execution timed out (5 seconds)",
            )
        except Exception as e:
            return TestCaseResult(
                name=name,
                passed=False,
                input=str(input_val),
                expected_output=expected,
                actual_output=None,
                error=str(e),
            )
    
    def _compare_outputs(self, actual: str, expected: str) -> bool:
        """Compare actual and expected outputs flexibly."""
        # Normalize whitespace
        actual_norm = ' '.join(actual.split())
        expected_norm = ' '.join(expected.split())
        
        # Direct comparison
        if actual_norm == expected_norm:
            return True
        
        # Try numeric comparison
        try:
            if float(actual_norm) == float(expected_norm):
                return True
        except (ValueError, TypeError):
            pass
        
        # Case-insensitive for strings
        if actual_norm.lower() == expected_norm.lower():
            return True
        
        return False
    
    async def _get_ai_feedback(
        self,
        code: str,
        test_results: list[TestCaseResult],
        passed: bool,
    ) -> dict:
        """Get AI-generated feedback on the submission."""
        # Build feedback prompt
        results_summary = "\n".join([
            f"- {r.name}: {'✓ Passed' if r.passed else '✗ Failed'}"
            + (f" (Error: {r.error})" if r.error else "")
            for r in test_results
        ])
        
        user_message = f"""Grade this Python submission:

**Code:**
```python
{code}
```

**Test Results:**
{results_summary}

**Overall:** {'All tests passed!' if passed else 'Some tests failed'}

Provide constructive feedback."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": GRADING_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.5,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.warning("ai_feedback_failed", error=str(e))
            return {
                "feedback": "Great effort!" if passed else "Keep trying! Review the failed tests.",
                "hints": [] if passed else ["Check your logic carefully"],
            }
    
    def _extract_topic(self, message: str) -> str:
        """Extract topic from message."""
        topics = {
            "loop": "control_flow",
            "for": "control_flow",
            "while": "control_flow",
            "if": "control_flow",
            "condition": "control_flow",
            "list": "data_structures",
            "dict": "data_structures",
            "tuple": "data_structures",
            "set": "data_structures",
            "function": "functions",
            "def": "functions",
            "return": "functions",
            "class": "oop",
            "object": "oop",
            "inherit": "oop",
            "file": "files",
            "read": "files",
            "write": "files",
            "error": "errors",
            "exception": "errors",
            "try": "errors",
            "variable": "basics",
            "string": "basics",
            "number": "basics",
            "int": "basics",
        }
        
        message_lower = message.lower()
        for keyword, topic in topics.items():
            if keyword in message_lower:
                return topic
        
        return "basics"  # Default
    
    def _extract_difficulty(self, message: str) -> Difficulty:
        """Extract difficulty from message."""
        message_lower = message.lower()
        
        if any(kw in message_lower for kw in ['easy', 'simple', 'beginner', 'basic']):
            return Difficulty.EASY
        if any(kw in message_lower for kw in ['hard', 'difficult', 'challenge', 'advanced']):
            return Difficulty.HARD
        
        return Difficulty.MEDIUM
    
    def _format_exercise_response(self, exercise: Exercise) -> str:
        """Format exercise as chat response."""
        response = f"## {exercise.title}\n\n"
        response += f"**Difficulty:** {exercise.difficulty.value.capitalize()}\n"
        response += f"**Estimated Time:** {exercise.estimated_time_minutes} minutes\n\n"
        response += f"### Instructions\n\n{exercise.instructions}\n\n"
        response += f"### Starter Code\n\n```python\n{exercise.starter_code}\n```\n\n"
        
        # Show visible test cases
        visible_tests = [tc for tc in exercise.test_cases if not tc.hidden]
        if visible_tests:
            response += "### Example Test Cases\n\n"
            for tc in visible_tests[:2]:
                response += f"- Input: `{tc.input}` → Expected: `{tc.expected_output}`\n"
        
        response += "\n_Submit your solution when ready!_"
        return response
    
    async def _publish_exercise_event(
        self,
        user_id: str,
        exercise_id: str,
        event_type: str,
        data: dict = None,
    ) -> None:
        """Publish exercise event."""
        try:
            await self.dapr.publish_event(
                topic=settings.kafka_topic_exercise,
                data={
                    "event_type": f"exercise_{event_type}",
                    "user_id": user_id,
                    "exercise_id": exercise_id,
                    **(data or {}),
                },
            )
        except Exception as e:
            logger.warning("failed_to_publish_event", error=str(e))
    
    def _get_fallback_exercise(self, topic: str, difficulty: Difficulty) -> Exercise:
        """Fallback exercise when AI is unavailable."""
        exercise_id = str(uuid4())
        
        fallback_exercises = {
            "basics": {
                "title": "Hello, Variables!",
                "description": "Practice working with variables",
                "instructions": "Create a function that takes a name and returns a greeting.",
                "starter_code": "def greet(name):\n    # TODO: Return 'Hello, {name}!'\n    pass",
                "test_cases": [
                    {"name": "Test Alice", "input": "'Alice'", "expected_output": "Hello, Alice!", "hidden": False},
                    {"name": "Test Bob", "input": "'Bob'", "expected_output": "Hello, Bob!", "hidden": False},
                ],
            },
            "control_flow": {
                "title": "Even or Odd",
                "description": "Practice conditionals",
                "instructions": "Create a function that returns 'even' or 'odd' for a number.",
                "starter_code": "def even_or_odd(n):\n    # TODO: Return 'even' or 'odd'\n    pass",
                "test_cases": [
                    {"name": "Test 4", "input": "4", "expected_output": "even", "hidden": False},
                    {"name": "Test 7", "input": "7", "expected_output": "odd", "hidden": False},
                ],
            },
            "data_structures": {
                "title": "Sum a List",
                "description": "Practice working with lists",
                "instructions": "Create a function that returns the sum of all numbers in a list.",
                "starter_code": "def sum_list(numbers):\n    # TODO: Return the sum\n    pass",
                "test_cases": [
                    {"name": "Test [1,2,3]", "input": "[1, 2, 3]", "expected_output": "6", "hidden": False},
                    {"name": "Test empty", "input": "[]", "expected_output": "0", "hidden": False},
                ],
            },
        }
        
        ex_data = fallback_exercises.get(topic, fallback_exercises["basics"])
        
        return Exercise(
            id=exercise_id,
            title=ex_data["title"],
            description=ex_data["description"],
            instructions=ex_data["instructions"],
            starter_code=ex_data["starter_code"],
            topic=topic,
            difficulty=difficulty,
            estimated_time_minutes=10,
            hints=["Think about the problem step by step", "Check the expected output format"],
            test_cases=[
                TestCase(
                    id=f"{exercise_id}-tc-{i}",
                    name=tc["name"],
                    input=tc["input"],
                    expected_output=tc["expected_output"],
                    hidden=tc.get("hidden", False),
                )
                for i, tc in enumerate(ex_data["test_cases"])
            ],
        )
