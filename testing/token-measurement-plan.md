# Token Measurement Plan

## Overview

This document outlines the methodology for measuring token efficiency of the MCP Code Execution pattern versus direct MCP tool loading.

## Measurement Approach

### Baseline: Direct MCP Integration

When MCP tools are loaded directly into an agent's context, each tool definition consumes tokens:

```
Tool Definition Structure:
- name: ~5 tokens
- description: ~50-100 tokens
- parameters schema: ~100-200 tokens
- examples: ~50-100 tokens
Total per tool: ~150-400 tokens
```

### Skills + Scripts Pattern

With MCP Code Execution pattern:
- SKILL.md loaded into context: ~100 tokens
- Scripts execute outside context: 0 tokens
- REFERENCE.md loaded on-demand: 0 tokens (unless requested)
- Script output (minimal): ~10-20 tokens

## Token Counting Methodology

### 1. Character-Based Estimation

Using GPT tokenizer average: ~4 characters per token

```python
def estimate_tokens(text: str) -> int:
    return len(text) // 4
```

### 2. Actual Token Counting

For precise measurements, use tiktoken library:

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4")
tokens = len(enc.encode(text))
```

## Measurement Process

### For Each Skill:

1. **Measure SKILL.md tokens**
   - Read SKILL.md content
   - Count tokens using estimation or tiktoken
   - This is the "context cost" of the skill

2. **Estimate Direct MCP equivalent**
   - Identify what MCP tools would be needed
   - Estimate tokens for each tool definition
   - Sum total for baseline

3. **Calculate savings**
   ```
   savings_tokens = baseline - skill_tokens
   savings_percent = (savings_tokens / baseline) * 100
   ```

## Expected Results

| Skill | Direct MCP (est.) | Skills Pattern | Savings |
|-------|-------------------|----------------|---------|
| agents-md-gen | ~300 | ~75 | 75% |
| kafka-k8s-setup | ~800 | ~95 | 88% |
| postgres-k8s-setup | ~600 | ~90 | 85% |
| fastapi-dapr-agent | ~500 | ~85 | 83% |
| mcp-code-execution | ~400 | ~100 | 75% |
| nextjs-k8s-deploy | ~700 | ~100 | 86% |
| docusaurus-deploy | ~500 | ~80 | 84% |

## Direct MCP Baseline Estimates

### agents-md-gen (~300 tokens)
Would require:
- File system tools (read, write, list): ~150 tokens
- Analysis tools (language detection): ~100 tokens
- Template tools: ~50 tokens

### kafka-k8s-setup (~800 tokens)
Would require:
- Kubernetes tools (apply, get, delete): ~300 tokens
- Helm tools (install, upgrade, list): ~200 tokens
- Kafka admin tools (topics, describe): ~200 tokens
- Verification tools: ~100 tokens

### postgres-k8s-setup (~600 tokens)
Would require:
- Kubernetes tools: ~200 tokens
- Helm tools: ~150 tokens
- Database tools (query, migrate): ~150 tokens
- Schema tools: ~100 tokens

### fastapi-dapr-agent (~500 tokens)
Would require:
- Scaffolding tools: ~200 tokens
- Template tools: ~150 tokens
- Kubernetes manifest tools: ~150 tokens

### mcp-code-execution (~400 tokens)
Would require:
- File generation tools: ~150 tokens
- Validation tools: ~150 tokens
- Template tools: ~100 tokens

### nextjs-k8s-deploy (~700 tokens)
Would require:
- Node.js tools: ~200 tokens
- Build tools: ~150 tokens
- Kubernetes tools: ~200 tokens
- Docker tools: ~150 tokens

### docusaurus-deploy (~500 tokens)
Would require:
- Documentation tools: ~200 tokens
- Build tools: ~150 tokens
- Deploy tools: ~150 tokens

## Validation

To validate measurements:
1. Run `measure_tokens.py` script on all skills
2. Compare estimated vs actual SKILL.md tokens
3. Verify savings percentages meet 80% threshold
4. Document any outliers

## Success Criteria

- All 7 skills achieve ≥75% token savings
- Average savings across all skills ≥80%
- Methodology documented and reproducible
