---
sidebar_position: 4
---

# API Reference

Complete API documentation for EmberLearn's 6 AI agents and sandbox service.

## Base URL

```
http://kong-proxy.default.svc.cluster.local:8000
```

For local development with port-forward:
```
http://localhost:8080
```

## Authentication

All endpoints require JWT authentication:

```http
Authorization: Bearer <token>
```

Tokens are obtained via `/api/auth/login` and expire after 24 hours.

---

## Triage Agent

Routes student queries to specialist agents.

### POST /api/triage/query

**Request:**
```json
{
  "query": "How do for loops work in Python?",
  "student_id": "uuid",
  "context": {
    "topic": "loops",
    "code": "for i in range(10):\n    print(i)",
    "error": null
  }
}
```

**Response:**
```json
{
  "response": "For loops in Python iterate over sequences...",
  "agent": "concepts",
  "confidence": 0.95,
  "follow_up_suggestions": [
    "Try the loops exercise",
    "Learn about while loops"
  ]
}
```

---

## Concepts Agent

Explains Python concepts with adaptive examples.

### POST /api/concepts/explain

**Request:**
```json
{
  "topic": "functions",
  "student_id": "uuid",
  "mastery_level": "learning",
  "specific_question": "What are default parameters?"
}
```

**Response:**
```json
{
  "explanation": "Default parameters allow you to...",
  "examples": [
    {
      "code": "def greet(name='World'):\n    print(f'Hello, {name}!')",
      "description": "Function with default parameter"
    }
  ],
  "related_topics": ["*args", "**kwargs"]
}
```

---

## Code Review Agent

Analyzes code for correctness, style, and efficiency.

### POST /api/code-review/analyze

**Request:**
```json
{
  "code": "def add(a,b):\n  return a+b",
  "student_id": "uuid",
  "topic": "functions"
}
```

**Response:**
```json
{
  "rating": 75,
  "issues": [
    {
      "type": "style",
      "severity": "warning",
      "line": 1,
      "message": "Missing spaces around parameters",
      "suggestion": "def add(a, b):"
    }
  ],
  "summary": "Functional code with minor style issues",
  "strengths": ["Correct logic", "Concise implementation"],
  "improvements": ["Follow PEP 8 spacing", "Add docstring"]
}
```

---

## Debug Agent

Parses errors and provides fix suggestions.

### POST /api/debug/analyze-error

**Request:**
```json
{
  "code": "print(undefined_var)",
  "error": "NameError: name 'undefined_var' is not defined",
  "student_id": "uuid"
}
```

**Response:**
```json
{
  "root_cause": "Variable 'undefined_var' used before assignment",
  "explanation": "Python requires variables to be defined before use...",
  "fix_suggestion": "Define the variable before using it",
  "fixed_code": "undefined_var = 'Hello'\nprint(undefined_var)",
  "similar_errors_count": 3
}
```

---

## Exercise Agent

Generates and grades coding challenges.

### POST /api/exercise/generate

**Request:**
```json
{
  "topic": "loops",
  "difficulty": "beginner",
  "student_id": "uuid"
}
```

**Response:**
```json
{
  "id": "exercise-uuid",
  "topic": "loops",
  "difficulty": "beginner",
  "title": "Sum of Numbers",
  "description": "Write a function that returns the sum of numbers from 1 to n",
  "starter_code": "def sum_to_n(n):\n    # Your code here\n    pass",
  "test_cases": [
    {"input": "5", "expected_output": "15", "is_hidden": false},
    {"input": "10", "expected_output": "55", "is_hidden": true}
  ],
  "hints": ["Use a for loop", "range(1, n+1) includes n"]
}
```

### POST /api/exercise/submit

**Request:**
```json
{
  "exercise_id": "exercise-uuid",
  "code": "def sum_to_n(n):\n    return sum(range(1, n+1))",
  "student_id": "uuid"
}
```

**Response:**
```json
{
  "passed": true,
  "score": 100,
  "test_results": [
    {"test_case_id": "1", "passed": true, "actual_output": "15", "expected_output": "15"},
    {"test_case_id": "2", "passed": true, "actual_output": "55", "expected_output": "55"}
  ],
  "feedback": "Excellent! All tests passed.",
  "code_review": {
    "rating": 95,
    "summary": "Clean, Pythonic solution using built-in sum()"
  }
}
```

---

## Progress Agent

Tracks mastery scores and learning progress.

### GET /api/progress/dashboard

**Query Parameters:**
- `student_id` (required): Student UUID

**Response:**
```json
{
  "student_id": "uuid",
  "overall_mastery": 65,
  "overall_level": "learning",
  "topics": [
    {
      "topic_id": "variables",
      "topic_name": "Variables & Data Types",
      "mastery_score": 85,
      "mastery_level": "proficient",
      "exercises_completed": 12,
      "exercises_total": 15,
      "last_activity": "2024-01-15T10:30:00Z"
    }
  ],
  "streak_days": 7,
  "total_exercises_completed": 45,
  "total_time_spent_minutes": 320
}
```

---

## Sandbox Service

Executes Python code in isolated environment.

### POST /api/sandbox/execute

**Request:**
```json
{
  "code": "print('Hello, World!')",
  "student_id": "uuid",
  "timeout_ms": 5000
}
```

**Response:**
```json
{
  "output": "Hello, World!\n",
  "error": null,
  "execution_time_ms": 45,
  "memory_used_bytes": 1048576
}
```

**Limits:**
- Timeout: 5 seconds max
- Memory: 50MB max
- No network access
- No filesystem access (except temp)

---

## Kafka Topics

Events published for analytics and inter-agent communication:

| Topic | Schema |
|-------|--------|
| `learning.query` | `{student_id, query, timestamp}` |
| `learning.response` | `{student_id, agent, response, latency_ms}` |
| `code.executed` | `{student_id, code_hash, success, execution_time_ms}` |
| `code.reviewed` | `{student_id, rating, issues_count}` |
| `exercise.created` | `{exercise_id, topic, difficulty}` |
| `exercise.completed` | `{student_id, exercise_id, passed, score}` |
| `struggle.detected` | `{student_id, trigger, details}` |
| `progress.updated` | `{student_id, topic, old_score, new_score}` |

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "error": "error_code",
  "message": "Human-readable description",
  "details": {}
}
```

Common error codes:
- `unauthorized`: Invalid or missing JWT
- `validation_error`: Invalid request body
- `rate_limited`: Too many requests
- `internal_error`: Server error
