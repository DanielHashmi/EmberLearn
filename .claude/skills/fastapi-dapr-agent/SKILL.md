---
name: fastapi-dapr-agent
description: Scaffold FastAPI + Dapr + OpenAI Agent microservices
---

# FastAPI Dapr Agent

## When to Use
- Create AI agent service
- Scaffold backend agents

## Instructions
1. `python scripts/scaffold_agent.py <type>` (triage|concepts|code_review|debug|exercise|progress)
2. `python scripts/generate_k8s_manifests.py <name> -i <image>`
3. `python scripts/verify_structure.py <agent_dir>`

See [REFERENCE.md](./REFERENCE.md) for agent patterns.
