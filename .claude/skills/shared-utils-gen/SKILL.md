---
name: shared-utils-gen
description: Generate shared backend utilities including structured logging, correlation middleware, Dapr client helpers, and Pydantic models for FastAPI microservices
---

# Shared Utilities Generator

## When to Use
- Generate foundational backend utilities for microservices
- Set up structured logging with correlation IDs
- Create Dapr client helper functions
- Generate Pydantic models from API contracts

## Instructions
1. Run `python scripts/generate_logging.py` to create structured logging configuration
2. Run `python scripts/generate_middleware.py` to create FastAPI middleware (CORS, correlation IDs)
3. Run `python scripts/generate_dapr_helpers.py` to create Dapr client wrapper functions
4. Run `python scripts/generate_pydantic_models.py <contracts-dir>` to generate Pydantic schemas from OpenAPI

## Output
- `backend/shared/logging_config.py` - structlog + orjson setup
- `backend/shared/correlation.py` - Correlation ID middleware
- `backend/shared/dapr_client.py` - Dapr helper functions
- `backend/shared/models.py` - Pydantic models
- Minimal output: "✓ Generated N shared utilities"

See [REFERENCE.md](./REFERENCE.md) for patterns and best practices.
