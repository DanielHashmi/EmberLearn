# Feature Specification: Hackathon III - Reusable Intelligence and Cloud-Native Mastery (Updated)

**Feature Branch**: `001-hackathon-iii`
**Created**: 2026-01-11
**Status**: Draft
**Input**: Updated EmberLearn repository state: Skills library + full-stack tutoring app (Next.js + FastAPI) + k8s manifests + docs.

**API Contracts**:
- Local monolith API (used by `start.sh`): `contracts/monolith-api.yaml`
- K8s agent microservice API (used by Kong + agent deployments): `contracts/agent-api.yaml`

## Clarifications

### Session 2026-01-11

- Q: What is the primary deliverable for Hackathon III in this repo? → A: Reusable Skills under `.claude/skills/` (MCP code execution pattern); EmberLearn app is the demo.
- Q: How is the app run locally? → A: `start.sh` launches the monolith FastAPI backend (`backend/main.py`) and the Next.js frontend (`frontend/`). (`start.sh:35`)
- Q: Which JWT algorithm is used by the backend? → A: Defaults to HS256 via `JWT_ALGORITHM` env var. (`backend/services/auth.py:16`)
- Q: How does the frontend authenticate? → A: Stores JWT in localStorage (`emberlearn_token`) and attaches it as `Authorization: Bearer ...` for API calls. (`frontend/src_lib/api.ts:2`, `frontend/src_lib/api.ts:148`)
- Q: What mastery calculation is used? → A: 40% exercises + 30% quiz + 20% code quality + 10% streak bonus. (`backend/services/progress.py:55`)
- Q: What Skills exist (current)? → A: 14 skills under `.claude/skills/` (includes required and additional). (Directory listing via repo state)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Foundation Skills (Priority: P1)

As a hackathon participant, I need to create core reusable Skills with MCP Code Execution pattern so that AI agents can autonomously generate and deploy components.

**Independent Test**: Run a skill script end-to-end and verify its checks pass (prereqs + generation/deploy + verification).

**Acceptance Scenarios**:

1. **Given** the Skill directory exists, **When** inspecting any skill, **Then** it contains `SKILL.md`, `scripts/`, and `REFERENCE.md`.
   - Evidence: `.claude/skills/nextjs-production-gen/`
2. **Given** minikube/kubectl/helm are present, **When** using `kafka-k8s-setup`, **Then** Kafka deploys and verification succeeds.
   - Evidence: `.claude/skills/kafka-k8s-setup/`

---

### User Story 2 - Run EmberLearn locally (Priority: P1)

As a developer, I want to run the full stack locally so I can test the tutoring experience.

**Independent Test**: Run `./setup.sh` then `./start.sh` and use the UI.

**Acceptance Scenarios**:

1. **Given** setup has been run, **When** running `./start.sh`, **Then** backend starts on `http://localhost:8000` and frontend on `http://localhost:3000`.
   - Evidence: `start.sh:35`
2. **Given** the backend is running, **When** opening `/docs`, **Then** OpenAPI docs render.
   - Evidence: `README.md:167`

---

### User Story 3 - Authentication (Priority: P1)

As a learner, I need to register and login so my progress can be tracked.

**Independent Test**: Register → login → call `/api/auth/me`.

**Acceptance Scenarios**:

1. **Given** a new email, **When** calling `POST /api/auth/register`, **Then** user is created and an auth response is returned.
   - Request: `{ email, password, name }` (`backend/routers/auth.py:17`)
   - Response: `{ token, user }` (`backend/routers/auth.py:37`)
2. **Given** valid credentials, **When** calling `POST /api/auth/login`, **Then** an auth response is returned.
   - Request: `{ email, password }` (`backend/routers/auth.py:23`)
   - Response: `{ token, user }` (`backend/routers/auth.py:37`)
3. **Given** a stored token, **When** calling `GET /api/auth/me`, **Then** user profile is returned.
   - Response: `{ id, email, name }` (`backend/routers/auth.py:137`)
4. **Given** the frontend uses the shared API client, **When** a 401 occurs, **Then** the token is cleared and an `auth:unauthorized` event is dispatched.
   - Evidence: `frontend/src_lib/api.ts:166`

---

### User Story 4 - Tutoring chat (Priority: P1)

As a learner, I need a chat interface backed by tutoring logic.

**Independent Test**: Open `/chat` and send a message.

**Acceptance Scenarios**:

1. **Given** an authenticated user, **When** calling `POST /api/chat` with `{ message }`, **Then** a chat response is returned.
   - Request: `{ message: string }` (`backend/routers/chat.py:23`)
   - Response: `{ id, message, response, agent_type, created_at }` (`backend/routers/chat.py:27`)
2. **Given** a message, **When** triage runs, **Then** an agent type is selected and used to pick a responder.
   - Evidence: `backend/routers/chat.py:86`
3. **Given** a user has prior chats, **When** calling `GET /api/chat/history`, **Then** paginated history is returned.
   - Evidence: `backend/routers/chat.py:123`
4. **Given** a user wants to clear context, **When** calling `DELETE /api/chat/history`, **Then** all messages are removed for that user.
   - Evidence: `backend/routers/chat.py:165`

---

### User Story 5 - Practice + sandbox execution (Priority: P1)

As a learner, I need to run Python code safely.

**Independent Test**: Execute safe code; reject unsafe code.

**Acceptance Scenarios**:

1. **Given** unsafe code, **When** validating, **Then** it is rejected.
   - Evidence (validator lists + AST walk): `backend/sandbox/validator.py:23`
2. **Given** safe code, **When** calling `POST /api/execute` with `{ code }`, **Then** execution output is returned.
   - Request: `{ code: string }` (`backend/routers/execute.py:17`)
   - Response: `{ success, output, error?, execution_time_ms }` (`backend/routers/execute.py:22`)
3. **Given** code should only be validated, **When** calling `POST /api/execute/validate`, **Then** it returns `{ valid, error }`.
   - Evidence: `backend/routers/execute.py:70`

---

### User Story 6 - Exercises + grading + progress (Priority: P1)

As a learner, I need exercises and progress tracking.

**Independent Test**: List exercises → submit → see progress changes.

**Acceptance Scenarios**:

1. **Given** exercises exist, **When** calling `GET /api/exercises`, **Then** a list is returned.
   - Optional query: `?topic=<topic_slug>` (`backend/routers/exercises.py:75`)
2. **Given** a learner wants topics grouped, **When** calling `GET /api/exercises/by-topic`, **Then** a per-topic list is returned.
   - Evidence: `backend/routers/exercises.py:134`
3. **Given** a submission, **When** calling `POST /api/exercises/{exercise_id}/submit` with `{ code }`, **Then** test cases run and scoring is returned.
   - Evidence: `backend/routers/exercises.py:221`
4. **Given** a user is authenticated, **When** calling `GET /api/progress`, **Then** user stats are returned (streak, total_xp, level, overall_mastery, topics[]).
   - Evidence: `backend/routers/progress.py:30`, `backend/services/progress.py:40`
5. **Given** a user wants per-topic mastery, **When** calling `GET /api/progress/topics`, **Then** a list of per-topic progress is returned.
   - Evidence: `backend/routers/progress.py:44`
6. **Given** a user wants streak updates, **When** calling `POST /api/progress/activity`, **Then** streak and bonus XP response is returned.
   - Evidence: `backend/routers/progress.py:85`
7. **Given** a user completes an exercise, **When** calling `POST /api/progress/topics/{topic_slug}/complete-exercise`, **Then** mastery is updated for that topic.
   - Evidence: `backend/routers/progress.py:113`

---

## Requirements *(mandatory)*

### Functional Requirements

#### Skills Library

- **FR-001**: Skills library MUST contain core Skills in `.claude/skills/`.
  - Current directories include: agents-md-gen, kafka-k8s-setup, postgres-k8s-setup, fastapi-dapr-agent, mcp-code-execution, nextjs-frontend-gen, nextjs-k8s-deploy, nextjs-production-gen, docusaurus-deploy, shared-utils-gen, database-schema-gen, dapr-deploy, k8s-manifest-gen, emberlearn-build-all.
- **FR-002**: Each Skill MUST follow MCP Code Execution pattern: SKILL.md + scripts/ + REFERENCE.md.
- **FR-003**: Skills MUST be cross-agent compatible via AAIF conventions.

#### EmberLearn Application

- **FR-004**: Frontend MUST be Next.js App Router with routes for auth, chat, dashboard, practice, and exercises.
  - Evidence: `frontend/app/layout.tsx:0`, `frontend/app/chat/page.tsx:0`, `frontend/app/practice/[topic]/page.tsx:0`
- **FR-005**: Backend MUST expose REST API routes under `/api/*` for auth, chat, execute, exercises, progress.
  - Evidence: `backend/main.py:0`
- **FR-006**: Backend MUST implement JWT authentication and bcrypt password hashing.
  - Evidence: `backend/services/auth.py:7`
- **FR-007**: Sandbox MUST validate code and block unsafe behavior.
  - Evidence: `backend/sandbox/validator.py:23`
- **FR-008**: Mastery calculation MUST follow 40/30/20/10 weights.
  - Evidence: `backend/services/progress.py:55`
- **FR-009**: Documentation MUST exist in Docusaurus.
  - Evidence: `docs/sidebars.js:0`
- **FR-010**: Kubernetes manifests MUST exist for agents, Dapr components, Kong, frontend.
  - Evidence: `k8s/agents/*-deployment.yaml`, `k8s/dapr/*.yaml`, `k8s/kong/*.yaml`, `k8s/frontend/*.yaml`

### Key Entities

- **Skill**: Reusable capability under `.claude/skills/`.
- **User**: Authenticated learner tracked in DB. (`backend/models/user.py:0`)
- **Exercise**: A coding challenge with test cases. (`backend/models/exercise.py:0`)
- **Progress/Streak**: Mastery scores and streak/XP. (`backend/models/progress.py:0`, `backend/models/streak.py:0`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Local stack runs using `start.sh` and is usable end-to-end.
- **SC-002**: Auth flow works (register/login/me) and frontend attaches bearer token.
- **SC-003**: Sandbox rejects unsafe code and executes safe code.
- **SC-004**: Exercises can be listed and submitted with deterministic scoring.
- **SC-005**: Progress endpoints return mastery and streak/XP.
- **SC-006**: Skills directory contains usable Skills following MCP code execution pattern.

## Assumptions

1. Local development uses a bash-compatible shell.
2. `NEXT_PUBLIC_API_URL` points to the backend.
3. Database URL is configured (SQLite or Postgres).

## Out of Scope

1. Production-grade multi-tenant SaaS concerns (billing, orgs).
2. Full sandbox hardening beyond current constraints.

## Dependencies

1. Node 18+ and Python 3.11+.
2. Optional: minikube/kubectl/helm for k8s usage.

## Environment Variables (regeneration-critical)

### Frontend

- `NEXT_PUBLIC_API_URL`
  - Used by API client: `frontend/src_lib/api.ts:2`
  - Created by scripts when missing: `setup.sh:51`, `start.sh:63`

### Backend

**Application**
- `DEBUG` (affects SQLAlchemy echo + uvicorn reload) — `backend/main.py:33`, `backend/database/config.py:17`
- `HOST` — `backend/main.py:34`
- `PORT` — `backend/main.py:35`

**Database**
- `DATABASE_URL` (required) — `backend/database/config.py:9-12`

**Auth**
- `JWT_SECRET` — `backend/services/auth.py:16`
- `JWT_ALGORITHM` (defaults HS256) — `backend/services/auth.py:17`
- `JWT_EXPIRY_HOURS` — `backend/services/auth.py:18`

**AI Provider**
- `GROQ_API_KEY`, `GROQ_MODEL` — `backend/agents/client.py:7`
- `GROQ_BASE_URL` — `backend/.env.example:22`
- `OPENAI_API_KEY` (legacy fallback) — `backend/.env.example:24`

**CORS**
- `CORS_ORIGINS` — `backend/main.py:36`, `backend/.env.example:35`

**Sandbox**
- `SANDBOX_TIMEOUT_SECONDS`, `SANDBOX_MEMORY_LIMIT_MB` are declared in env template: `backend/.env.example:37-40`.
  - Note: the monolith sandbox service currently uses constants (5s / 50MB) in code: `backend/services/sandbox.py:20-23`.

**Future integration flags (present in env template)**
- `KAFKA_BOOTSTRAP_SERVERS` — `backend/.env.example:27`
- `DAPR_ENABLED`, `DAPR_HOST`, `DAPR_PORT` — `backend/.env.example:30-33`

## Notes

- JWT algorithm mismatch across artifacts exists (Kong/README mention RS256; backend defaults HS256). See: `README.md:58`, `k8s/kong/kong-config.yaml:174`, `backend/services/auth.py:16`.
- The repo contains both a local monolith API shape and a k8s microservice API shape; docs and smoke tests may reference the microservice shape. See: `docs/docs/api-reference.md:23`, `test-stack.sh:40`.
