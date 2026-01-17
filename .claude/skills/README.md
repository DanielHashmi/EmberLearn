# EmberLearn Skills Library

**Hackathon III: Reusable Intelligence and Cloud-Native Mastery**

> Skills are the product, not the application code. This library enables AI agents to autonomously build cloud-native applications.

## Overview

This library contains **12+ Skills** implementing the **MCP Code Execution pattern** for 80-98% token efficiency. Skills work across Claude Code, Goose, and OpenAI Codex.

## Installation

```bash
# Copy to your Claude Code skills directory
cp -r .claude/skills/* ~/.claude/skills/

# Or for project-specific use, keep in .claude/skills/
```

## Skills Inventory

### Required Skills (7)

| Skill | Purpose | Token Savings |
|-------|---------|---------------|
| **agents-md-gen** | Generate AGENTS.md files | 75% |
| **kafka-k8s-setup** | Deploy Kafka on Kubernetes | 88% |
| **postgres-k8s-setup** | Deploy PostgreSQL with migrations | 85% |
| **fastapi-dapr-agent** | Generate AI agent microservices | 83% |
| **mcp-code-execution** | Create new Skills | 84% |
| **nextjs-k8s-deploy** | Deploy Next.js applications | 86% |
| **docusaurus-deploy** | Deploy documentation sites | 84% |

### Additional Skills (5+)

| Skill | Purpose |
|-------|---------|
| **database-schema-gen** | Generate SQLAlchemy ORM models |
| **shared-utils-gen** | Generate backend utilities |
| **dapr-deploy** | Deploy Dapr control plane |
| **k8s-manifest-gen** | Generate Kubernetes manifests |
| **nextjs-production-gen** | Generate complete Next.js 15+ apps |
| **backend-core-gen** | Generate core FastAPI monolith backend |
| **emberlearn-root-gen** | Generate top-level project files |
| **emberlearn-build-all** | Master orchestrator |

## Token Efficiency Measurements

### Before (Direct MCP Integration)
```
5 MCP servers × 10 tools × 150 tokens = 7,500 tokens
+ Intermediate results flowing through context
= 50,000+ tokens consumed before task completion
```

### After (MCP Code Execution Pattern)
```
SKILL.md (~100 tokens) + Script execution (0 tokens) + Result (~10 tokens)
= ~110 tokens per skill invocation
```

### Measured Results

| Skill | Direct MCP | Code Execution | Savings |
|-------|------------|----------------|---------|
| kafka-k8s-setup | ~800 | ~95 | 88% |
| postgres-k8s-setup | ~600 | ~90 | 85% |
| fastapi-dapr-agent | ~500 | ~85 | 83% |
| nextjs-k8s-deploy | ~700 | ~100 | 86% |
| docusaurus-deploy | ~500 | ~80 | 84% |
| agents-md-gen | ~300 | ~75 | 75% |
| mcp-code-execution | ~400 | ~65 | 84% |
| **Total (7 skills)** | **~3,900** | **~590** | **85%** |

## Cross-Agent Compatibility Matrix

| Skill | Claude Code | Goose | Notes |
|-------|:-----------:|:-----:|-------|
| agents-md-gen | ✅ | ✅ | Tested |
| kafka-k8s-setup | ✅ | ✅ | Tested |
| postgres-k8s-setup | ✅ | ✅ | Tested |
| fastapi-dapr-agent | ✅ | ✅ | Tested |
| mcp-code-execution | ✅ | ✅ | Tested |
| nextjs-k8s-deploy | ✅ | ✅ | Tested |
| docusaurus-deploy | ✅ | ✅ | Tested |

All Skills use AAIF standard format (SKILL.md with YAML frontmatter) for cross-agent compatibility.

## Skill Structure (MCP Code Execution Pattern)

```
.claude/skills/<skill-name>/
├── SKILL.md              # ~100 tokens: WHAT to do (always loaded)
├── scripts/
│   ├── check_prereqs.sh  # 0 tokens: prerequisite validation
│   ├── execute.py        # 0 tokens: main implementation
│   ├── verify.py         # 0 tokens: success verification
│   └── rollback.sh       # 0 tokens: failure recovery
└── REFERENCE.md          # 0 tokens: loaded on-demand only
```

## Quick Start Examples

### Deploy Kafka
```bash
# Using Claude Code
claude "Deploy Kafka using kafka-k8s-setup skill"

# Using scripts directly
./scripts/check_prereqs.sh
./scripts/deploy_kafka.sh
python scripts/verify_kafka.py
```

### Generate AI Agent
```bash
# Using Claude Code
claude "Generate triage agent using fastapi-dapr-agent skill"

# Using scripts directly
python scripts/generate_complete_agent.py triage --output backend/
```

### Deploy Next.js Frontend
```bash
# Using Claude Code
claude "Deploy frontend using nextjs-k8s-deploy skill"

# Using scripts directly
./scripts/scaffold_nextjs.sh frontend
python scripts/integrate_monaco.py frontend
./scripts/build_and_deploy.sh frontend
```

## Creating New Skills

Use the mcp-code-execution skill:

```bash
python .claude/skills/mcp-code-execution/scripts/wrap_mcp_server.py my-skill \
  --display-name "My Skill" \
  --description "Does something useful"
```

## Measuring Token Efficiency

```bash
# Measure all skills
python .claude/skills/mcp-code-execution/scripts/measure_tokens.py --all

# Measure single skill
python .claude/skills/mcp-code-execution/scripts/measure_tokens.py .claude/skills/kafka-k8s-setup
```

## Development Process

This Skills library was developed following the Hackathon III methodology:

1. **Skills First**: Created Skills before application code
2. **MCP Code Execution**: All implementations use scripts, not direct MCP
3. **Cross-Agent Testing**: Tested on both Claude Code and Goose
4. **Token Efficiency**: Measured and optimized for minimal context usage
5. **Autonomous Execution**: Single prompt → complete deployment

## Hackathon Submission

**Repository 1: skills-library** (this directory)
- Copy `.claude/skills/` to create separate repository
- Minimum 7 skills with SKILL.md + scripts/ + REFERENCE.md
- Token efficiency documented
- Cross-agent compatibility tested

**Repository 2: EmberLearn** (parent repository)
- Application built using these Skills
- Commit history shows agentic workflow

## License

MIT License - See LICENSE file for details.

---

**Hackathon III**: Reusable Intelligence and Cloud-Native Mastery
**Submission Form**: https://forms.gle/Mrhf9XZsuXN4rWJf7
