# Skills Development Guide

This guide explains how to create and use Skills with MCP Code Execution pattern for EmberLearn.

## What Are Skills?

Skills are reusable capabilities that teach AI agents how to perform specific tasks autonomously. They follow the AAIF (Agentic AI Foundation) standard and work across Claude Code, Goose, and OpenAI Codex.

## Skill Structure

Each Skill follows this structure:

```
.claude/skills/<skill-name>/
├── SKILL.md              # Instructions (~100 tokens)
├── scripts/              # Executable scripts (0 tokens in context)
│   ├── check_prereqs.py
│   ├── deploy.sh
│   └── verify.py
└── REFERENCE.md          # Deep documentation (loaded on-demand)
```

## Token Efficiency

The MCP Code Execution pattern dramatically reduces token usage:

| Component | Tokens | Notes |
|-----------|--------|-------|
| SKILL.md | ~100 | Loaded when triggered |
| scripts/ | 0 | Executed, never loaded |
| REFERENCE.md | 0 | Loaded only if needed |
| Output | ~10 | "✓ Deployed successfully" |

**Total: ~110 tokens vs 50,000+ with direct MCP**

## Creating a Skill

### 1. SKILL.md Template

```yaml
---
name: my-skill
description: What this skill does
allowed-tools: Bash, Read
---

# My Skill

## When to Use
- User asks to [trigger condition]
- Setting up [use case]

## Instructions
1. Run prerequisite check: `./scripts/check_prereqs.py`
2. Execute deployment: `./scripts/deploy.sh`
3. Verify: `python scripts/verify.py`

## Validation
- [ ] Prerequisites met
- [ ] Deployment successful
- [ ] Verification passed

See [REFERENCE.md](./REFERENCE.md) for configuration options.
```

### 2. Scripts

Scripts should:
- Be executable without modification
- Validate prerequisites before execution
- Return minimal, structured output
- Handle errors gracefully

### 3. REFERENCE.md

Include:
- Configuration options
- Environment variables
- Troubleshooting guide
- Examples and use cases

## EmberLearn Skills

### Available Skills

1. **agents-md-gen** - Generate AGENTS.md files
2. **kafka-k8s-setup** - Deploy Kafka on Kubernetes
3. **postgres-k8s-setup** - Deploy PostgreSQL on Kubernetes
4. **fastapi-dapr-agent** - Create FastAPI + Dapr services
5. **mcp-code-execution** - Implement MCP pattern
6. **nextjs-k8s-deploy** - Deploy Next.js applications
7. **docusaurus-deploy** - Deploy documentation sites

### Using Skills

**With Claude Code:**
```bash
claude "Deploy Kafka using kafka-k8s-setup skill"
```

**With Goose:**
```bash
goose "Use kafka-k8s-setup to deploy Kafka"
```

## Best Practices

1. **Keep SKILL.md minimal** - Under 500 lines, ~100 tokens
2. **Scripts do the work** - All logic in scripts, not instructions
3. **Validate everything** - Check prerequisites and verify results
4. **Handle failures** - Include rollback scripts where applicable
5. **Test cross-agent** - Verify on both Claude Code and Goose
