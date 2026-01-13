# API Reference

EmberLearn API documentation for all agent endpoints.

## Base URL

```
Production: https://emberlearn.app/api
Development: http://localhost:8000/api
```

## Authentication

All endpoints (except health checks) require JWT authentication:

```
Authorization: Bearer <token>
```

## Endpoints

### Triage Agent

#### POST /api/triage/chat
Route a message to the appropriate specialist agent.

**Request:**
```json
{
  "message": "How do for loops work?",
  "user_id": "user123",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "success": true,
  "response": "For loops iterate over sequences...",
  "agent_type": "concepts",
  "session_id": "session123",
  "suggestions": ["Try a for loop exercise"]
}
```

### Concepts Agent

#### POST /api/concepts/chat
Get explanations for Python concepts.

#### POST /api/concepts/explain
Get detailed explanation with examples.

**Request:**
```json
{
  "topic": "loops",
  "user_id": "user123",
  "mastery_level": "beginner"
}
```

### Code Review Agent

#### POST /api/code-review/chat
Get code review from chat message.

#### POST /api/code-review/review
Get detailed code analysis.

**Request:**
```json
{
  "code": "def hello():\n  print('hi')",
  "user_id": "user123",
  "context": "greeting function"
}
```

**Response:**
```json
{
  "success": true,
  "overall_score": 75,
  "style_score": 70,
  "efficiency_score": 80,
  "readability_score": 75,
  "issues": [
    {
      "type": "style",
      "severity": "info",
      "line": 2,
      "message": "Use 4 spaces for indentation"
    }
  ],
  "suggestions": ["Add a docstring"]
}
```

### Debug Agent

#### POST /api/debug/chat
Get debugging help from chat.

#### POST /api/debug/debug
Debug specific error with code.

**Request:**
```json
{
  "code": "print(x)",
  "error_message": "NameError: name 'x' is not defined",
  "user_id": "user123",
  "hint_level": 1
}
```

**Response:**
```json
{
  "success": true,
  "error_type": "NameError",
  "error_explanation": "Variable not defined",
  "root_cause": "Using x before assignment",
  "hint": "Define x before using it",
  "prevention_tips": ["Always initialize variables"]
}
```

### Exercise Agent

#### POST /api/exercises/generate
Generate a new exercise.

**Request:**
```json
{
  "topic": "loops",
  "difficulty": "medium",
  "user_id": "user123"
}
```

#### POST /api/exercises/grade
Grade a submission.

**Request:**
```json
{
  "exercise_id": "ex123",
  "user_id": "user123",
  "code": "def solution(n):\n  return sum(range(n))"
}
```

### Progress Agent

#### GET /api/progress/dashboard/{user_id}
Get complete dashboard data.

**Response:**
```json
{
  "user_id": "user123",
  "overall_mastery": 65.5,
  "overall_level": "learning",
  "streak_days": 5,
  "total_xp": 1250,
  "level": 3,
  "topics": [
    {
      "topic_id": "loops",
      "topic_name": "Control Flow",
      "mastery_score": 72,
      "mastery_level": "proficient"
    }
  ]
}
```

#### POST /api/progress/update-mastery
Update mastery for a topic.

### Sandbox

#### POST /api/sandbox/execute
Execute Python code safely.

**Request:**
```json
{
  "code": "print(2 + 2)",
  "user_id": "user123",
  "timeout_seconds": 5
}
```

**Response:**
```json
{
  "success": true,
  "output": "4",
  "execution_time_ms": 50,
  "timed_out": false
}
```

## Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "details": {}
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 429 | Rate Limited |
| 500 | Internal Error |
| 503 | Service Unavailable |

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| /api/triage | 60/min |
| /api/concepts | 60/min |
| /api/code-review | 30/min |
| /api/debug | 60/min |
| /api/exercises | 30/min |
| /api/progress | 120/min |
| /api/sandbox | 20/min |
