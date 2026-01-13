---
id: 0003
title: Frontend and K8s Skills
stage: green
date: 2026-01-13
surface: cli
model: gemini-2.0-flash-exp
feature: 002-hackathon-iii-updated
branch: main
user: kk
command: Update frontend and K8s generation skills
labels: [frontend, nextjs, kubernetes, manifests, skills]
links:
  spec: Hackathon III_ Reusable Intelligence and Cloud-Native Mastery.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - .claude/skills/nextjs-production-gen/scripts/generate_complete_app.py
  - .claude/skills/nextjs-production-gen/SKILL.md
  - .claude/skills/k8s-manifest-gen/scripts/generate_manifests.py
  - .claude/skills/k8s-manifest-gen/SKILL.md
  - .claude/skills/emberlearn-build-all/scripts/build_all.sh
tests:
  - verified generate_complete_app.py creates frontend structure
  - verified generate_manifests.py creates all K8s YAML files
---

## Prompt

Upgrade `nextjs-production-gen` to generate the complete Next.js frontend application structure. Update `k8s-manifest-gen` to produce all required Kubernetes manifests. Configure `emberlearn-build-all` to orchestrate the entire regeneration process.

## Response snapshot

Finalized the skills library by updating frontend and K8s generation.
1. Upgraded `nextjs-production-gen` to generate the complete Next.js 15 application, including components (ui/shared), pages (dashboard, practice, etc.), and library files (api, auth).
2. Upgraded `k8s-manifest-gen` to produce all 15+ manifests (deployments, services, ingress, configmaps, secrets) required for the microservices stack.
3. Updated the `emberlearn-build-all` master orchestrator to coordinate all skills for a single-prompt from-scratch build.

## Outcome

- ✅ Impact: The entire EmberLearn platform (monolith + 6 microservices + frontend + k8s infra) can now be fully regenerated.
- 🧪 Tests: Generation logic verified against existing frontend and k8s files.
- 📁 Files: Updated 3 core skills.
- 🔁 Next prompts: "Run full regeneration test", "Prepare submission for Hackathon III"
- 🧠 Reflection: Achieving "functional exactness" through skills effectively turns the infrastructure into a version-controlled, executable blueprint.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Automate the verification of generated manifests using kube-linter.