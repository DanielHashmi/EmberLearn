#!/usr/bin/env python3
"""
Check prerequisites for Next.js production generation.
"""

import sys
import subprocess
import json
from pathlib import Path

def check_command(command: str, min_version: str = None) -> bool:
    """Check if a command exists and optionally verify version."""
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ {command} found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"✗ {command} not found")
        return False

def check_design_system(path: str) -> bool:
    """Check if design system file exists and is valid JSON."""
    design_system_path = Path(path)

    if not design_system_path.exists():
        print(f"✗ Design system not found at: {path}")
        return False

    try:
        with open(design_system_path, 'r') as f:
            data = json.load(f)

        # Validate required sections
        required_sections = ['colors', 'typography', 'spacing', 'animations']
        missing = [s for s in required_sections if s not in data]

        if missing:
            print(f"✗ Design system missing sections: {', '.join(missing)}")
            return False

        print(f"✓ Design system valid: {path}")
        return True

    except json.JSONDecodeError as e:
        print(f"✗ Design system invalid JSON: {e}")
        return False

def main():
    """Run all prerequisite checks."""
    print("Checking prerequisites for Next.js production generation...\n")

    checks = [
        ("Node.js", lambda: check_command("node")),
        ("npm", lambda: check_command("npm")),
        ("Design System", lambda: check_design_system("design-system.json")),
    ]

    results = []
    for name, check_fn in checks:
        try:
            results.append(check_fn())
        except Exception as e:
            print(f"✗ {name} check failed: {e}")
            results.append(False)

    print("\n" + "="*60)

    if all(results):
        print("✓ All prerequisites met. Ready to generate.")
        sys.exit(0)
    else:
        print("✗ Some prerequisites missing. Please install required tools.")
        sys.exit(1)

if __name__ == "__main__":
    main()
