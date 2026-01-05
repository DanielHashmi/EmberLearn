#!/usr/bin/env python3
"""Verify the structure of a scaffolded FastAPI + Dapr agent."""

import argparse
import sys
from pathlib import Path


REQUIRED_FILES = [
    "main.py",
    "Dockerfile",
    "requirements.txt",
    "__init__.py",
]

REQUIRED_IMPORTS = [
    "fastapi",
    "dapr",
    "openai",
    "structlog",
]

REQUIRED_ENDPOINTS = [
    "/health",
    "/query",
    "/dapr/subscribe",
]


def check_file_exists(agent_dir: Path, filename: str) -> bool:
    """Check if a required file exists."""
    return (agent_dir / filename).exists()


def check_imports(main_py: Path) -> list[str]:
    """Check for required imports in main.py."""
    content = main_py.read_text()
    missing = []
    for imp in REQUIRED_IMPORTS:
        if f"import {imp}" not in content and f"from {imp}" not in content:
            missing.append(imp)
    return missing


def check_endpoints(main_py: Path) -> list[str]:
    """Check for required endpoints in main.py."""
    content = main_py.read_text()
    missing = []
    for endpoint in REQUIRED_ENDPOINTS:
        if f'"{endpoint}"' not in content and f"'{endpoint}'" not in content:
            missing.append(endpoint)
    return missing


def verify_agent(agent_dir: Path) -> bool:
    """Verify agent structure and return success status."""
    print(f"Verifying agent at {agent_dir}...")
    print()

    errors = []

    # Check required files
    print("Checking required files:")
    for filename in REQUIRED_FILES:
        if check_file_exists(agent_dir, filename):
            print(f"  ✓ {filename}")
        else:
            print(f"  ✗ {filename} - MISSING")
            errors.append(f"Missing file: {filename}")

    # Check main.py contents
    main_py = agent_dir / "main.py"
    if main_py.exists():
        print("\nChecking imports:")
        missing_imports = check_imports(main_py)
        if not missing_imports:
            print("  ✓ All required imports present")
        else:
            for imp in missing_imports:
                print(f"  ✗ Missing import: {imp}")
                errors.append(f"Missing import: {imp}")

        print("\nChecking endpoints:")
        missing_endpoints = check_endpoints(main_py)
        if not missing_endpoints:
            print("  ✓ All required endpoints present")
        else:
            for endpoint in missing_endpoints:
                print(f"  ✗ Missing endpoint: {endpoint}")
                errors.append(f"Missing endpoint: {endpoint}")

    # Check Dockerfile
    dockerfile = agent_dir / "Dockerfile"
    if dockerfile.exists():
        print("\nChecking Dockerfile:")
        content = dockerfile.read_text()
        if "uvicorn" in content:
            print("  ✓ Uses uvicorn")
        else:
            print("  ✗ Missing uvicorn command")
            errors.append("Dockerfile missing uvicorn")

        if "8000" in content:
            print("  ✓ Exposes port 8000")
        else:
            print("  ✗ Missing port 8000")
            errors.append("Dockerfile missing port 8000")

    # Summary
    print()
    if errors:
        print(f"✗ Verification failed with {len(errors)} error(s)")
        return False
    else:
        print("✓ Agent structure verified successfully!")
        return True


def main():
    parser = argparse.ArgumentParser(description="Verify FastAPI + Dapr agent structure")
    parser.add_argument("agent_dir", type=Path, help="Path to agent directory")
    args = parser.parse_args()

    if not args.agent_dir.exists():
        print(f"✗ Directory not found: {args.agent_dir}")
        sys.exit(1)

    success = verify_agent(args.agent_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
