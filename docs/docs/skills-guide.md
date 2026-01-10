---
sidebar_position: 3
---

# Skills Guide

Skills are the primary deliverable for Hackathon III. This guide explains the MCP Code Execution pattern and how to use EmberLearn's 7 Skills.

## What Are Skills?

Skills are reusable AI agent capabilities that enable **autonomous execution** of complex tasks. A single prompt like "Deploy Kafka on Kubernetes" triggers a complete deployment with zero manual intervention.

## MCP Code Execution Pattern

The key innovation is separating **instructions** from **implementation**:

```
.claude/skills/<skill-name>/
├── SKILL.md              # ~100 tokens: WHAT to do (loaded into context)
├── scripts/              # 0 tokens: HOW to do it (executed outside context)
│   ├── deploy.sh
│   ├── verify.py
│   └── rollback.sh
└── REFERENCE.md          # On-demand: Deep documentation
```

### Why This Pattern?

| Approach | Context Tokens | Problem |
|----------|----------------|---------|
| Direct MCP | 3,000-5,000 | Tool definitions bloat context |
| Skills + Scripts | 100-150 | Instructions only, scripts execute externally |

**Result**: 79% token efficiency (798 vs 3,800 tokens across 7 Skills)

## Token Efficiency Results

| Skill | Context Tokens | Direct MCP (est.) | Savings |
|-------|----------------|-------------------|---------|
| agents-md-gen | 93 | 300 | 69% |
| kafka-k8s-setup | 111 | 800 | 86% |
| postgres-k8s-setup | 104 | 600 | 83% |
| fastapi-dapr-agent | 119 | 500 | 76% |
| mcp-code-execution | 114 | 400 | 72% |
| nextjs-k8s-deploy | 122 | 700 | 83% |
| docusaurus-deploy | 135 | 500 | 73% |
| **TOTAL** | **798** | **3,800** | **79%** |

## Cross-Agent Compatibility

All Skills use the **AAIF (Agentic AI Foundation)** standard:

```yaml
---
name: skill-identifier
description: What this does and when to use it
allowed-tools: Bash, Read  # Optional restrictions
---
```

### Tested Agents
- **Claude Code**: Full compatibility
- **Goose**: Full compatibility

Skills work because they use universal tools (Bash, Python, kubectl) rather than proprietary APIs.

## The 7 Skills

### 1. agents-md-gen
Generate AGENTS.md files for AI agent guidance.

```bash
# Trigger
"Generate AGENTS.md for this repository"

# What it does
1. Analyzes repository structure
2. Identifies conventions and patterns
3. Generates comprehensive AGENTS.md
```

### 2. kafka-k8s-setup
Deploy Kafka on Kubernetes via Bitnami Helm.

```bash
# Trigger
"Deploy Kafka on Kubernetes"

# What it does
1. Checks prerequisites (kubectl, helm, minikube)
2. Installs Bitnami Kafka Helm chart
3. Creates 8 EmberLearn topics
4. Verifies all brokers running
5. Tests pub/sub functionality
```

### 3. postgres-k8s-setup
Deploy PostgreSQL with Alembic migrations.

```bash
# Trigger
"Deploy PostgreSQL on Kubernetes"

# What it does
1. Installs PostgreSQL Helm chart
2. Runs Alembic migrations
3. Verifies all 10 tables exist
4. Seeds initial topic data
```

### 4. fastapi-dapr-agent
Scaffold FastAPI + Dapr + OpenAI Agent microservices.

```bash
# Trigger
"Create a new AI agent service"

# What it does
1. Scaffolds FastAPI project structure
2. Configures Dapr sidecar annotations
3. Sets up OpenAI Agents SDK integration
4. Creates K8s deployment manifests
```

### 5. mcp-code-execution
Implement MCP with code execution pattern.

```bash
# Trigger
"Create a new Skill with MCP pattern"

# What it does
1. Creates SKILL.md with AAIF format
2. Scaffolds scripts/ directory
3. Creates REFERENCE.md template
4. Measures token efficiency
```

### 6. nextjs-k8s-deploy
Deploy Next.js + Monaco Editor to Kubernetes.

```bash
# Trigger
"Deploy Next.js frontend to Kubernetes"

# What it does
1. Scaffolds Next.js 15 project
2. Configures Monaco Editor (SSR disabled)
3. Creates Dockerfile for production
4. Deploys to Kubernetes
```

### 7. docusaurus-deploy
Deploy documentation site via Skill.

```bash
# Trigger
"Generate and deploy documentation"

# What it does
1. Scans codebase for README files
2. Creates Docusaurus configuration
3. Builds static site
4. Deploys to Kubernetes
```

## Using Skills

### Installation
Copy Skills to your Claude Code configuration:

```bash
cp -r .claude/skills/* ~/.claude/skills/
```

### Invocation
Skills are triggered by natural language matching the `description` field:

```
User: "Deploy Kafka on Kubernetes"
Claude: [Matches kafka-k8s-setup, executes scripts]
```

### Creating New Skills

1. Create directory: `.claude/skills/<skill-name>/`
2. Write SKILL.md with AAIF frontmatter
3. Create executable scripts in `scripts/`
4. Add REFERENCE.md for deep documentation
5. Test with both Claude Code and Goose

## Best Practices

1. **Keep SKILL.md concise** (~100 tokens)
2. **Scripts do the work** - all logic in scripts/
3. **Validate prerequisites** - check before executing
4. **Verify success** - always include verification step
5. **Support rollback** - enable recovery from failures
6. **Test cross-agent** - verify on multiple AI agents
