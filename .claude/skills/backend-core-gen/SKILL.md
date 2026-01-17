---
name: backend-core-gen
description: Generate the core FastAPI monolith backend for EmberLearn
---

# Backend Core Generator

## When to Use
- User wants to regenerate the main FastAPI backend
- Initializing a fresh EmberLearn project
- Recreating the monolith API server

## Instructions
1. Run the generation script:
   - `python scripts/generate_core.py`
2. Verify files are created in `backend/`

## Output
- `backend/main.py`
- `backend/routers/*.py`
- `backend/database/*.py` (excluding models which are in database-schema-gen)
- `backend/services/*.py`
- `backend/requirements.txt`
- `backend/.env.example`
