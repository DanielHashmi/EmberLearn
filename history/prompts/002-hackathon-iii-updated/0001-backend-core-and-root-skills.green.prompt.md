---
id: 0001
title: Backend Core and Root Skills
stage: green
date: 2026-01-13
surface: cli
model: gemini-2.0-flash-exp
feature: 002-hackathon-iii-updated
branch: main
user: kk
command: Create and update backend core and root generation skills
labels: [backend, skills, core, root, regeneration]
links:
  spec: Hackathon III_ Reusable Intelligence and Cloud-Native Mastery.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - .claude/skills/backend-core-gen/scripts/generate_core.py
  - .claude/skills/backend-core-gen/SKILL.md
  - .claude/skills/emberlearn-root-gen/scripts/generate_root.py
  - .claude/skills/emberlearn-root-gen/SKILL.md
  - .claude/skills/database-schema-gen/scripts/generate_models.py
  - .claude/skills/shared-utils-gen/scripts/generate_shared.py
tests:
  - verified generate_core.py produces all routers and services
  - verified generate_root.py produces project config files
---

## Prompt

Create a new `backend-core-gen` skill to regenerate the monolithic FastAPI backend (routers, services, config) and an `emberlearn-root-gen` skill for top-level files. Update `shared-utils-gen` and `database-schema-gen` to include exact file contents.

## Response snapshot

Implemented the backend core and root generation logic.
1. Created `backend-core-gen` to generate the monolithic FastAPI backend (main.py, routers, services, database config).
2. Created `emberlearn-root-gen` to generate top-level files (package.json, setup.sh, .gitignore, etc.).
3. Upgraded `shared-utils-gen` and `database-schema-gen` to include exact file contents for bit-perfect regeneration.

## Outcome

- ✅ Impact: The core infrastructure and monolithic backend can now be recreated from scratch using skills.
- 🧪 Tests: Generation scripts verified against existing backend file structure.
- 📁 Files: Created 2 new skills and updated 2 existing ones.
- 🔁 Next prompts: "Implement agent microservices generation"
- 🧠 Reflection: Using a dictionary of full file contents in the generator scripts ensures functional exactness but makes the scripts large. This is a trade-off for the "rebuild from zero" requirement.

## Evaluation notes (flywheel)

- Failure modes observed: Initial script truncation during write_file; resolved by splitting updates.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test core generation in a isolated sandbox.