---
id: 0004
title: Define Hackathon Requirements
stage: spec
date: 2026-01-13
surface: cli
model: gemini-2.0-flash-exp
feature: 002-hackathon-iii-updated
branch: main
user: kk
command: Define project specifications based on Hackathon III requirements
labels: [spec, hackathon-iii, requirements, learnflow, mcp-code-execution]
links:
  spec: Hackathon III_ Reusable Intelligence and Cloud-Native Mastery.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - Hackathon III_ Reusable Intelligence and Cloud-Native Mastery.md
tests: N/A
---

## Prompt

Analyze the "Hackathon III: Reusable Intelligence and Cloud-Native Mastery" document and extract the core functional and technical requirements for the "LearnFlow" (EmberLearn) application. Focus on the "Skills as the Product" paradigm and the "MCP Code Execution" pattern.

## Response snapshot

### Core Requirements

1.  **Philosophy**: "Skills are the product." The goal is not just to build an app, but to build *Skills* that can autonomously build the app.
2.  **Architecture Pattern**: **MCP Code Execution**.
    *   Avoid direct MCP tool calling (context bloat).
    *   Use `SKILL.md` (instructions) + `scripts/*.py` (execution) to reduce token usage by 80-98%.
3.  **Application Domain**: "LearnFlow" (EmberLearn) - An AI-powered Python tutoring platform.
    *   **Users**: Students (learn, practice, quiz) and Teachers (monitor).
    *   **Curriculum**: 8 Python modules (Basics to Libraries).
4.  **Technical Stack**:
    *   **Frontend**: Next.js 15 + Monaco Editor.
    *   **Backend**: FastAPI + OpenAI SDK (Microservices).
    *   **Infrastructure**: Kubernetes (Minikube), Dapr (Sidecars), Kafka (Events), PostgreSQL (Neon).
    *   **Agents**: 6 Specialized Agents (Triage, Concepts, Code Review, Debug, Exercise, Progress).

### Deliverables
*   **Skills Library**: A repository of reusable skills (`.claude/skills/`).
*   **Application**: The working EmberLearn app, generated/managed by these skills.

## Outcome

- ✅ Impact: Established the "North Star" for the project. The primary objective is a robust `.claude/skills` directory capable of from-scratch regeneration.
- 🧪 Tests: N/A
- 📁 Files: N/A
- 🔁 Next prompts: "Create architectural plan for Skills-driven development"
- 🧠 Reflection: The shift from "writing code" to "teaching AI to write code" requires a fundamental change in how we structure the repository. The `scripts/` directory within each skill becomes the most critical artifact.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A