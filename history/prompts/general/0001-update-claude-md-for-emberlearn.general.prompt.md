---
id: 0001
title: Update CLAUDE.md for EmberLearn
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: kk
command: user-request
labels: ["claude-md", "agent-guidance", "hackathon-iii", "skills", "documentation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - CLAUDE.md
tests:
  - none
---

## Prompt

User requested: "Update @CLAUDE.md file for this project"

Context: After creating the EmberLearn constitution (v1.0.0) with 8 core principles focused on Skills with MCP Code Execution, the user requested to update the CLAUDE.md agent guidance file to align with the project-specific requirements.

The existing CLAUDE.md was a generic template. It needed to be customized for:
- Hackathon III specific context and goals
- Skills-driven development workflow
- MCP Code Execution pattern implementation
- Cross-agent compatibility (Claude Code + Goose)
- LearnFlow application requirements
- EmberLearn project structure

## Response snapshot

Updated CLAUDE.md with comprehensive project-specific guidance including:

**Project Context**:
- Specialization in Skills-Driven Development with MCP Code Execution
- Critical understanding: Skills are the product, not application code
- Hackathon III mission and deliverables (2 repositories)
- Evaluation focus on autonomous execution

**Core Guarantees** (6 sections):
1. Skills Are The Product - Every capability as reusable Skill, agentic workflow
2. Token Efficiency First - 80-98% reduction via Skills + Scripts pattern
3. MCP Code Execution Pattern - SKILL.md + scripts/ + REFERENCE.md structure
4. Cross-Agent Compatibility - AAIF standard, test on both Claude Code and Goose
5. Prompt History Records (PHRs) - Record every user input
6. Architectural Decision Records (ADRs) - Suggest for significant decisions

**Skills Development Workflow** (7 steps):
1. Understand the Need
2. Design for Autonomy (prereqs, validation, error handling, idempotency)
3. Implement MCP Code Execution Pattern
4. Write SKILL.md (AAIF Format with complete template)
5. Create Executable Scripts
6. Test Cross-Agent Compatibility
7. Document in REFERENCE.md

**Required Skills**: Listed 7 minimum skills (agents-md-gen, kafka-k8s-setup, postgres-k8s-setup, fastapi-dapr-agent, mcp-code-execution, nextjs-k8s-deploy, docusaurus-deploy)

**LearnFlow Application Requirements**:
- Complete tech stack specifications (Next.js, FastAPI, Kafka, Dapr, etc.)
- 6 AI agents with OpenAI Agents SDK
- Agent implementation pattern (FastAPI + Dapr + Kafka pub/sub)
- Mastery calculation formula
- Code execution sandbox rules

**Default Policies**:
- Human as Tool Strategy (4 invocation triggers)
- Code Standards (no hardcoded secrets, smallest diff, cloud-native patterns)
- Security Standards (JWT RS256, K8s Secrets, PII tokenization)
- Execution Contract (6 steps for every request)

**Architect Guidelines**:
- 9-point planning checklist
- ADR significance test (Impact, Alternatives, Scope)

**Project Structure**: Complete directory tree showing .claude/skills/, .specify/, specs/, history/

**Hackathon Submission Checklist**:
- Repository 1: skills-library (7+ skills, cross-agent tested)
- Repository 2: learnflow-app (built via Skills, 6 agents functional)
- Evaluation criteria breakdown (100 points)

**Key Reminders**: 7 emoji-marked reminders for critical concepts (Skills as product, token efficiency, cross-agent, autonomous execution, documentation, cloud-native, security)

**Constitution Reference**: Links to constitution v1.0.0 and lists 8 core principles

## Outcome

- ✅ Impact: Agent guidance file now project-specific. Provides clear workflow for Skills development, LearnFlow requirements, and hackathon submission criteria. Every interaction will reference these guidelines.
- 🧪 Tests: N/A - Documentation file
- 📁 Files: Updated CLAUDE.md (356 lines) with comprehensive EmberLearn-specific guidance
- 🔁 Next prompts: Ready for feature specification (/sp.specify) to define specific implementation requirements
- 🧠 Reflection: CLAUDE.md now serves as operational handbook for Skills development. Includes concrete templates (SKILL.md format), required deliverables (7 skills), tech stack details (for LearnFlow), and evaluation criteria. Agent now has complete context for autonomous Skills creation.

## Evaluation notes (flywheel)

- Failure modes observed: None - CLAUDE.md update successful
- Graders run and results (PASS/FAIL): Manual review - PASS (comprehensive, project-specific, actionable guidance)
- Prompt variant (if applicable): N/A - Direct user request
- Next experiment (smallest change to try): None needed - proceed to specification phase
