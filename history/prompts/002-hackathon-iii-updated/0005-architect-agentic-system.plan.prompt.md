---
id: 0005
title: Architect Agentic System
stage: plan
date: 2026-01-13
surface: cli
model: gemini-2.0-flash-exp
feature: 002-hackathon-iii-updated
branch: main
user: kk
command: Create architectural plan for Skills-based regeneration
labels: [plan, architecture, skills-design, microservices]
links:
  spec: history/prompts/002-hackathon-iii-updated/0004-define-hackathon-requirements.spec.prompt.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - .claude/skills/
tests: N/A
---

## Prompt

Design the system architecture for EmberLearn and the corresponding Skills Library structure to support autonomous regeneration. Define the roles of specific skills and how they interact to build the full stack (Frontend, Backend, Infrastructure).

## Response snapshot

### System Architecture (Target State)
*   **Microservices**: Split the backend into a Core Monolith (Auth, Shared) and 6 Agent Services (Triage, Concepts, etc.).
*   **Communication**: Dapr Sidecars for service invocation and Pub/Sub (Kafka).
*   **Deployment**: Kubernetes manifests for all components.

### Skills Design Strategy
To achieve "functional exactness" and autonomous build:

1.  **`backend-core-gen`**:
    *   **Goal**: Regenerate the monolithic FastAPI core.
    *   **Mechanism**: Script contains exact file contents for `routers/`, `services/`, and `database/`.
2.  **`fastapi-dapr-agent`**:
    *   **Goal**: Generate specialized microservices.
    *   **Mechanism**: A master generator script (`generate_complete_agent.py`) holding logic/code for all 6 agent types.
3.  **`nextjs-production-gen`**:
    *   **Goal**: Build the Next.js frontend.
    *   **Mechanism**: Script populates pages, components, and libraries.
4.  **`k8s-manifest-gen`**:
    *   **Goal**: Create deployment YAMLs.
    *   **Mechanism**: Dictionary-based generation of Deployments, Services, ConfigMaps.
5.  **`emberlearn-build-all`**:
    *   **Goal**: Orchestrate the sequence.
    *   **Mechanism**: Calls the above skills in order: Root -> Shared -> Models -> Core -> Agents -> Frontend -> Manifests.

## Outcome

- ✅ Impact: A clear blueprint for the Skills Library. We are moving from generic templates to specific, content-rich generator scripts.
- 🧪 Tests: N/A
- 📁 Files: Planned structure for `.claude/skills/`
- 🔁 Next prompts: "Break down the implementation into specific tasks"
- 🧠 Reflection: This plan prioritizes *reliability* over *flexibility*. By embedding the exact "Gold Standard" code into the skills, we ensure the AI can reproduce a known-good state every time.

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A