# Implementation Plan: Hackathon III - EmberLearn (Updated)

**Branch**: `001-hackathon-iii` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/002-hackathon-iii-updated/spec.md`

## Summary

Build (and be able to reproduce) EmberLearn: a Next.js tutoring UI backed by a FastAPI API with auth, chat, exercises, progress tracking, and a sandboxed code execution path. Maintain reusable Skills as the primary hackathon deliverable.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5+ (frontend)

**Frontend**:
- Next.js App Router: `frontend/app/layout.tsx:0`

**Backend**:
- FastAPI monolith entrypoint: `backend/main.py:0`
- Routers under `backend/routers/`
- Async SQLAlchemy under `backend/database/`

**Deployment artifacts**:
- k8s manifests under `k8s/` (agents, dapr, kong, frontend)

## Constraints

- Local development uses the monolith API started by `start.sh`.
  - Evidence: `start.sh:35`
- Kubernetes manifests target microservice-style agents.
  - Evidence: `k8s/agents/triage-deployment.yaml:0`
- Sandbox must enforce strict constraints.
  - Evidence: `backend/sandbox/main.py:0`

## Architecture Overview

### Component diagram (logical)

```
Browser (Next.js)
  └── HTTP (JWT)
        └── FastAPI monolith (backend/main.py)
              ├── /api/auth
              ├── /api/chat
              ├── /api/execute
              ├── /api/exercises
              └── /api/progress

Optional K8s shape:
  Kong → Agent microservices (FastAPI per agent) + Dapr sidecars
  Dapr pubsub/state components configured under k8s/dapr/
```

### Backend layering

- API routers: `backend/routers/*.py`
- Services:
  - Auth: `backend/services/auth.py`
  - Progress: `backend/services/progress.py`
  - Sandbox (monolith): `backend/services/sandbox.py`
- Database:
  - Engine/session: `backend/database/config.py`
  - ORM models: `backend/models/*.py`

## Implementation Steps

### Phase 1 — Frontend

1. Create App Router pages for auth/chat/dashboard/practice/exercises.
   - Evidence: `frontend/app/**/page.tsx`
2. Implement `api.ts` fetch wrapper and auth token wiring.
   - Evidence: `frontend/src_lib/api.ts:136`
3. Add AuthProvider and enforce redirects on unauthorized.
   - Evidence: `frontend/src_lib/auth-context.tsx:68`

### Phase 2 — Backend monolith API

1. Create FastAPI app and include routers.
   - Evidence: `backend/main.py:0`
2. Configure async DB session.
   - Evidence: `backend/database/config.py:36`
3. Implement auth endpoints.
   - Evidence: `backend/routers/auth.py:0`
4. Implement chat endpoints.
   - Evidence: `backend/routers/chat.py:0`
5. Implement execute endpoints.
   - Evidence: `backend/routers/execute.py:31`
6. Implement exercise endpoints.
   - Evidence: `backend/routers/exercises.py:74`
7. Implement progress endpoints.
   - Evidence: `backend/routers/progress.py:30`

### Phase 3 — Sandbox

1. Validate code and block dangerous operations.
   - Evidence: `backend/sandbox/validator.py:70`
2. Execute code with strict limits.
   - Evidence: `backend/sandbox/executor.py:24`

### Phase 4 — Agent microservices (optional runtime)

1. Maintain one FastAPI service per agent under `backend/*_agent/`.
   - Example: `backend/debug_agent/main.py:67`
2. Ensure health/readiness endpoints exist.
   - Evidence: `backend/debug_agent/main.py:84`

### Phase 5 — Kubernetes manifests

1. Maintain manifests for agents.
   - Evidence: `k8s/agents/*-deployment.yaml`
2. Maintain Dapr components.
   - Evidence: `k8s/dapr/pubsub.yaml`, `k8s/dapr/statestore.yaml`
3. Maintain Kong gateway.
   - Evidence: `k8s/kong/kong-config.yaml`
4. Maintain frontend deployment/service/ingress.
   - Evidence: `k8s/frontend/deployment.yaml`

### Phase 6 — Skills library

1. Keep reusable skills under `.claude/skills/`.
   - Evidence: `.claude/skills/nextjs-production-gen/`

## Validation

- Local startup:
  - `./start.sh` starts backend + frontend. (`start.sh:35`)
- API sanity:
  - Register/login/me works.
  - Chat, execute, exercises, progress return expected payloads.
- Sandbox:
  - Unsafe imports rejected.
  - Long-running code times out.
- Docs:
  - Docusaurus pages render from `docs/sidebars.js:0`.

## Risks / follow-ups

- JWT algorithm mismatch across artifacts (Kong/README mention RS256; backend defaults HS256): `README.md:58`, `k8s/kong/kong-config.yaml:174`, `backend/services/auth.py:16`.
- API surface mismatch across artifacts (docs + Kong microservices vs local monolith routers): `docs/docs/api-reference.md:23`, `backend/main.py:82`.
- Duplicate sandbox implementations (monolith vs microservice) need a clear ownership boundary.
- `test-stack.sh` appears to validate an older/different API shape than the local monolith: `test-stack.sh:40`.
