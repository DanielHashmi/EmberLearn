---
name: docusaurus-deploy
description: Generate and deploy Docusaurus documentation sites
---

# Docusaurus Deploy

## When to Use
- Generate documentation site
- Deploy project docs

## Instructions
1. `python scripts/scan_codebase.py`
2. `python scripts/generate_docusaurus_config.py -o docs-site`
3. `python scripts/generate_docs.py -o docs-site`
4. `./scripts/build_and_deploy.sh docs-site . <target>` (local|github-pages|kubernetes)
5. `python scripts/verify_docs.py docs-site`

See [REFERENCE.md](./REFERENCE.md) for customization.
