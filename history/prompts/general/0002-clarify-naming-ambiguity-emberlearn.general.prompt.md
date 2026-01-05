---
id: 0002
title: Clarify naming ambiguity EmberLearn
stage: general
date: 2026-01-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: kk
command: user-clarification
labels: ["naming", "clarification", "constitution-update", "emberlearn", "learnflow"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
  - CLAUDE.md
tests:
  - none
---

## Prompt

User identified ambiguity: "I see something ambiguous, The main project name is 'EmberLearn' but there are different names like 'learnflow' and 'skills_library'"

Context: After creating constitution and CLAUDE.md, user noticed naming inconsistency between:
- EmberLearn (current repository name)
- LearnFlow (application name mentioned in hackathon doc)
- skills-library and learnflow-app (repository names in documentation)

User clarified via AskUserQuestion:
1. **EmberLearn relation**: EmberLearn = learnflow-app repository (the application)
2. **Rename decision**: Rename "LearnFlow" to "EmberLearn" throughout for consistency
3. **Repository structure**: Two separate repositories - "emberlearn" for app and "skills-library" for skills

## Response snapshot

**Clarified Naming Convention**:
- **EmberLearn**: The AI-powered Python tutoring application (renamed from LearnFlow)
- **skills-library**: Separate repository containing 7+ reusable Skills
- **Repository Structure**: Two separate repositories for Hackathon III submission

**Documents Updated**:

**1. Constitution v1.0.0 → v1.0.1 (PATCH)**:
- Renamed all instances of "LearnFlow" to "EmberLearn" (7 occurrences)
- Updated SYNC IMPACT REPORT with v1.0.1 changes
- Clarified repository structure in rationale section:
  ```
  Repository Structure:
  - skills-library: Separate repository containing 7+ reusable Skills
  - EmberLearn: This repository - the AI-powered Python tutoring platform application
  ```
- Updated "LearnFlow Application Stack" → "EmberLearn Application Stack"
- Updated "LearnFlow MUST implement 6 specialized AI agents" → "EmberLearn MUST implement..."
- Updated evaluation criteria: "LearnFlow Completion" → "EmberLearn Completion"
- Updated submission requirements: "Repository 2: learnflow-app" → "Repository 2: EmberLearn (this repository)"

**2. CLAUDE.md**:
- Updated Project Context: "The EmberLearn application" (was LearnFlow)
- Updated Deliverables: "EmberLearn repository (this repo)" instead of "learnflow-app repository"
- Updated section header: "EmberLearn Application Requirements" (was LearnFlow)
- Updated Hackathon Submission Checklist: "Repository 2: EmberLearn (this repository)" with clearer description
- Updated evaluation criteria reference: "EmberLearn Completion: 15%"

**Version Bump Rationale**:
- PATCH version (1.0.1) because only naming consistency changes
- No principle modifications
- No structural changes to governance
- Semantic versioning: MAJOR.MINOR.PATCH

## Outcome

- ✅ Impact: Eliminated naming ambiguity. All documentation now consistently uses "EmberLearn" for the application. Clear separation: skills-library (separate repo) vs EmberLearn (this repo, the application).
- 🧪 Tests: N/A - Documentation updates only
- 📁 Files: Updated constitution v1.0.1 and CLAUDE.md (7 replacements in constitution, 7 replacements in CLAUDE.md)
- 🔁 Next prompts: Ready to proceed with /sp.specify for feature specification with clear, unambiguous naming
- 🧠 Reflection: User's observation was critical. Naming ambiguity would have caused confusion throughout development. Now crystal clear: EmberLearn = this repo = the AI tutoring app. skills-library = separate repo = the Skills. Constitution v1.0.1 properly documents this structure.

## Evaluation notes (flywheel)

- Failure modes observed: Initial documentation used hackathon doc naming without clarifying project context
- Graders run and results (PASS/FAIL): Manual review - PASS (all naming consistent, repository structure clear)
- Prompt variant (if applicable): Used AskUserQuestion tool effectively to gather clarification before making changes
- Next experiment (smallest change to try): None needed - naming now consistent across all documentation
