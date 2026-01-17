---
name: database-schema-gen
description: Generate SQLAlchemy models and Alembic migrations from data-model.md specification for PostgreSQL database schema
---

# Database Schema Generator

## When to Use
- Generate SQLAlchemy ORM models from data model specifications
- Create Alembic migration scripts
- Set up database structure for Python applications

## Instructions
1. Run `python scripts/generate_models.py <data-model-path>` to generate SQLAlchemy models
2. Run `python scripts/generate_migrations.py <models-path>` to create Alembic migrations
3. Run `python scripts/verify_schema.py` to validate generated code

## Output
- `backend/database/models.py` - SQLAlchemy ORM models
- `backend/database/migrations/versions/*.py` - Alembic migration files
- Minimal console output: "✓ Generated N models, M migrations"

See [REFERENCE.md](./REFERENCE.md) for data model specification format and SQLAlchemy patterns.
