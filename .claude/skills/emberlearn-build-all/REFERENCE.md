# EmberLearn Build All - Reference Documentation

## Overview

Master orchestrator Skill that coordinates all other Skills to build the complete EmberLearn application autonomously from a single prompt.

## Build Phases

### Phase 1: Generate Backend Code
1. Database models (database-schema-gen)
2. Shared utilities (shared-utils-gen)
3. All 6 AI agents (fastapi-dapr-agent)

### Phase 2: Generate Frontend Code
1. Complete Next.js app with Monaco Editor (nextjs-frontend-gen)

### Phase 3: Deploy Infrastructure
1. PostgreSQL (postgres-k8s-setup)
2. Kafka (kafka-k8s-setup)
3. Dapr control plane (dapr-deploy)

### Phase 4: Deploy Application
1. Generate K8s manifests (k8s-manifest-gen)
2. Build Docker images
3. Deploy to Kubernetes

### Phase 5: Verify Deployment
1. Wait for pods to be ready
2. Validate services

## Expected Output

- 9 database models
- 4 shared utilities
- 6 AI agents (18 files total)
- Complete Next.js frontend
- All infrastructure deployed
- All services running in Kubernetes

## Token Efficiency

**Total Reduction**: ~98%
- Manual approach: ~100,000 tokens (load all docs, write all code)
- Skill approach: ~2,000 tokens (orchestration only)

## Prerequisites

- Minikube running
- Helm installed
- Docker available
- Python 3.9+
- kubectl configured

## Customization

Edit `build_all.sh` to:
- Skip phases (comment out sections)
- Add custom validation steps
- Deploy to different clusters

## Troubleshooting

**Build fails at Phase 1**: Check Python dependencies
**Infrastructure deployment fails**: Verify Minikube resources (4 CPU, 8GB RAM)
**Pods not starting**: Check Docker images built successfully
**Services not accessible**: Verify ingress configured

## Time to Complete

- Generation: ~30 seconds
- Deployment: ~5 minutes (depends on image pulls)
- Total: ~6 minutes for complete application
