# AGENTS.md - EmberLearn Repository

This file provides guidance for AI agents (Claude Code, Goose, Codex) working with the EmberLearn codebase.

## Repository Overview

EmberLearn is an AI-powered Python tutoring platform built for **Hackathon III: Reusable Intelligence and Cloud-Native Mastery**. The project demonstrates Skills-Driven Development with MCP Code Execution pattern.

## Project Structure

```
EmberLearn/
├── .claude/skills/          # 7 Reusable Skills (PRIMARY DELIVERABLE)
│   ├── agents-md-gen/       # Generate AGENTS.md files
│   ├── kafka-k8s-setup/     # Deploy Kafka on Kubernetes
│   ├── postgres-k8s-setup/  # Deploy PostgreSQL with migrations
│   ├── fastapi-dapr-agent/  # Scaffold AI agent microservices
│   ├── mcp-code-execution/  # Create Skills with MCP pattern
│   ├── nextjs-k8s-deploy/   # Deploy Next.js frontend
│   └── docusaurus-deploy/   # Deploy documentation site
├── backend/                 # Python backend services
│   ├── agents/              # 6 AI agent microservices
│   │   ├── triage/          # Query routing agent
│   │   ├── concepts/        # Python concepts explainer
│   │   ├── code_review/     # Code analysis agent
│   │   ├── debug/           # Error debugging agent
│   │   ├── exercise/        # Challenge generator
│   │   └── progress/        # Mastery tracking agent
│   ├── database/            # SQLAlchemy models + Alembic
│   ├── sandbox/             # Secure code execution
│   └── shared/              # Common utilities
├── frontend/                # Next.js 15 + Monaco Editor
├── k8s/                     # Kubernetes manifests
│   ├── agents/              # Agent deployments
│   ├── infrastructure/      # Dapr, Kong, Kafka configs
│   └── sandbox/             # Sandbox deployment
├── docs/                    # Docusaurus documentation
└── specs/                   # Spec-Kit Plus artifacts
```

## Key Conventions

### Skills Development
- Skills are in `.claude/skills/<skill-name>/`
- Each Skill has: `SKILL.md` (instructions), `scripts/` (implementation), `REFERENCE.md` (docs)
- SKILL.md should be ~100 tokens (concise instructions only)
- Scripts execute outside context for token efficiency

### Backend Services
- FastAPI 0.110+ with async endpoints
- OpenAI Agents SDK for AI functionality
- Dapr sidecar for state management and pub/sub
- Structured logging with structlog + orjson
- Pydantic models for request/response validation

### Frontend
- Next.js 15 with App Router
- Monaco Editor with SSR disabled (dynamic import)
- Tailwind CSS for styling
- JWT authentication stored in localStorage

### Kubernetes
- All services deployed to `default` namespace
- Dapr annotations for sidecar injection
- Kong API Gateway for routing and auth
- Resource limits on all containers

## Important Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Agent-specific guidance (this project) |
| `.specify/memory/constitution.md` | Project principles |
| `specs/001-hackathon-iii/tasks.md` | 200 implementation tasks |
| `backend/agents/base_agent.py` | Base class for all agents |
| `backend/agents/agent_factory.py` | OpenAI Agent configuration |
| `frontend/lib/api.ts` | API client for backend |
| `frontend/lib/types.ts` | TypeScript type definitions |

## Coding Standards

### Python
- Type hints on all functions
- Docstrings for public functions
- Use `structlog` for logging
- Async/await for I/O operations
- Pydantic for data validation

### TypeScript
- Strict mode enabled
- Interface-first design
- Use `@/` path alias for imports
- Prefer `const` over `let`

### Commits
- Prefix with agent name: "Claude: implemented X"
- Reference Skills used: "using kafka-k8s-setup skill"
- Keep commits atomic and focused

## Environment Variables

### Backend
- `OPENAI_API_KEY`: OpenAI API key (from K8s Secret)
- `DAPR_HTTP_PORT`: Dapr sidecar port (default: 3500)
- `DATABASE_URL`: PostgreSQL connection string

### Frontend
- `NEXT_PUBLIC_API_URL`: Backend API URL

## Testing

- Skills must be tested on both Claude Code AND Goose
- Token efficiency measured with `mcp-code-execution/scripts/measure_tokens.py`
- Cross-agent compatibility results in `testing/` directory

## Common Tasks

### Deploy Infrastructure
```bash
# Use Skills for autonomous deployment
"Deploy Kafka on Kubernetes"
"Deploy PostgreSQL on Kubernetes"
```

### Create New Agent
```bash
# Use fastapi-dapr-agent Skill
"Create a new AI agent for [purpose]"
```

### Run Frontend Locally
```bash
cd frontend
npm install
npm run dev
```

### Build Documentation
```bash
cd docs
npm install
npm run build
```

## Architecture Decisions

Key decisions documented in `history/adr/`:
- ADR-001: MCP Code Execution pattern for token efficiency
- ADR-002: Dapr for service mesh (state, pub/sub)
- ADR-003: OpenAI Agents SDK for AI functionality
- ADR-004: Kafka for event streaming

## Contact

This project was built for Hackathon III submission.
- Submission form: https://forms.gle/Mrhf9XZsuXN4rWJf7
