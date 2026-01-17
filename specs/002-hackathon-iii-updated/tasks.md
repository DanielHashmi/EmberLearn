# Tasks: Hackathon III - Reusable Intelligence and Cloud-Native Mastery (Updated)

**Input**: Design documents from `/specs/002-hackathon-iii-updated/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/agent-api.yaml ✓, contracts/monolith-api.yaml ✓, quickstart.md ✓

**Tests**: Tests are OPTIONAL per spec.md. This task list does NOT include test tasks unless explicitly requested.

**Organization**: Tasks are grouped by user story (6 total) to enable independent implementation and testing. User stories follow priority order from spec.md (P1 → P2).

**✅ IMPLEMENTATION STATUS** (repo current state):
- **Skills**: 14 skills exist under `.claude/skills/` (required + additional)
- **Frontend**: Next.js App Router pages implemented under `frontend/app/`
- **Backend**: FastAPI monolith implemented under `backend/` with routers + services
- **Kubernetes**: manifests exist under `k8s/` for agents, Dapr, Kong, frontend
- **Docs**: Docusaurus docs exist under `docs/`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

All paths shown are relative to EmberLearn repository root.

---

## Phase 1: User Story 1 - Create/maintain Skills library (Priority: P1)

- [ ] T001 [US1] Ensure each Skill follows MCP Code Execution structure (`SKILL.md`, `scripts/`, `REFERENCE.md`)
  - Paths: `.claude/skills/*/SKILL.md`, `.claude/skills/*/scripts/`, `.claude/skills/*/REFERENCE.md`
- [ ] T002 [US1] Validate Skills inventory matches expected set (14 current)
  - Paths: `.claude/skills/`

---

## Phase 2: User Story 2 - Run EmberLearn locally (Priority: P1)

- [ ] T010 [US2] Ensure `setup.sh` provisions backend venv and frontend dependencies
  - Paths: `setup.sh`, `backend/requirements.txt`, `frontend/package.json`
- [ ] T011 [US2] Ensure `start.sh` boots backend then frontend
  - Paths: `start.sh:35`, `backend/main.py:0`

---

## Phase 3: User Story 3 - Authentication (Priority: P1)

- [ ] T020 [US3] Implement AuthService (bcrypt + JWT)
  - Paths: `backend/services/auth.py`
- [ ] T021 [US3] Implement auth router endpoints (register/login/me)
  - Paths: `backend/routers/auth.py`
- [ ] T022 [US3] Implement frontend auth pages + token storage
  - Paths: `frontend/app/(auth)/**`, `frontend/src_lib/api.ts:102`

---

## Phase 4: User Story 4 - Tutoring chat (Priority: P1)

- [ ] T030 [US4] Implement chat router endpoints and persistence
  - Paths: `backend/routers/chat.py`, `backend/models/chat.py`
- [ ] T031 [US4] Implement triage routing logic
  - Paths: `backend/agents/triage.py`
- [ ] T032 [US4] Implement chat UI
  - Paths: `frontend/app/chat/page.tsx`

---

## Phase 5: User Story 5 - Practice + sandbox execution (Priority: P1)

- [ ] T040 [US5] Implement execute router endpoints
  - Paths: `backend/routers/execute.py`
- [ ] T041 [US5] Maintain sandbox validation rules
  - Paths: `backend/sandbox/validator.py`
- [ ] T042 [US5] Maintain sandbox executor
  - Paths: `backend/sandbox/executor.py`
- [ ] T043 [US5] Implement practice route with Monaco editor
  - Paths: `frontend/app/practice/[topic]/page.tsx`

---

## Phase 6: User Story 6 - Exercises + grading + progress (Priority: P1)

- [ ] T050 [US6] Maintain exercise list/detail/submit endpoints
  - Paths: `backend/routers/exercises.py`
- [ ] T051 [US6] Maintain mastery/streak/XP rules
  - Paths: `backend/services/progress.py:55`
- [ ] T052 [US6] Maintain dashboard UI
  - Paths: `frontend/app/dashboard/page.tsx`

---

## Consistency tasks

- [ ] T090 Align JWT algorithm documentation with implementation (`README.md:55` vs `backend/services/auth.py:16`).
- [ ] T091 Decide and document sandbox ownership boundaries (monolith vs microservice).
