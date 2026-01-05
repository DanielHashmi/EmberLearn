#!/usr/bin/env python3
"""Scan codebase to extract documentation sources."""

import argparse
import json
import re
from pathlib import Path


def extract_docstrings(file_path: Path) -> list[dict]:
    """Extract docstrings from Python file."""
    content = file_path.read_text()
    docstrings = []

    # Module docstring
    module_match = re.match(r'^"""(.*?)"""', content, re.DOTALL)
    if module_match:
        docstrings.append({
            "type": "module",
            "content": module_match.group(1).strip(),
            "file": str(file_path),
        })

    # Function/class docstrings
    pattern = r'(?:def|class)\s+(\w+).*?:\s*"""(.*?)"""'
    for match in re.finditer(pattern, content, re.DOTALL):
        docstrings.append({
            "type": "function" if "def" in match.group(0) else "class",
            "name": match.group(1),
            "content": match.group(2).strip(),
            "file": str(file_path),
        })

    return docstrings


def extract_jsdoc(file_path: Path) -> list[dict]:
    """Extract JSDoc comments from TypeScript/JavaScript files."""
    content = file_path.read_text()
    docs = []

    # JSDoc pattern
    pattern = r'/\*\*\s*(.*?)\s*\*/\s*(?:export\s+)?(?:async\s+)?(?:function|const|class)\s+(\w+)'
    for match in re.finditer(pattern, content, re.DOTALL):
        docs.append({
            "type": "jsdoc",
            "name": match.group(2),
            "content": match.group(1).strip(),
            "file": str(file_path),
        })

    return docs


def scan_codebase(root_dir: Path) -> dict:
    """Scan codebase for documentation sources."""
    result = {
        "python_docs": [],
        "typescript_docs": [],
        "markdown_files": [],
        "api_specs": [],
        "skills": [],
    }

    # Scan Python files
    for py_file in root_dir.rglob("*.py"):
        if any(skip in str(py_file) for skip in ["__pycache__", ".venv", "node_modules"]):
            continue
        docs = extract_docstrings(py_file)
        result["python_docs"].extend(docs)

    # Scan TypeScript files
    for ts_file in list(root_dir.rglob("*.ts")) + list(root_dir.rglob("*.tsx")):
        if "node_modules" in str(ts_file):
            continue
        docs = extract_jsdoc(ts_file)
        result["typescript_docs"].extend(docs)

    # Find markdown files
    for md_file in root_dir.rglob("*.md"):
        if any(skip in str(md_file) for skip in ["node_modules", ".venv"]):
            continue
        result["markdown_files"].append({
            "path": str(md_file),
            "name": md_file.stem,
        })

    # Find API specs
    for spec_file in root_dir.rglob("*.yaml"):
        if "api" in spec_file.stem.lower() or "openapi" in spec_file.stem.lower():
            result["api_specs"].append(str(spec_file))

    # Find skills
    skills_dir = root_dir / ".claude" / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    result["skills"].append({
                        "name": skill_dir.name,
                        "path": str(skill_md),
                    })

    return result


def main():
    parser = argparse.ArgumentParser(description="Scan codebase for documentation")
    parser.add_argument("root_dir", type=Path, nargs="?", default=Path("."),
                        help="Root directory to scan")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    result = scan_codebase(args.root_dir)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    print("Documentation Sources Scan")
    print("=" * 50)
    print(f"Python docstrings: {len(result['python_docs'])}")
    print(f"TypeScript docs: {len(result['typescript_docs'])}")
    print(f"Markdown files: {len(result['markdown_files'])}")
    print(f"API specs: {len(result['api_specs'])}")
    print(f"Skills: {len(result['skills'])}")
    print()

    if result["skills"]:
        print("Skills found:")
        for skill in result["skills"]:
            print(f"  - {skill['name']}")

    if result["api_specs"]:
        print("\nAPI specs found:")
        for spec in result["api_specs"]:
            print(f"  - {spec}")


if __name__ == "__main__":
    main()
