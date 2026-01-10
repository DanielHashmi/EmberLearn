---
name: k8s-manifest-gen
description: Generate complete Kubernetes deployment manifests for all microservices including Deployments, Services, ConfigMaps, Secrets, and Ingress
---

# Kubernetes Manifest Generator

## When to Use
- Generate Kubernetes manifests for microservices
- Create Deployments with Dapr sidecar annotations
- Generate Services, ConfigMaps, Secrets, and Ingress

## Instructions
1. `python scripts/generate_manifests.py <services-spec>` - Generates all K8s manifests
2. Output: Complete manifests in `k8s/` directory

## Output
- Deployment manifests with Dapr annotations
- Service manifests for each microservice
- ConfigMaps for configuration
- Secrets for sensitive data
- Ingress for external access
- Minimal output: "✓ Generated manifests for N services"

See [REFERENCE.md](./REFERENCE.md) for customization options.
