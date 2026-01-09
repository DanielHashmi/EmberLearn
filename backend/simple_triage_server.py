"""
Simplified Triage Agent for Local Development
Runs without Dapr/Kafka dependencies
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional

# Initialize FastAPI
app = FastAPI(title="EmberLearn Triage Agent")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("⚠️  WARNING: OPENAI_API_KEY not set. Using mock responses.")
    client = None
else:
    client = OpenAI(api_key=openai_api_key)


class QueryRequest(BaseModel):
    query: str
    student_id: Optional[str] = "demo_user"


class TriageResponse(BaseModel):
    agent: str
    explanation: str
    response: str


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "triage_agent"}


@app.post("/api/triage", response_model=TriageResponse)
async def triage_query(request: QueryRequest):
    """Route student query to appropriate agent"""

    if not client:
        # Mock response when no API key
        return TriageResponse(
            agent="concepts",
            explanation="This would route to the Concepts agent in production",
            response="This is a demo response. Please set OPENAI_API_KEY to enable AI features."
        )

    try:
        # Use OpenAI to determine routing
        system_prompt = """You are a triage agent for an AI Python tutoring platform.
Analyze the student's query and determine which specialist can best help:
- CONCEPTS: Questions about Python concepts, syntax, or theory
- CODE_REVIEW: Requests for code feedback, style improvements, or bug spotting
- DEBUG: Help finding and fixing errors in code
- EXERCISE: Requests for coding challenges or practice problems
- PROGRESS: Questions about their learning progress or mastery scores

Respond with JSON: {"agent": "...", "explanation": "...", "response": "..."}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.query}
            ],
            temperature=0.7,
            max_tokens=500
        )

        content = response.choices[0].message.content

        # Parse response (simplified)
        if "CONCEPTS" in content.upper() or "concept" in content.lower():
            agent = "concepts"
        elif "CODE_REVIEW" in content.upper() or "review" in content.lower():
            agent = "code_review"
        elif "DEBUG" in content.upper() or "debug" in content.lower():
            agent = "debug"
        elif "EXERCISE" in content.upper() or "exercise" in content.lower():
            agent = "exercise"
        elif "PROGRESS" in content.upper() or "progress" in content.lower():
            agent = "progress"
        else:
            agent = "concepts"  # Default

        return TriageResponse(
            agent=agent,
            explanation=f"Routing to {agent} agent",
            response=content
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Triage failed: {str(e)}")


@app.post("/api/concepts")
async def concepts_agent(request: QueryRequest):
    """Explain Python concepts"""

    if not client:
        return {
            "response": "This is a demo response for Python concepts. Set OPENAI_API_KEY for real AI responses.",
            "examples": ["print('Hello')", "x = 5"]
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python concepts teacher. Explain concepts clearly with examples."},
                {"role": "user", "content": request.query}
            ],
            temperature=0.7,
            max_tokens=800
        )

        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/code_review")
async def code_review_agent(request: QueryRequest):
    """Review Python code"""

    if not client:
        return {
            "response": "This is a demo code review. Set OPENAI_API_KEY for real AI code analysis.",
            "suggestions": ["Add docstrings", "Use type hints"]
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python code reviewer. Analyze code for correctness, PEP 8 style, and efficiency."},
                {"role": "user", "content": request.query}
            ],
            temperature=0.5,
            max_tokens=1000
        )

        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/debug")
async def debug_agent(request: QueryRequest):
    """Help debug Python errors"""

    if not client:
        return {
            "response": "This is a demo debug response. Set OPENAI_API_KEY for real AI debugging help.",
            "hints": ["Check line numbers", "Look for syntax errors"]
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python debugging expert. Parse errors, identify root causes, provide hints before solutions."},
                {"role": "user", "content": request.query}
            ],
            temperature=0.6,
            max_tokens=1000
        )

        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/exercise")
async def exercise_agent(request: QueryRequest):
    """Generate coding exercises"""

    if not client:
        return {
            "response": "Demo exercise: Write a function that reverses a string.",
            "difficulty": "easy",
            "test_cases": ["reverse('hello') == 'olleh'"]
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Python exercise generator. Create coding challenges appropriate to skill level."},
                {"role": "user", "content": request.query}
            ],
            temperature=0.8,
            max_tokens=800
        )

        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/progress")
async def progress_agent(request: QueryRequest):
    """Track learning progress"""

    return {
        "response": "Your Python mastery: 65%. You've completed 12 exercises and 5 quizzes this week!",
        "mastery_score": 65,
        "completed_exercises": 12,
        "streak_days": 5
    }


@app.post("/api/chat")
async def chat(request: QueryRequest):
    """General chat endpoint that routes through triage"""
    triage_result = await triage_query(request)

    # Route to appropriate agent based on triage
    agent_map = {
        "concepts": concepts_agent,
        "code_review": code_review_agent,
        "debug": debug_agent,
        "exercise": exercise_agent,
        "progress": progress_agent
    }

    handler = agent_map.get(triage_result.agent, concepts_agent)
    agent_response = await handler(request)

    return {
        "routed_to": triage_result.agent,
        "explanation": triage_result.explanation,
        **agent_response
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"🚀 Starting EmberLearn API on http://localhost:{port}")
    print(f"📖 Docs: http://localhost:{port}/docs")

    if not openai_api_key:
        print("⚠️  Running in DEMO mode (no OPENAI_API_KEY)")
        print("   Set OPENAI_API_KEY environment variable for AI features")
    else:
        print("✅ OpenAI API key configured")

    uvicorn.run(app, host="0.0.0.0", port=port)
