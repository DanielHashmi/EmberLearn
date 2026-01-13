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
1. Regenerate into a fresh directory (recommended):
   - `OUTPUT_DIR=./_regen/test MODE=both DEPLOY_K8S=0 bash scripts/build_all.sh`

   Note: in bash you must prefix env vars *before* the command (the example above is correct).
2. (Optional) Also regenerate selected artifacts from specs using Skills:
   - `OUTPUT_DIR=./_regen/test MODE=both REGENERATE=1 bash scripts/build_all.sh`
3. (Optional) Deploy the K8s stack (requires minikube/helm/kubectl/docker):
   - `OUTPUT_DIR=./_regen/k8s MODE=both DEPLOY_K8S=1 bash scripts/build_all.sh`

   If you need to set variables in the current shell first:
   - `export OUTPUT_DIR=...; export MODE=both; export DEPLOY_K8S=0; bash scripts/build_all.sh`

The script includes a verification step (`scripts/verify_regeneration.py`).

## What This Does
This master Skill regenerates the *current* EmberLearn working project into a fresh output directory.

- Default (`REGENERATE=0`): copies the working project for functional exactness.
- Optional (`REGENERATE=1`): also regenerates selected artifacts from specs using Skills.

When enabled, it can coordinate other Skills to:
1. Generate database models (database-schema-gen)
2. Generate shared API models (shared-utils-gen)
3. Generate agent microservices (fastapi-dapr-agent)
4. Generate production frontend (nextjs-production-gen)
5. Generate docs site (docusaurus-deploy)
6. Generate K8s manifests (k8s-manifest-gen)
7. (Optional) Deploy infra + services to Kubernetes (kafka-k8s-setup, postgres-k8s-setup, dapr-deploy)

## Output
- Regenerated EmberLearn project under `OUTPUT_DIR`
- Verification status line: `✓ verify passed` (or a single failure line)
- Minimal output: `✓ EmberLearn regenerated`

If `DEPLOY_K8S=1`, the script will also attempt Kubernetes deployment.

See [REFERENCE.md](./REFERENCE.md) for customization options.
