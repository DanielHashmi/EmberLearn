#!/usr/bin/env python3
"""Validate skill structure follows MCP code execution pattern."""

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = [
    "SKILL.md",
    "REFERENCE.md",
    "scripts/",
]

SKILL_MD_REQUIREMENTS = [
    ("YAML frontmatter", "---"),
    ("name field", "name:"),
    ("description field", "description:"),
    ("When to Use section", "## When to Use"),
    ("Instructions section", "## Instructions"),
]


def validate_skill(skill_dir: Path) -> tuple[bool, list[str]]:
    """Validate a skill directory structure."""
    errors = []

    # Check required files
    for required in REQUIRED_FILES:
        path = skill_dir / required
        if required.endswith("/"):
            if not path.is_dir():
                errors.append(f"Missing directory: {required}")
        else:
            if not path.exists():
                errors.append(f"Missing file: {required}")

    # Check SKILL.md content
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()

        for name, marker in SKILL_MD_REQUIREMENTS:
            if marker not in content:
                errors.append(f"SKILL.md missing: {name}")

        # Check token count (should be ~100 tokens)
        word_count = len(content.split())
        if word_count > 200:
            errors.append(f"SKILL.md too long: {word_count} words (target: <150)")

    # Check scripts directory has executable files
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.is_dir():
        scripts = list(scripts_dir.glob("*.py")) + list(scripts_dir.glob("*.sh"))
        if not scripts:
            errors.append("No scripts found in scripts/ directory")

    return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="Validate skill structure")
    parser.add_argument("skill_dir", type=Path, help="Path to skill directory")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Only output errors")
    args = parser.parse_args()

    if not args.skill_dir.exists():
        print(f"✗ Directory not found: {args.skill_dir}")
        sys.exit(1)

    valid, errors = validate_skill(args.skill_dir)

    if not args.quiet:
        print(f"Validating skill: {args.skill_dir.name}")
        print()

    if valid:
        if not args.quiet:
            print("✓ Skill structure is valid!")
            print()
            print("Checklist:")
            for name, _ in SKILL_MD_REQUIREMENTS:
                print(f"  ✓ {name}")
    else:
        print("✗ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
