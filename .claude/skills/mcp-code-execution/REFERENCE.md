# MCP Code Execution Pattern - Reference

## Overview

This skill implements the MCP Code Execution pattern, which dramatically reduces token usage by keeping tool implementations outside the agent's context window.

## The Problem

Traditional MCP integration loads tool definitions into the agent context:

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Context Window                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  MCP Tool Definitions (~500-1000 tokens each)       │   │
│  │  - Tool 1: name, description, parameters, schema    │   │
│  │  - Tool 2: name, description, parameters, schema    │   │
│  │  - Tool 3: name, description, parameters, schema    │   │
│  │  ...                                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Conversation + Task Context                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Problem**: 5 MCP servers × 10 tools × 150 tokens = **7,500 tokens** consumed before any work begins.

## The Solution

MCP Code Execution pattern moves implementations to scripts:

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent Context Window                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  SKILL.md (~100 tokens)                              │   │
│  │  - When to use                                       │   │
│  │  - Instructions (run scripts)                        │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Conversation + Task Context (MORE SPACE!)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │
         │ Bash tool calls
         ▼
┌─────────────────────────────────────────────────────────────┐
│                 External Execution (0 tokens)                │
│  scripts/deploy.sh    → Runs outside context                │
│  scripts/verify.py    → Returns minimal result              │
│  REFERENCE.md         → Loaded only when needed             │
└─────────────────────────────────────────────────────────────┘
```

**Result**: ~100 tokens per skill, **80-98% reduction**.

## Pattern Structure

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

## SKILL.md Format (AAIF Standard)

```yaml
---
name: skill-identifier          # lowercase-with-hyphens
description: Brief description  # Used for semantic matching
allowed-tools: Bash, Read       # Optional: restrict available tools
model: claude-sonnet-4-20250514 # Optional: override model
---

# Skill Display Name

## When to Use
- Trigger condition 1
- Trigger condition 2

## Instructions
1. Run prerequisite check: `./scripts/check_prereqs.sh`
2. Execute operation: `python scripts/execute.py [args]`
3. Verify success: `python scripts/verify.py`

## Validation
- [ ] Check 1
- [ ] Check 2

See [REFERENCE.md](./REFERENCE.md) for details.
```

## Token Efficiency Measurements

| Skill | Direct MCP | Code Execution | Savings |
|-------|------------|----------------|---------|
| kafka-k8s-setup | ~800 | ~95 | 88% |
| postgres-k8s-setup | ~600 | ~90 | 85% |
| fastapi-dapr-agent | ~500 | ~85 | 83% |
| nextjs-k8s-deploy | ~700 | ~100 | 86% |
| docusaurus-deploy | ~500 | ~80 | 84% |
| agents-md-gen | ~300 | ~75 | 75% |
| **Total (7 skills)** | **~3,900** | **~625** | **84%** |

## Script Best Practices

### 1. Minimal Output

```python
# BAD: Verbose output
print(f"Starting deployment of {service} to {namespace}...")
print(f"Checking prerequisites...")
print(f"Found kubectl version {version}")
# ... 50 more lines

# GOOD: Minimal, structured output
print(f"✓ {service} deployed to {namespace}")
```

### 2. Structured Results

```python
# Return parseable results
result = {
    "status": "success",
    "service": "kafka",
    "namespace": "kafka",
    "endpoints": ["kafka.kafka.svc.cluster.local:9092"]
}
print(json.dumps(result))
```

### 3. Clear Exit Codes

```bash
# Success
exit 0

# Failure with message
echo "✗ Deployment failed: $error_message" >&2
exit 1
```

### 4. Idempotency

```python
# Check if already done before doing
if is_already_deployed():
    print("✓ Already deployed, skipping")
    return

deploy()
print("✓ Deployed successfully")
```

## Creating New Skills

### Using the Wrapper Script

```bash
python scripts/wrap_mcp_server.py my-new-skill \
  --display-name "My New Skill" \
  --description "Does something useful"
```

### Manual Creation

1. Create directory structure
2. Write SKILL.md (~100 tokens max)
3. Implement scripts
4. Add REFERENCE.md
5. Validate with `python scripts/validate_structure.py`

## Measuring Efficiency

```bash
# Measure single skill
python scripts/measure_tokens.py .claude/skills/kafka-k8s-setup

# Measure all skills
python scripts/measure_tokens.py --all

# JSON output for automation
python scripts/measure_tokens.py --all --json
```

## Cross-Agent Compatibility

The MCP Code Execution pattern works with:

| Agent | Skill Location | Notes |
|-------|----------------|-------|
| Claude Code | `.claude/skills/` | Native support |
| Goose | `.claude/skills/` | Reads AAIF format |
| OpenAI Codex | `.claude/skills/` | Via custom integration |

All agents can:
1. Read SKILL.md for instructions
2. Execute scripts via Bash
3. Load REFERENCE.md when needed

## Troubleshooting

### Skill Not Triggering

- Check `description` field matches user intent
- Verify skill is in `.claude/skills/` directory
- Test with explicit: "Use the X skill to..."

### Script Execution Fails

- Ensure scripts are executable: `chmod +x scripts/*.sh`
- Check shebang lines: `#!/bin/bash` or `#!/usr/bin/env python3`
- Verify dependencies are available

### Token Count Higher Than Expected

- SKILL.md may be too verbose (target: <150 words)
- REFERENCE.md being loaded unnecessarily
- Script output too verbose (minimize stdout)
