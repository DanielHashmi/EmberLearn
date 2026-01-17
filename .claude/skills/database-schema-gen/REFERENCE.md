# Database Schema Generator - Reference

## Purpose

Automatically generates SQLAlchemy ORM models and Alembic migrations from data-model.md specifications, eliminating manual model writing and ensuring consistency between documentation and code.

## Data Model Format

### Expected Structure

```markdown
## 1. EntityName

**Purpose**: Brief description

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTO INCREMENT | ... |
| `name` | VARCHAR(255) | NOT NULL | ... |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | ... |
```

### Supported SQL Types

- **INTEGER**, **INT** → `sqlalchemy.Integer`
- **VARCHAR(n)** → `sqlalchemy.String(n)`
- **TEXT** → `sqlalchemy.Text`
- **TIMESTAMP**, **DATETIME** → `sqlalchemy.DateTime`
- **UUID** → `sqlalchemy.dialects.postgresql.UUID`
- **BOOLEAN**, **BOOL** → `sqlalchemy.Boolean`
- **DECIMAL**, **NUMERIC** → `sqlalchemy.Numeric`
- **FLOAT** → `sqlalchemy.Float`
- **ENUM('a','b','c')** → `sqlalchemy.Enum('a','b','c')`

### Supported Constraints

- **PRIMARY KEY** → `primary_key=True`
- **UNIQUE** → `unique=True`
- **NOT NULL** → `nullable=False`
- **AUTO INCREMENT** → `autoincrement=True`
- **DEFAULT value** → `default=value` or `server_default`
- **FOREIGN KEY REFERENCES table(col)** → `ForeignKey('table.col')`

## Generated Code Structure

```
backend/
├── database/
│   ├── models.py              # All SQLAlchemy models
│   └── migrations/
│       ├── env.py             # Alembic environment
│       ├── script.py.mako     # Migration template
│       └── versions/
│           └── 001_initial_schema.py
└── alembic.ini                # Alembic configuration
```

## Usage Examples

### Generate from EmberLearn data model

```bash
python scripts/generate_models.py specs/001-hackathon-iii/data-model.md
python scripts/generate_migrations.py
```

### Generated Model Example

```python
class User(Base):
    """
    Students, teachers, and admins with authentication and profile data.
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(UUID, nullable=False, unique=True, server_default=text('gen_random_uuid()'))
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('student', 'teacher', 'admin', name='role_enum'), nullable=False, default='student')
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now())
    last_login_at = Column(DateTime, nullable=True)
```

## Token Efficiency

**Without Skill** (manual coding):
- Context: ~10,000 tokens (reading docs, planning models, writing code)
- Total: ~10,000 tokens

**With Skill** (MCP Code Execution):
- SKILL.md: ~100 tokens
- Scripts: 0 tokens (executed outside context)
- Result: ~10 tokens ("✓ Generated 10 models")
- Total: ~110 tokens

**Reduction**: ~99% (10,000 → 110 tokens)

## Troubleshooting

### Issue: Type mapping not recognized

**Symptom**: Unknown SQL type defaults to `String(255)`

**Solution**: Add type mapping in `map_sql_type_to_sqlalchemy()` function

### Issue: Constraints not parsed correctly

**Symptom**: Missing primary keys or foreign keys

**Solution**: Check constraint format matches regex patterns in `parse_constraints()`

### Issue: Migration autogenerate doesn't detect changes

**Symptom**: `alembic revision --autogenerate` creates empty migration

**Solution**: Verify `target_metadata = Base.metadata` in `env.py` and models are imported

## Extension Points

### Add Custom Types

Edit `map_sql_type_to_sqlalchemy()`:

```python
elif 'JSONB' in sql_type:
    return 'JSONB'
```

### Add Relationships

Extend `generate_sqlalchemy_model()` to detect foreign keys and generate `relationship()` mappings:

```python
# Auto-detect relationships from foreign keys
if constraints['foreign_key']:
    related_table, related_col = constraints['foreign_key']
    code += f"    {related_table}_rel = relationship('{related_table.capitalize()}')\n"
```

### Add Indexes

Parse index specifications from data-model.md and generate:

```python
__table_args__ = (
    Index('idx_user_email', 'email'),
    Index('idx_user_uuid', 'uuid'),
)
```

## Best Practices

1. **Single Source of Truth**: data-model.md is authoritative. Never manually edit models.py.
2. **Regenerate on Changes**: Re-run generator whenever data-model.md is updated.
3. **Review Migrations**: Always review auto-generated migrations before applying.
4. **Test First**: Generate models in test environment before production.
5. **Version Control**: Commit both data-model.md changes and generated code together.

## Integration with Other Skills

- **postgres-k8s-setup**: Deploys database where these models will run
- **fastapi-dapr-agent**: Agent services import these models for data access
- **shared-utils-gen**: Generates Pydantic schemas that mirror these SQLAlchemy models
