# QuickStart Guide: EmberLearn Hackathon III (Updated)

**Date**: 2026-01-11
**Feature**: 002-hackathon-iii-updated
**Prerequisites**: Node.js 18+, Python 3.11+, npm, a bash-compatible shell (WSL/Git Bash/macOS/Linux)

---

## Phase-by-Phase Implementation Order

### Phase 1: Skills Library (P1 - Foundation)
**Goal**: Maintain and validate Skills under `.claude/skills/`.

1. Verify skill inventory exists (14 skills)
2. Spot-check a few skills for required structure (`SKILL.md`, `scripts/`, `REFERENCE.md`)

### Phase 2: Local App (P1)
**Goal**: Run backend + frontend locally.

1. Run `./setup.sh`
2. Run `./start.sh`
3. Open:
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API docs: http://localhost:8000/docs

### Phase 3: Core user flows (P1)
**Goal**: Validate the learning loop.

1. Register/login
2. Chat with tutor
3. Run code (practice)
4. List exercises → submit
5. View progress dashboard

### Phase 4: Kubernetes artifacts (P2)
**Goal**: Ensure manifests exist and are coherent.

1. Inspect manifests:
   - `k8s/agents/`
   - `k8s/dapr/`
   - `k8s/kong/`
   - `k8s/frontend/`

---

## Local Development Setup

### 1. One-time setup

```bash
chmod +x setup.sh start.sh test-stack.sh
./setup.sh
```

### 2. Start the application

```bash
./start.sh
```

Evidence:
- Local startup path: `start.sh:35`

### 3. Smoke test

```bash
./test-stack.sh
```

Notes:
- `test-stack.sh` currently targets the *agent microservice* API shape (e.g., `/api/concepts`) and expects auth fields like `access_token`/`full_name`.
- The running monolith API (used by `start.sh`) uses `/api/chat` and auth responses like `{ token, user }`.

Evidence:
- Test script payload expectations: `test-stack.sh:40`
- Monolith auth schema: `backend/routers/auth.py:17`
- Monolith chat schema: `backend/routers/chat.py:23`
