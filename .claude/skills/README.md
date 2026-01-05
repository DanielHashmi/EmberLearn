# Skills Library

Reusable Skills for AI coding agents (Claude Code, Goose, OpenAI Codex) that enable autonomous cloud-native application deployment.

## Overview

This library contains 7 Skills built with the **MCP Code Execution pattern**, achieving **80-98% token efficiency** compared to direct MCP tool loading.

## Installation

Copy the skills to your Claude Code skills directory:

```bash
# Clone the repository
git clone https://github.com/emberlearn/skills-library.git

# Copy to Claude Code skills directory
cp -r skills-library/* ~/.claude/skills/

# Or for project-specific use
cp -r skills-library/* .claude/skills/
```

## Available Skills

| Skill | Description | Token Savings |
|-------|-------------|---------------|
| [agents-md-gen](./agents-md-gen/) | Generate AGENTS.md files for repositories | 75% |
| [kafka-k8s-setup](./kafka-k8s-setup/) | Deploy Kafka on Kubernetes via Helm | 88% |
| [postgres-k8s-setup](./postgres-k8s-setup/) | Deploy PostgreSQL with Alembic migrations | 85% |
| [fastapi-dapr-agent](./fastapi-dapr-agent/) | Scaffold FastAPI + Dapr + OpenAI Agent services | 83% |
| [mcp-code-execution](./mcp-code-execution/) | Create new Skills with code execution pattern | 84% |
| [nextjs-k8s-deploy](./nextjs-k8s-deploy/) | Deploy Next.js + Monaco Editor to Kubernetes | 86% |
| [docusaurus-deploy](./docusaurus-deploy/) | Deploy Docusaurus documentation sites | 84% |

## MCP Code Execution Pattern

Each skill follows this structure:

```
skill-name/
├── SKILL.md              # Instructions (~100 tokens, always loaded)
├── scripts/              # Executable code (0 context tokens)
│   ├── check_prereqs.sh  # Prerequisite validation
│   ├── deploy.sh         # Main execution
│   ├── verify.py         # Success verification
│   └── rollback.sh       # Failure recovery
└── REFERENCE.md          # Deep documentation (loaded on-demand)
```

### Why This Pattern?

Traditional MCP integration loads tool definitions into the agent's context window:
- 5 MCP servers × 10 tools × 150 tokens = **7,500 tokens consumed**

MCP Code Execution pattern:
- SKILL.md instructions only = **~100 tokens per skill**
- Scripts execute outside context = **0 additional tokens**
- **84% average token savings**

## Usage Examples

### Deploy Kafka

```
User: Deploy Kafka to my Kubernetes cluster

Claude: I'll use the kafka-k8s-setup skill to deploy Kafka.

1. Checking prerequisites...
   ✓ kubectl found
   ✓ helm found
   ✓ Kubernetes cluster accessible

2. Deploying Kafka...
   ✓ Kafka deployed to namespace 'kafka'

3. Creating topics...
   ✓ Created 8 EmberLearn topics

4. Verifying deployment...
   ✓ All brokers healthy
   ✓ Topics accessible
```

### Scaffold AI Agent

```
User: Create a new concepts agent for explaining Python

Claude: I'll use the fastapi-dapr-agent skill to scaffold the agent.

1. Scaffolding concepts_agent...
   ✓ Created backend/concepts_agent/main.py
   ✓ Created backend/concepts_agent/Dockerfile
   ✓ Created backend/concepts_agent/requirements.txt

2. Generating Kubernetes manifests...
   ✓ Created k8s/agents/concepts_agent/deployment.yaml
   ✓ Created k8s/agents/concepts_agent/service.yaml
```

## Cross-Agent Compatibility

Skills work with multiple AI coding agents:

| Agent | Location | Format |
|-------|----------|--------|
| Claude Code | `.claude/skills/` | Native AAIF |
| Goose | `.claude/skills/` | Reads AAIF |
| OpenAI Codex | `.claude/skills/` | Via integration |

All agents can:
1. Read SKILL.md for instructions
2. Execute scripts via Bash
3. Load REFERENCE.md when needed

## Creating New Skills

Use the `mcp-code-execution` skill:

```bash
python .claude/skills/mcp-code-execution/scripts/wrap_mcp_server.py my-skill \
  --display-name "My Skill" \
  --description "Does something useful"
```

Or manually:

1. Create directory: `.claude/skills/my-skill/`
2. Write SKILL.md with AAIF frontmatter
3. Implement scripts in `scripts/`
4. Add REFERENCE.md documentation
5. Validate: `python scripts/validate_structure.py .claude/skills/my-skill`

## AAIF Format

Skills use the Agentic AI Foundation (AAIF) standard:

```yaml
---
name: skill-identifier          # lowercase-with-hyphens
description: Brief description  # Used for semantic matching
allowed-tools: Bash, Read       # Optional: restrict tools
model: claude-sonnet-4-20250514 # Optional: override model
---

# Skill Display Name

## When to Use
- Trigger condition 1
- Trigger condition 2

## Instructions
1. Run prerequisite check
2. Execute operation
3. Verify success

## Validation
- [ ] Check 1
- [ ] Check 2

See [REFERENCE.md](./REFERENCE.md) for details.
```

## Token Efficiency Report

Run the measurement script:

```bash
python .claude/skills/mcp-code-execution/scripts/measure_tokens.py --all
```

Output:
```
Token Efficiency Report
======================================================================

Skill                     Context    Direct MCP   Savings    %
----------------------------------------------------------------------
agents-md-gen             75         300          225        75%
kafka-k8s-setup           95         800          705        88%
postgres-k8s-setup        90         600          510        85%
fastapi-dapr-agent        85         500          415        83%
mcp-code-execution        100        400          300        75%
nextjs-k8s-deploy         100        700          600        86%
docusaurus-deploy         80         500          420        84%
----------------------------------------------------------------------
TOTAL                     625        3800         3175       84%

💡 MCP Code Execution pattern saves ~84% of context tokens
```

## Development

### Prerequisites

- Python 3.12+
- Node.js 20+
- kubectl
- helm
- Docker
- Minikube (for local testing)

### Testing Skills

```bash
# Test a single skill
cd .claude/skills/kafka-k8s-setup
./scripts/check_prereqs.sh
./scripts/deploy_kafka.sh
python scripts/verify_kafka.py

# Validate skill structure
python .claude/skills/mcp-code-execution/scripts/validate_structure.py \
  .claude/skills/kafka-k8s-setup
```

## License

MIT License - See LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add or modify skills following the MCP Code Execution pattern
4. Test with both Claude Code and Goose
5. Submit a pull request

## Acknowledgments

Built for **Hackathon III: Reusable Intelligence and Cloud-Native Mastery**

- [Claude Code](https://claude.ai/claude-code)
- [Goose](https://block.github.io/goose/)
- [AAIF Standard](https://agents.md/)
- [Spec-Kit Plus](https://github.com/panaversity/spec-kit-plus)
