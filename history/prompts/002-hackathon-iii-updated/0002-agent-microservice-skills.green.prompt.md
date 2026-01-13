---
id: 0002
title: Agent Microservice Skills
stage: green
date: 2026-01-13
surface: cli
model: gemini-2.0-flash-exp
feature: 002-hackathon-iii-updated
branch: main
user: kk
command: Update agent generation skills for all 6 specialists
labels: [agents, microservices, fastapi, dapr, skills]
links:
  spec: Hackathon III_ Reusable Intelligence and Cloud-Native Mastery.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - .claude/skills/fastapi-dapr-agent/scripts/generate_complete_agent.py
  - .claude/skills/fastapi-dapr-agent/SKILL.md
tests:
  - verified generate_complete_agent.py creates valid microservice folders
---

## Prompt

Update the `fastapi-dapr-agent` skill to generate all 6 specific agent microservices (Triage, Concepts, Code Review, Debug, Exercise, Progress) with their exact logic, including Dockerfiles and main.py.

## Response snapshot

Upgraded the `fastapi-dapr-agent` skill to support all 6 specialized agents (Triage, Concepts, Code Review, Debug, Exercise, Progress).
1. Added full implementation code for all 6 agents to the `AGENT_DATA` structure.
2. Updated the generator to create `Dockerfile`, `requirements.txt`, `agent.py`, and `main.py` for each agent type.
3. Ensured correct port mapping and Dapr sidecar annotations are included in the generated code.

## Outcome

- ✅ Impact: All agentic microservices can now be independently generated and deployed.
- 🧪 Tests: Verified generated agents against current `backend/*_agent` implementations.
- 📁 Files: Updated 1 key generator script with comprehensive agent logic.
- 🔁 Next prompts: "Implement frontend and k8s manifest generation"
- 🧠 Reflection: Centralizing all agent logic in one generator simplifies the "Build All" process but requires careful management of the generator's internal data structures.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add unit tests to the generated agent code.