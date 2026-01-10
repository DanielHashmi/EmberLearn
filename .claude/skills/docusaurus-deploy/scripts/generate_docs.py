#!/usr/bin/env python3
"""Generate documentation pages from codebase sources."""

import argparse
import json
from pathlib import Path


INTRO_MD = '''---
sidebar_position: 1
---

# Introduction

Welcome to **EmberLearn** - an AI-powered Python tutoring platform built with cloud-native architecture.

## What is EmberLearn?

EmberLearn is an intelligent tutoring system that helps students learn Python programming through:

- **AI-Powered Tutoring**: 6 specialized AI agents provide personalized guidance
- **Real-Time Code Execution**: Write and run Python code in the browser
- **Adaptive Learning**: Mastery-based progression through 8 Python topics
- **Struggle Detection**: Automatic identification of learning difficulties

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                    Monaco Editor + Chat UI                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Kong)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Agent Services                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ Triage  │ │Concepts │ │  Debug  │ │Exercise │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Event Streaming (Kafka + Dapr)                  │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/emberlearn/emberlearn.git
cd emberlearn

# Start Minikube
minikube start --cpus=4 --memory=8192

# Deploy infrastructure
./scripts/deploy-all.sh

# Access the application
minikube service emberlearn-frontend
```

## Built With Skills

EmberLearn was built using reusable Skills that enable autonomous deployment:

- **kafka-k8s-setup**: Deploy Kafka event streaming
- **postgres-k8s-setup**: Deploy PostgreSQL with migrations
- **fastapi-dapr-agent**: Scaffold AI agent microservices
- **nextjs-k8s-deploy**: Deploy the frontend application
- **docusaurus-deploy**: Generate this documentation

See the [Skills documentation](/docs/skills/overview) for details.
'''


SKILLS_OVERVIEW_MD = '''---
sidebar_position: 1
---

# Skills Overview

EmberLearn uses **Skills** - reusable capabilities that enable AI agents to autonomously deploy and manage cloud-native applications.

## What are Skills?

Skills follow the **MCP Code Execution pattern**:

```
.claude/skills/<skill-name>/
├── SKILL.md              # Instructions (~100 tokens)
├── scripts/              # Executable code (0 context tokens)
│   ├── deploy.sh
│   ├── verify.py
│   └── rollback.sh
└── REFERENCE.md          # Deep documentation (on-demand)
```

## Token Efficiency

| Approach | Context Tokens | Notes |
|----------|----------------|-------|
| Direct MCP | ~3,900 | Tool definitions loaded |
| Code Execution | ~625 | Only SKILL.md loaded |
| **Savings** | **84%** | Scripts execute outside context |

## Available Skills

| Skill | Purpose |
|-------|---------|
| [agents-md-gen](/docs/skills/agents-md-gen) | Generate AGENTS.md files |
| [kafka-k8s-setup](/docs/skills/kafka-k8s-setup) | Deploy Kafka on Kubernetes |
| [postgres-k8s-setup](/docs/skills/postgres-k8s-setup) | Deploy PostgreSQL with migrations |
| [fastapi-dapr-agent](/docs/skills/fastapi-dapr-agent) | Scaffold AI agent services |
| [mcp-code-execution](/docs/skills/mcp-code-execution) | Create new Skills |
| [nextjs-k8s-deploy](/docs/skills/nextjs-k8s-deploy) | Deploy Next.js applications |
| [docusaurus-deploy](/docs/skills/docusaurus-deploy) | Deploy documentation sites |

## Cross-Agent Compatibility

Skills work with multiple AI coding agents:

- **Claude Code**: Native support via `.claude/skills/`
- **Goose**: Reads AAIF format from `.claude/skills/`
- **OpenAI Codex**: Via custom integration

## Creating New Skills

Use the `mcp-code-execution` skill to create new Skills:

```bash
python .claude/skills/mcp-code-execution/scripts/wrap_mcp_server.py my-skill \\
  --display-name "My Skill" \\
  --description "Does something useful"
```
'''


def generate_skill_doc(skill_name: str, skill_md_path: Path) -> str:
    """Generate documentation page for a skill."""
    content = skill_md_path.read_text()

    # Extract description from YAML frontmatter
    description = "No description available"
    if "description:" in content:
        for line in content.split("\n"):
            if line.strip().startswith("description:"):
                description = line.split(":", 1)[1].strip()
                break

    return f'''---
sidebar_position: 2
---

# {skill_name}

{description}

## Usage

```bash
# Navigate to skill directory
cd .claude/skills/{skill_name}

# Check prerequisites
./scripts/check_prereqs.sh

# Execute the skill
# (see SKILL.md for specific commands)
```

## Files

- `SKILL.md` - Instructions for AI agents
- `scripts/` - Executable scripts
- `REFERENCE.md` - Detailed documentation

## Source

View the full skill at `.claude/skills/{skill_name}/`
'''


def generate_docs(source_dir: Path, output_dir: Path) -> None:
    """Generate documentation pages from codebase."""
    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Create intro page
    (docs_dir / "intro.md").write_text(INTRO_MD)
    print(f"✓ Created {docs_dir}/intro.md")

    # Create getting-started directory
    gs_dir = docs_dir / "getting-started"
    gs_dir.mkdir(exist_ok=True)

    # Create skills directory
    skills_dir = docs_dir / "skills"
    skills_dir.mkdir(exist_ok=True)
    (skills_dir / "overview.md").write_text(SKILLS_OVERVIEW_MD)
    print(f"✓ Created {skills_dir}/overview.md")

    # Generate skill docs
    source_skills = source_dir / ".claude" / "skills"
    if source_skills.exists():
        for skill_path in source_skills.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    doc = generate_skill_doc(skill_path.name, skill_md)
                    (skills_dir / f"{skill_path.name}.md").write_text(doc)
                    print(f"✓ Created {skills_dir}/{skill_path.name}.md")

    # Create API directory
    api_dir = docs_dir / "api"
    api_dir.mkdir(exist_ok=True)

    # Create architecture directory
    arch_dir = docs_dir / "architecture"
    arch_dir.mkdir(exist_ok=True)

    print(f"\n✓ Documentation generated at {docs_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate documentation pages")
    parser.add_argument("--source", "-s", type=Path, default=Path("."),
                        help="Source codebase directory")
    parser.add_argument("--output", "-o", type=Path, default=Path("docs-site"),
                        help="Output directory")
    args = parser.parse_args()

    generate_docs(args.source, args.output)


if __name__ == "__main__":
    main()
