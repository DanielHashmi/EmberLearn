# AGENTS.md Generator - Reference

## Overview

This skill generates comprehensive AGENTS.md files following the AAIF (Agentic AI Foundation) standard, providing guidance for AI coding agents working with repositories.

## AGENTS.md Format

The generated file follows this structure:

```markdown
# AGENTS.md - {Repository Name}

## Overview
- Repository name and description
- Primary languages detected
- Frameworks and tools used
- File statistics

## Project Structure
- Directory tree (top-level)
- Key directories explained

## Coding Conventions
- Language-specific guidelines
- Style preferences
- Naming conventions

## AI Agent Guidelines
- Do's and Don'ts
- Testing requirements
- Documentation standards
```

## Detection Capabilities

### Languages Detected
- Python (.py)
- TypeScript (.ts, .tsx)
- JavaScript (.js, .jsx)
- Go (.go)
- Rust (.rs)
- Java (.java)
- Ruby (.rb)
- PHP (.php)
- C# (.cs)
- C/C++ (.c, .cpp)
- Swift (.swift)
- Kotlin (.kt)

### Frameworks Detected
- Node.js (package.json)
- Python (pyproject.toml, requirements.txt)
- Next.js (next.config.js)
- Docker (Dockerfile)
- Kubernetes (k8s/, kubernetes/)
- Claude Code Skills (.claude/)
- Alembic (alembic.ini)
- Tailwind CSS (tailwind.config.js)

## Customization

### Adding Custom Sections

Edit the generated AGENTS.md to add project-specific sections:

```markdown
## API Conventions
- REST endpoints follow /api/v1/{resource} pattern
- Use JSON for request/response bodies
- Include correlation IDs in headers

## Database Conventions
- Use Alembic for migrations
- Follow naming: {table}_{column} for foreign keys
- JSONB for flexible schema fields
```

### Excluding Directories

The analyzer automatically excludes:
- `.git/`
- `node_modules/`
- `__pycache__/`
- `.venv/`, `venv/`
- `dist/`, `build/`
- `.next/`

## Integration with Claude Code

AGENTS.md files are automatically read by Claude Code when working with repositories, providing context about:

1. **Project structure** - Where to find different types of files
2. **Conventions** - How to write code that matches existing patterns
3. **Guidelines** - What to do and avoid when making changes

## Best Practices

1. **Keep it concise** - Focus on information AI agents need
2. **Update regularly** - Regenerate after major changes
3. **Add specifics** - Include project-specific conventions
4. **Link to docs** - Reference detailed documentation

## Example Output

```markdown
# AGENTS.md - EmberLearn

## Overview

**Repository**: EmberLearn
**Primary Languages**: Python, TypeScript
**Frameworks/Tools**: FastAPI, Next.js, Kafka, Dapr
**Total Files**: 150

## Project Structure

```
backend/
frontend/
k8s/
.claude/skills/
docs/
```

## Coding Conventions

### Python
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Use async/await for asynchronous code

### TypeScript
- Use strict mode
- Prefer interfaces over type aliases
- Follow React hooks conventions

## AI Agent Guidelines

### Do
- Read existing code before making changes
- Follow established patterns
- Write clear commit messages

### Don't
- Introduce new dependencies without justification
- Make changes outside requested scope
- Hardcode secrets or credentials
```
