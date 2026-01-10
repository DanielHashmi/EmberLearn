---
name: dapr-deploy
description: Deploy Dapr control plane to Kubernetes cluster with sidecar injection and component configurations
---

# Dapr Deployment Skill

## When to Use
- Deploy Dapr control plane to Kubernetes
- Configure Dapr components (state stores, pub/sub)
- Enable sidecar injection for microservices

## Instructions
1. `bash scripts/deploy_dapr.sh` - Deploys Dapr control plane via Helm
2. `bash scripts/configure_components.sh` - Creates Dapr component configurations
3. `python scripts/verify_dapr.py` - Validates Dapr installation and components

## Output
- Dapr control plane deployed to `dapr-system` namespace
- Dapr components configured (state store, pub/sub)
- Sidecar injection enabled
- Minimal output: "✓ Dapr deployed and configured"

See [REFERENCE.md](./REFERENCE.md) for configuration options and troubleshooting.
