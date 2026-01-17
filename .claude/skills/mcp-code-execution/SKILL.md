---
name: mcp-code-execution
description: Create Skills with MCP code execution pattern for token efficiency
---

# MCP Code Execution Pattern

## When to Use
- Create new reusable Skill
- Wrap MCP server as Skill

## Instructions
1. `python scripts/wrap_mcp_server.py <name> -d "<display>" -D "<desc>"`
2. `python scripts/validate_structure.py <skill_dir>`
3. `python scripts/measure_tokens.py --all`

See [REFERENCE.md](./REFERENCE.md) for pattern details.
