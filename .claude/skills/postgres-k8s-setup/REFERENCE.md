# PostgreSQL Kubernetes Setup - Reference

## Overview

This skill deploys PostgreSQL on Kubernetes using the Bitnami Helm chart with Alembic migration support for schema management.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │              PostgreSQL Primary                  │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │         EmberLearn Database             │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │   │
│  │  │  │  users  │ │ topics  │ │progress │   │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘   │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │   │
│  │  │  │exercises│ │ quizzes │ │ alerts  │   │   │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘   │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                    ┌─────┴─────┐                        │
│                    │    PVC    │                        │
│                    │  (8Gi)    │                        │
│                    └───────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_NAMESPACE` | `default` | Kubernetes namespace |
| `POSTGRES_RELEASE` | `postgresql` | Helm release name |
| `POSTGRES_DATABASE` | `emberlearn` | Database name |
| `POSTGRES_USERNAME` | `emberlearn` | Database user |
| `POSTGRES_PASSWORD` | `emberlearn` | Database password |

### Connection String

```
postgresql+asyncpg://emberlearn:emberlearn@postgresql.default.svc.cluster.local:5432/emberlearn
```

## Database Schema

### Tables (10 total)

1. **users** - Student, teacher, admin accounts
2. **topics** - 8 Python curriculum modules
3. **progress** - Per-student mastery scores
4. **exercises** - Coding challenges
5. **test_cases** - Exercise validation criteria
6. **exercise_submissions** - Student attempts
7. **quizzes** - Multiple-choice assessments
8. **quiz_attempts** - Quiz scores
9. **struggle_alerts** - Teacher notifications

### Mastery Calculation Trigger

The database includes a PostgreSQL trigger that automatically calculates mastery scores:

```sql
mastery_score = (
    exercise_score * 0.4 +    -- 40% weight
    quiz_score * 0.3 +        -- 30% weight
    code_quality_score * 0.2 + -- 20% weight
    streak_bonus * 0.1        -- 10% weight (max 10 days)
)
```

## Alembic Migrations

### Migration Files

```
backend/database/migrations/versions/
├── 001_initial_schema.py    # All 10 tables
├── 002_seed_topics.py       # 8 Python topics
└── 003_mastery_triggers.py  # Auto-calculation triggers
```

### Running Migrations

```bash
# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Generate new migration
alembic revision --autogenerate -m "description"
```

## Troubleshooting

### Connection Issues

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=postgresql

# Port forward for local access
kubectl port-forward svc/postgresql 5432:5432

# Connect with psql
psql -h localhost -U emberlearn -d emberlearn
```

### Migration Failures

```bash
# Check migration status
alembic current

# Show migration history
alembic history

# Force specific revision
alembic stamp head
```

## Backup and Restore

```bash
# Backup
kubectl exec postgresql-0 -- pg_dump -U emberlearn emberlearn > backup.sql

# Restore
kubectl exec -i postgresql-0 -- psql -U emberlearn emberlearn < backup.sql
```

## Performance Tuning

### For Development
- 256Mi memory request
- 8Gi storage
- Single replica

### For Production
- Use Neon serverless PostgreSQL
- Enable connection pooling (PgBouncer)
- Configure read replicas
- Enable automated backups
