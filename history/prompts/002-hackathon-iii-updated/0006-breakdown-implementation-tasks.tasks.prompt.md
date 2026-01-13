---
id: 0006
title: Breakdown Implementation Tasks
stage: tasks
date: 2026-01-13
surface: cli
model: gemini-2.0-flash-exp
feature: 002-hackathon-iii-updated
branch: main
user: kk
command: Breakdown the plan into executable tasks for skill creation
labels: [tasks, breakdown, implementation-plan]
links:
  plan: history/prompts/002-hackathon-iii-updated/0005-architect-agentic-system.plan.prompt.md
  ticket: N/A
  adr: N/A
  pr: N/A
files: N/A
tests: N/A
---

## Prompt

Break down the architectural plan into a concrete list of tasks to update the `.claude/skills` directory. Group tasks by the component they address.

## Response snapshot

### Task List

#### Phase 1: Foundation & Core Backend
1.  [x] **Audit**: Read current `backend/` files to capture "Gold Standard" code.
2.  [x] **Skill**: Create `emberlearn-root-gen` to generate top-level config (`package.json`, `setup.sh`).
3.  [x] **Skill**: Update `shared-utils-gen` with exact content of `backend/shared/`.
4.  [x] **Skill**: Update `database-schema-gen` with exact content of `backend/database/models.py`.
5.  [x] **Skill**: Create `backend-core-gen` to generate `main.py`, `routers/`, `services/`.

#### Phase 2: Agent Microservices
6.  [x] **Audit**: Read `agent.py` and `main.py` for all 6 agents (Triage, Concepts, etc.).
7.  [x] **Skill**: Update `fastapi-dapr-agent/scripts/generate_complete_agent.py` to include `AGENT_DATA` dictionary with full source code for all agents.

#### Phase 3: Frontend & Infrastructure
8.  [x] **Audit**: Read critical frontend files (`app/`, `components/`, `src_lib/`).
9.  [x] **Skill**: Update `nextjs-production-gen` to generate the complete Next.js app structure.
10. [x] **Skill**: Update `k8s-manifest-gen` to produce specific YAMLs for all services and ingress.

#### Phase 4: Orchestration
11. [x] **Skill**: Update `emberlearn-build-all/scripts/build_all.sh` to call these new/updated skills in sequence, enabling "from-scratch" regeneration.

## Outcome

- ✅ Impact: A checklist of 11 actionable tasks that transform the generic skills library into a specific EmberLearn factory.
- 🧪 Tests: N/A
- 📁 Files: N/A
- 🔁 Next prompts: "Execute tasks: Create backend-core-gen"
- 🧠 Reflection: The sequential execution of these tasks will systematically transfer the project's "DNA" from the file system into the generator scripts.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A