#!/usr/bin/env python3
"""Wrap an MCP server capability as a Skill with code execution pattern."""

import argparse
import os
from pathlib import Path


SKILL_MD_TEMPLATE = '''---
name: {skill_name}
description: {description}
allowed-tools: Bash, Read
---

# {display_name}

## When to Use
- {use_case_1}
- {use_case_2}

## Instructions

1. Check prerequisites:
   ```bash
   ./scripts/check_prereqs.sh
   ```

2. Execute the operation:
   ```bash
   python scripts/execute.py {example_args}
   ```

3. Verify success:
   ```bash
   python scripts/verify.py
   ```

## Validation
- [ ] Prerequisites met
- [ ] Operation completed successfully
- [ ] Verification passed

See [REFERENCE.md](./REFERENCE.md) for configuration options.
'''


EXECUTE_PY_TEMPLATE = '''#!/usr/bin/env python3
"""{description}"""

import argparse
import subprocess
import sys


def execute_{operation}({params}):
    """{operation_doc}"""
    # Implementation that calls external tools/APIs
    # This runs OUTSIDE the agent context

    try:
        # Your implementation here
        result = {{"status": "success", "message": "Operation completed"}}
        print(f"✓ {{result['message']}}")
        return result
    except Exception as e:
        print(f"✗ Error: {{e}}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="{description}")
    # Add your arguments here
    args = parser.parse_args()

    execute_{operation}()


if __name__ == "__main__":
    main()
'''


VERIFY_PY_TEMPLATE = '''#!/usr/bin/env python3
"""Verify the {skill_name} operation completed successfully."""

import argparse
import sys


def verify():
    """Run verification checks."""
    checks_passed = 0
    checks_failed = 0

    # Add your verification checks here
    print("Running verification checks...")

    # Example check
    print("  ✓ Operation completed")
    checks_passed += 1

    print()
    if checks_failed > 0:
        print(f"✗ Verification failed: {{checks_passed}} passed, {{checks_failed}} failed")
        sys.exit(1)
    else:
        print(f"✓ All {{checks_passed}} checks passed!")


def main():
    parser = argparse.ArgumentParser(description="Verify {skill_name}")
    args = parser.parse_args()
    verify()


if __name__ == "__main__":
    main()
'''


CHECK_PREREQS_TEMPLATE = '''#!/bin/bash
# Check prerequisites for {skill_name}

set -e

echo "Checking prerequisites for {skill_name}..."

# Add your prerequisite checks here
# Example:
# if ! command -v some_tool &> /dev/null; then
#     echo "✗ some_tool not found"
#     exit 1
# fi
# echo "✓ some_tool found"

echo ""
echo "✓ All prerequisites met!"
'''


REFERENCE_MD_TEMPLATE = '''# {display_name} - Reference

## Overview

{description}

## Token Efficiency

| Approach | Context Tokens | Notes |
|----------|----------------|-------|
| Direct MCP | ~{direct_tokens} | Tool definitions loaded into context |
| Code Execution | ~100 | Only SKILL.md loaded; scripts execute outside |
| **Savings** | **{savings}%** | |

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `EXAMPLE_VAR` | No | Example configuration |

## Usage Examples

### Basic Usage

```bash
python scripts/execute.py --example arg
```

### With Options

```bash
python scripts/execute.py --option value
```

## Troubleshooting

### Common Issues

1. **Issue**: Description
   - **Solution**: How to fix

## Integration

This skill wraps the following MCP capabilities:
- Capability 1
- Capability 2

By using the code execution pattern, these capabilities are available
without loading MCP tool definitions into the agent context.
'''


def create_skill(
    skill_name: str,
    display_name: str,
    description: str,
    output_dir: Path,
) -> None:
    """Create a new skill with MCP code execution pattern."""
    skill_dir = output_dir / skill_name
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)

    # Create SKILL.md
    skill_md = SKILL_MD_TEMPLATE.format(
        skill_name=skill_name,
        display_name=display_name,
        description=description,
        use_case_1=f"User needs to {description.lower()}",
        use_case_2=f"Setting up {display_name.lower()} functionality",
        example_args="--example arg",
    )
    (skill_dir / "SKILL.md").write_text(skill_md)
    print(f"✓ Created {skill_dir}/SKILL.md")

    # Create execute.py
    execute_py = EXECUTE_PY_TEMPLATE.format(
        description=description,
        operation=skill_name.replace("-", "_"),
        operation_doc=f"Execute {display_name} operation",
        params="",
    )
    (scripts_dir / "execute.py").write_text(execute_py)
    os.chmod(scripts_dir / "execute.py", 0o755)
    print(f"✓ Created {scripts_dir}/execute.py")

    # Create verify.py
    verify_py = VERIFY_PY_TEMPLATE.format(skill_name=skill_name)
    (scripts_dir / "verify.py").write_text(verify_py)
    os.chmod(scripts_dir / "verify.py", 0o755)
    print(f"✓ Created {scripts_dir}/verify.py")

    # Create check_prereqs.sh
    check_prereqs = CHECK_PREREQS_TEMPLATE.format(skill_name=skill_name)
    (scripts_dir / "check_prereqs.sh").write_text(check_prereqs)
    os.chmod(scripts_dir / "check_prereqs.sh", 0o755)
    print(f"✓ Created {scripts_dir}/check_prereqs.sh")

    # Create REFERENCE.md
    reference_md = REFERENCE_MD_TEMPLATE.format(
        display_name=display_name,
        description=description,
        direct_tokens=750,
        savings=87,
    )
    (skill_dir / "REFERENCE.md").write_text(reference_md)
    print(f"✓ Created {skill_dir}/REFERENCE.md")

    print(f"\n✓ Skill '{skill_name}' created at {skill_dir}")
    print("\nNext steps:")
    print("  1. Edit scripts/execute.py with your implementation")
    print("  2. Add verification checks to scripts/verify.py")
    print("  3. Update REFERENCE.md with detailed documentation")


def main():
    parser = argparse.ArgumentParser(
        description="Create a skill with MCP code execution pattern"
    )
    parser.add_argument("skill_name", help="Skill identifier (lowercase-with-hyphens)")
    parser.add_argument("--display-name", "-d", required=True,
                        help="Human-readable skill name")
    parser.add_argument("--description", "-D", required=True,
                        help="Brief description of what the skill does")
    parser.add_argument("--output", "-o", type=Path, default=Path(".claude/skills"),
                        help="Output directory (default: .claude/skills)")
    args = parser.parse_args()

    create_skill(
        args.skill_name,
        args.display_name,
        args.description,
        args.output,
    )


if __name__ == "__main__":
    main()
