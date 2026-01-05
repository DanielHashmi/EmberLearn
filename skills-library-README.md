# Skills Library

Reusable AI agent Skills with MCP Code Execution pattern for autonomous cloud-native deployment.

**Built for Hackathon III: Reusable Intelligence and Cloud-Native Mastery**

## Overview

This library contains 7 Skills that enable AI agents (Claude Code, Goose, Codex) to autonomously deploy and manage cloud-native applications. Each Skill follows the MCP Code Execution pattern for maximum token efficiency.

## Token Efficiency

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

## Installation

Copy Skills to your Claude Code configuration:

```bash
# Clone this repository
git clone https://github.com/emberlearn/skills-library.git

# Copy to Claude Code skills directory
cp -r skills-library/* ~/.claude/skills/
```

## Skills

### 1. agents-md-gen
Generate AGENTS.md files for AI agent guidance.

```
Trigger: "Generate AGENTS.md for this repository"
```

### 2. kafka-k8s-setup
Deploy Kafka on Kubernetes via Bitnami Helm.

```
Trigger: "Deploy Kafka on Kubernetes"
```

### 3. postgres-k8s-setup
Deploy PostgreSQL with Alembic migrations.

```
Trigger: "Deploy PostgreSQL on Kubernetes"
```

### 4. fastapi-dapr-agent
Scaffold FastAPI + Dapr + OpenAI Agent microservices.

```
Trigger: "Create a new AI agent service"
```

### 5. mcp-code-execution
Create Skills with MCP Code Execution pattern.

```
Trigger: "Create a new Skill with MCP pattern"
```

### 6. nextjs-k8s-deploy
Deploy Next.js + Monaco Editor to Kubernetes.

```
Trigger: "Deploy Next.js frontend to Kubernetes"
```

### 7. docusaurus-deploy
Deploy documentation site via Skill.

```
Trigger: "Generate and deploy documentation"
```

## Skill Structure

Each Skill follows the MCP Code Execution pattern:

```
<skill-name>/
├── SKILL.md              # ~100 tokens: Instructions (loaded into context)
├── scripts/              # 0 tokens: Implementation (executed outside context)
│   ├── deploy.sh
│   ├── verify.py
│   └── rollback.sh
└── REFERENCE.md          # On-demand: Deep documentation
```

## Cross-Agent Compatibility

All Skills use the AAIF (Agentic AI Foundation) standard and have been tested on:

| Agent | Status |
|-------|--------|
| Claude Code | ✅ 7/7 pass |
| Goose | ✅ 7/7 pass |

## Creating New Skills

1. Create directory: `<skill-name>/`
2. Write SKILL.md with AAIF frontmatter:
   ```yaml
   ---
   name: skill-identifier
   description: What this does and when to use it
   ---
   ```
3. Create executable scripts in `scripts/`
4. Add REFERENCE.md for deep documentation
5. Test with both Claude Code and Goose

## Development

This library was developed as part of the EmberLearn project using Spec-Kit Plus workflow:
- Constitution with 8 principles
- 200 tasks across 10 phases
- PHRs for all significant prompts
- ADRs for architectural decisions

## License

MIT License - See LICENSE file for details.

## Related

- [EmberLearn](https://github.com/emberlearn/emberlearn) - AI-powered Python tutoring platform built using these Skills
