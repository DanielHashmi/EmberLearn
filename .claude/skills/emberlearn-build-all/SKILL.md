---
name: emberlearn-build-all
description: Master orchestrator that autonomously builds the complete EmberLearn application from scratch using all Skills
---

# EmberLearn Build All Orchestrator

## When to Use
- Build complete EmberLearn application from scratch
- Coordinate all Skills to generate and deploy the entire system
- Single prompt → Complete working application

## Instructions
1. `bash scripts/build_all.sh` - Orchestrates complete build and deployment

## What This Does
This master Skill coordinates all other Skills to autonomously:
1. Generate database models (database-schema-gen)
2. Generate shared utilities (shared-utils-gen)
3. Generate all 6 AI agents (fastapi-dapr-agent)
4. Generate complete frontend (nextjs-frontend-gen)
5. Deploy infrastructure (kafka-k8s-setup, postgres-k8s-setup)
6. Deploy Dapr control plane (dapr-deploy)
7. Generate K8s manifests (k8s-manifest-gen)
8. Deploy all services to Kubernetes

## Output
- Complete EmberLearn application deployed and running
- All 6 AI agents operational
- Frontend accessible
- Infrastructure ready
- Minimal output: "✓ EmberLearn built and deployed"

See [REFERENCE.md](./REFERENCE.md) for customization options.
