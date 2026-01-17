---
id: 0001
title: Create EmberLearn Constitution
stage: constitution
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: kk
command: /sp.constitution
labels: ["constitution", "hackathon-iii", "skills", "mcp-code-execution", "aaif"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

User executed: /sp.constitution

Context: After deep research on Hackathon III requirements (Reusable Intelligence and Cloud-Native Mastery), the user requested constitution creation for the EmberLearn project. This project focuses on:
1. Building Skills with MCP Code Execution pattern (the product)
2. Creating LearnFlow application (the demonstration) using those Skills
3. Following AAIF open standards for cross-agent compatibility
4. Achieving 80-98% token efficiency through Skills + Scripts pattern

Research completed:
- MCP Code Execution pattern (98.7% token reduction: 150k → 2k tokens)
- AAIF Standards and Skills format (December 2025 open standard)
- Skills cross-agent compatibility (Claude Code, Goose, OpenAI Codex)
- LearnFlow architecture (6 AI agents with OpenAI Agents SDK, Kafka, Dapr, K8s)
- Technical stack (Next.js + Monaco, FastAPI, Neon PostgreSQL, Kong, Argo CD)
- Evaluation criteria (100 points across 8 categories)

## Response snapshot

Created comprehensive constitution (v1.0.0) with 8 core principles:

**I. Skills Are The Product** - Skills are the deliverable, not application code. Judges test for autonomous execution.

**II. Token Efficiency First** - Skills + Scripts pattern: SKILL.md (~100 tokens) → scripts/ (0 tokens, executed) → minimal result. Target: 80-98% reduction vs direct MCP.

**III. Cross-Agent Compatibility** - AAIF open standard. Must work on Claude Code AND Goose. Universal tools only.

**IV. Autonomous Execution** - Single prompt to complete deployment. Zero manual intervention. Includes validation, prerequisites, error handling, idempotency.

**V. Cloud-Native Architecture** - Event-driven (Kafka), Dapr sidecars, stateless services, Kubernetes-native patterns.

**VI. MCP Code Execution Pattern** - Core innovation: wrap MCP servers in scripts. SKILL.md + scripts/ + REFERENCE.md structure.

**VII. Test-Driven Development** - Skills must include validation scripts. Integration/contract/E2E tests for application.

**VIII. Spec-Driven Development** - Spec-Kit Plus framework. Constitution → Spec → Plan → Tasks. ADRs for significant decisions.

Additional sections:
- **Skills Development Standards**: SKILL.md format (AAIF), required 7 skills, quality standards
- **Architecture Requirements**: LearnFlow tech stack, 6 AI agents (OpenAI Agents SDK), mastery calculation, struggle detection, sandbox security
- **Security Standards**: JWT auth, secrets management, data privacy
- **Governance**: Amendment process, compliance review, hackathon submission requirements, evaluation criteria (100 points)

Constitution includes:
- Sync Impact Report (HTML comment documenting version, changes, template status)
- Complete SKILL.md template with YAML frontmatter
- Detailed agent architecture with Kafka topics
- Mastery calculation formula and levels
- Submission requirements for both repositories
- Evaluation rubric with gold standards

## Outcome

- ✅ Impact: Foundation document created. Establishes principles for entire hackathon project. All subsequent artifacts (spec, plan, tasks) will reference and comply with this constitution.
- 🧪 Tests: N/A - Constitution is governance document, not executable code
- 📁 Files: Created `.specify/memory/constitution.md` (v1.0.0, 334 lines)
- 🔁 Next prompts: Ready for `/sp.specify` to create feature specification for Hackathon III implementation
- 🧠 Reflection: Constitution comprehensively captures all research findings. Eight principles directly map to evaluation criteria (especially Skills Autonomy, Token Efficiency, Cross-Agent Compatibility). Architecture section provides concrete technical requirements for LearnFlow. Ready to proceed with spec creation.

## Evaluation notes (flywheel)

- Failure modes observed: None - Constitution creation successful on first attempt
- Graders run and results (PASS/FAIL): Manual review - PASS (all placeholders filled, no bracket tokens remaining, version properly set, dates ISO format, principles testable)
- Prompt variant (if applicable): N/A - Standard /sp.constitution command
- Next experiment (smallest change to try): None needed - proceed to /sp.specify for feature specification
