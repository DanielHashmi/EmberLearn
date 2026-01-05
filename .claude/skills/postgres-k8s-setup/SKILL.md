---
name: postgres-k8s-setup
description: Deploy PostgreSQL on Kubernetes with Alembic migrations
---

# PostgreSQL Kubernetes Setup

## When to Use
- Deploy PostgreSQL database
- Run database migrations

## Instructions
1. `./scripts/check_prereqs.sh`
2. `./scripts/deploy_postgres.sh`
3. `python scripts/run_migrations.py`
4. `python scripts/verify_schema.py`

See [REFERENCE.md](./REFERENCE.md) for schema details.
