#!/usr/bin/env python3
"""Verify Docusaurus documentation deployment."""

import argparse
import subprocess
import sys
from pathlib import Path


def check_build_output(docs_dir: Path) -> bool:
    """Check if build output exists."""
    build_dir = docs_dir / "build"
    if not build_dir.exists():
        return False
    # Check for index.html
    index_html = build_dir / "index.html"
    return index_html.exists()


def check_required_pages(docs_dir: Path) -> tuple[bool, list[str]]:
    """Check for required documentation pages."""
    required = [
        "docs/intro.md",
        "docs/skills/overview.md",
    ]
    missing = []
    for page in required:
        if not (docs_dir / page).exists():
            missing.append(page)
    return len(missing) == 0, missing


def check_config(docs_dir: Path) -> bool:
    """Check if Docusaurus config exists."""
    return (docs_dir / "docusaurus.config.js").exists()


def check_dependencies(docs_dir: Path) -> bool:
    """Check if dependencies are installed."""
    return (docs_dir / "node_modules").exists()


def verify_deployment(docs_dir: Path) -> bool:
    """Run all verification checks."""
    print(f"Verifying Docusaurus deployment: {docs_dir}")
    print()

    checks_passed = 0
    checks_failed = 0

    # Check config
    print("Checking configuration...", end=" ")
    if check_config(docs_dir):
        print("✓")
        checks_passed += 1
    else:
        print("✗ docusaurus.config.js not found")
        checks_failed += 1

    # Check required pages
    print("Checking required pages...", end=" ")
    pages_ok, missing = check_required_pages(docs_dir)
    if pages_ok:
        print("✓")
        checks_passed += 1
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        checks_failed += 1

    # Check dependencies
    print("Checking dependencies...", end=" ")
    if check_dependencies(docs_dir):
        print("✓")
        checks_passed += 1
    else:
        print("✗ Run 'npm install' first")
        checks_failed += 1

    # Check build output
    print("Checking build output...", end=" ")
    if check_build_output(docs_dir):
        print("✓")
        checks_passed += 1
    else:
        print("✗ Run 'npm run build' first")
        checks_failed += 1

    # Summary
    print()
    if checks_failed > 0:
        print(f"✗ Verification failed: {checks_passed} passed, {checks_failed} failed")
        return False
    else:
        print(f"✓ All {checks_passed} checks passed!")
        return True


def main():
    parser = argparse.ArgumentParser(description="Verify Docusaurus deployment")
    parser.add_argument("docs_dir", type=Path, nargs="?", default=Path("docs-site"),
                        help="Documentation directory")
    args = parser.parse_args()

    if not args.docs_dir.exists():
        print(f"✗ Directory not found: {args.docs_dir}")
        sys.exit(1)

    success = verify_deployment(args.docs_dir)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
