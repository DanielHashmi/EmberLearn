# Research: Hackathon III Implementation (Updated)

**Date**: 2026-01-11
**Feature**: 002-hackathon-iii-updated
**Purpose**: Deep research on technical decisions supporting the updated spec/plan.

---

## 1. Frontend architecture

### Decision

Use Next.js App Router with a centralized API client and auth context.

### Evidence

- Layout and providers: `frontend/app/layout.tsx:0`
- API client wrapper: `frontend/src_lib/api.ts:136`
- Auth context: `frontend/src_lib/auth-context.tsx:18`

---

## 2. Backend architecture

### Decision

Support two execution shapes:

1) Local/dev uses monolith API server
- Entrypoint: `backend/main.py:0`
- Startup script: `start.sh:35`

2) K8s deployment uses microservice-style agents
- Example: `backend/debug_agent/main.py:67`
- Manifests: `k8s/agents/debug-deployment.yaml:0`

---

## 3. Sandbox security model

### Decision

Validate code before execution and block:
- dangerous imports
- dangerous builtins/calls
- reflective dunder attribute access

### Evidence

- Forbidden modules/calls/attributes lists: `backend/sandbox/validator.py:23`
- AST walk validation: `backend/sandbox/validator.py:101`

---

## 4. Progress model

### Decision

Mastery score uses a weighted model:
- 40% exercises
- 30% quizzes
- 20% code quality
- 10% consistency/streak

### Evidence

- Formula: `backend/services/progress.py:55`

---

## 5. Kubernetes deployment model

### Decision

Keep manifests for:
- agent deployments
- Dapr components (pubsub + statestore)
- Kong gateway
- frontend deployment

### Evidence

- Dapr pubsub: `k8s/dapr/pubsub.yaml:0`
- Kong config: `k8s/kong/kong-config.yaml:0`
- Frontend deployment: `k8s/frontend/deployment.yaml:0`

---

## 6. Implementation patterns worth reusing

### 6.1 Skills structure pattern (MCP code execution)

- Skill layout: `SKILL.md` (instructions), `scripts/` (execution), `REFERENCE.md` (deep docs)
- Evidence: `.claude/skills/nextjs-production-gen/`

### 6.2 Frontend API client + centralized 401 handling

- Token stored as `emberlearn_token` and attached as bearer token.
- On 401, token is cleared and `auth:unauthorized` event is dispatched; AuthProvider listens and redirects.
- Evidence: `frontend/src_lib/api.ts:102`, `frontend/src_lib/api.ts:166`, `frontend/src_lib/auth-context.tsx:68`

### 6.3 FastAPI router modularization

- `backend/main.py` wires routers; routers are grouped under `backend/routers/` with prefixes like `/api/auth`, `/api/exercises`.
- Evidence: `backend/main.py:0`, `backend/routers/exercises.py:15`

### 6.4 Sandbox validation + execution split

- Validation precedes execution; unsafe imports/calls are blocked.
- Evidence: `backend/sandbox/validator.py:23`, `backend/sandbox/executor.py:24`

### 6.5 Mastery scoring and streak bonus

- Mastery formula uses 40/30/20/10 weights.
- XP includes streak multiplier capped at 50%.
- Evidence: `backend/services/progress.py:55`, `backend/services/progress.py:104`

---

## 7. Known gaps

1. JWT algorithm mismatch across artifacts:
   - Root README claims RS256: `README.md:58`
   - Kong consumer is configured for RS256: `k8s/kong/kong-config.yaml:170`
   - Backend defaults to HS256 (env + code): `backend/.env.example:14`, `backend/services/auth.py:16`
2. API surface mismatch across artifacts:
   - Monolith API (local/dev) routes are `/api/auth/*`, `/api/chat`, `/api/execute`, `/api/exercises`, `/api/progress`: `backend/main.py:82`, `backend/routers/chat.py:19`
   - Docusaurus API reference documents agent microservice endpoints like `/api/triage/chat`, `/api/sandbox/execute`: `docs/docs/api-reference.md:23`
   - Kong is configured to route `/api/triage`, `/api/concepts`, `/api/code-review`, `/api/debug`, `/api/exercises`, `/api/progress`, `/api/sandbox` to separate services: `k8s/kong/kong-config.yaml:10`
3. Test script mismatch:
   - `test-stack.sh` uses payload fields `full_name`, expects `access_token`, and calls endpoints like `/api/concepts` that are not present in the monolith router set: `test-stack.sh:40`
   - Actual auth response is `{ token, user }` and register expects `{ email, password, name }`: `backend/routers/auth.py:17`
4. Duplicate sandbox implementations (monolith vs microservice): `backend/services/sandbox.py:0` vs `backend/sandbox/main.py:0`.
5. K8s manifests exist in multiple styles (`k8s/agents/` vs `k8s/manifests/`), which can drift.

## 8. Skill candidates to create/strengthen

- Sandbox hardening skill (validate constraints; add security tests)
- Docs consistency skill (detect mismatches between README claims and implementation defaults)
- Spec-kit-plus artifact generator (create new spec bundle from current repo state)

## 9. Notes

- Auth tokens are HS256 by default via env var (`JWT_ALGORITHM`). (`backend/services/auth.py:17`)
- Frontend uses localStorage for token persistence. (`frontend/src_lib/api.ts:5`)
