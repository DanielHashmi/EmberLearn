---
name: fastapi-dapr-agent
description: Generate complete FastAPI + Dapr + OpenAI Agents SDK microservices with full production features including tools, handoffs, Kafka integration, and health checks
---

# FastAPI Dapr Agent Generator

## When to Use
- Generate complete AI agent microservices
- Create production-ready FastAPI + OpenAI Agents SDK services
- Build agents with Dapr sidecars and Kafka pub/sub

## Instructions
1. `python scripts/generate_complete_agent.py <type>` where type is: triage, concepts, code_review, debug, exercise, or progress
2. Output: Complete agent service with main.py, Dockerfile, requirements.txt

## Output
- Full FastAPI application with OpenAI Agents SDK
- Complete API endpoints matching contracts
- Kafka event publishing via Dapr
- Structured logging with correlation IDs
- Health and readiness checks
- Production-ready Dockerfile
- Minimal output: "✓ Generated complete [AgentName]"

See [REFERENCE.md](./REFERENCE.md) for agent patterns and customization.
