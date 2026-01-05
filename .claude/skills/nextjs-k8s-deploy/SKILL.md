---
name: nextjs-k8s-deploy
description: Deploy Next.js with Monaco Editor to Kubernetes
---

# Next.js Kubernetes Deploy

## When to Use
- Deploy Next.js frontend
- Setup Monaco Editor

## Instructions
1. `./scripts/scaffold_nextjs.sh <dir>`
2. `python scripts/integrate_monaco.py <dir>`
3. `python scripts/generate_k8s_deploy.py <name> -i <image>`
4. `./scripts/build_and_deploy.sh <dir>`
5. `python scripts/verify_deployment.py <name>`

See [REFERENCE.md](./REFERENCE.md) for SSR config.
