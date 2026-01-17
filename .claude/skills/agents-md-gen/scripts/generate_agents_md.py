#!/usr/bin/env python3
"""
Generate AGENTS.md file from repository analysis.

Creates a comprehensive AGENTS.md following the AAIF standard format.
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path


def generate_header(repo_name: str) -> str:
    """Generate the AGENTS.md header section."""
    return f"""# AGENTS.md - {repo_name}

> This file provides guidance for AI coding agents working with this repository.
> Generated: {datetime.now().strftime('%Y-%m-%d')}

"""


def generate_overview(analysis: dict) -> str:
    """Generate the overview section."""
    languages = ", ".join(l["name"] for l in analysis.get("languages", [])[:5])
    frameworks = []
    for f in analysis.get("frameworks", []):
        frameworks.extend(f.get("frameworks", []))
    frameworks_str = ", ".join(set(frameworks)[:10])

    return f"""## Overview

**Repository**: {analysis.get('repo_name', 'Unknown')}
**Primary Languages**: {languages or 'Not detected'}
**Frameworks/Tools**: {frameworks_str or 'Not detected'}
**Total Files**: {analysis.get('structure', {}).get('total_files', 'Unknown')}

"""


def generate_structure(analysis: dict) -> str:
    """Generate the project structure section."""
    dirs = analysis.get("structure", {}).get("directories", [])

    # Group by top-level directory
    top_level = set()
    for d in dirs:
        parts = d.split(os.sep)
        if parts:
            top_level.add(parts[0])

    structure_text = """## Project Structure

```
"""
    for d in sorted(top_level)[:20]:
        structure_text += f"{d}/\n"

    structure_text += """```

"""
    return structure_text


def generate_conventions(analysis: dict) -> str:
    """Generate coding conventions section based on detected languages."""
    conventions = """## Coding Conventions

"""

    languages = [l["name"] for l in analysis.get("languages", [])]

    if "Python" in languages:
        conventions += """### Python
- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Prefer f-strings for string formatting
- Use `async/await` for asynchronous code

"""

    if "TypeScript" in languages or "TypeScript (React)" in languages:
        conventions += """### TypeScript
- Use strict mode (`strict: true` in tsconfig)
- Prefer interfaces over type aliases for object shapes
- Use explicit return types for functions
- Follow React hooks conventions for components

"""

    if "JavaScript" in languages or "JavaScript (React)" in languages:
        conventions += """### JavaScript
- Use ES6+ features (const/let, arrow functions, destructuring)
- Prefer async/await over callbacks
- Use meaningful variable and function names

"""

    return conventions


def generate_ai_guidelines() -> str:
    """Generate AI agent guidelines section."""
    return """## AI Agent Guidelines

### Do
- Read existing code before making changes
- Follow established patterns in the codebase
- Write clear, descriptive commit messages
- Add appropriate error handling
- Maintain existing code style

### Don't
- Introduce new dependencies without justification
- Make changes outside the requested scope
- Remove existing functionality without explicit request
- Hardcode secrets or credentials
- Skip validation or error handling

### Testing
- Run existing tests before submitting changes
- Add tests for new functionality
- Ensure all tests pass before committing

### Documentation
- Update relevant documentation when changing functionality
- Add inline comments for complex logic
- Keep README.md up to date

"""


def generate_agents_md(analysis: dict, repo_name: str = None) -> str:
    """Generate complete AGENTS.md content."""
    name = repo_name or analysis.get("repo_name", "Repository")

    content = generate_header(name)
    content += generate_overview(analysis)
    content += generate_structure(analysis)
    content += generate_conventions(analysis)
    content += generate_ai_guidelines()

    return content


def main():
    parser = argparse.ArgumentParser(description="Generate AGENTS.md from repository analysis")
    parser.add_argument("--path", default=".", help="Path to repository")
    parser.add_argument("--analysis", help="Path to analysis JSON (from analyze_repo.py)")
    parser.add_argument("--output", default="AGENTS.md", help="Output file path")
    parser.add_argument("--name", help="Repository name override")
    args = parser.parse_args()

    try:
        # Load or generate analysis
        if args.analysis and os.path.exists(args.analysis):
            with open(args.analysis) as f:
                analysis = json.load(f)
        else:
            # Import and run analysis
            from analyze_repo import analyze_repo
            analysis = analyze_repo(args.path)

        # Generate AGENTS.md
        content = generate_agents_md(analysis, args.name)

        # Write output
        output_path = Path(args.path) / args.output if not os.path.isabs(args.output) else Path(args.output)
        with open(output_path, "w") as f:
            f.write(content)

        print(f"✓ AGENTS.md generated successfully: {output_path}")
        print(f"✓ File size: {len(content)} characters")

    except Exception as e:
        print(f"✗ Error generating AGENTS.md: {e}")
        exit(1)


if __name__ == "__main__":
    main()
