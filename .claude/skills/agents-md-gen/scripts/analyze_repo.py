#!/usr/bin/env python3
"""
Analyze repository structure for AGENTS.md generation.

Scans the repository to identify:
- Directory structure
- File types and conventions
- Existing documentation
- Code patterns
"""

import argparse
import json
import os
from pathlib import Path
from collections import defaultdict


def analyze_directory_structure(repo_path: Path) -> dict:
    """Analyze the directory structure of the repository."""
    structure = {
        "directories": [],
        "file_counts": defaultdict(int),
        "total_files": 0,
    }

    ignore_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".next"}

    for root, dirs, files in os.walk(repo_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        rel_path = os.path.relpath(root, repo_path)
        if rel_path != ".":
            structure["directories"].append(rel_path)

        for file in files:
            ext = Path(file).suffix.lower()
            structure["file_counts"][ext] += 1
            structure["total_files"] += 1

    return structure


def detect_languages(file_counts: dict) -> list:
    """Detect programming languages used in the repository."""
    language_map = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript (React)",
        ".jsx": "JavaScript (React)",
        ".go": "Go",
        ".rs": "Rust",
        ".java": "Java",
        ".rb": "Ruby",
        ".php": "PHP",
        ".cs": "C#",
        ".cpp": "C++",
        ".c": "C",
        ".swift": "Swift",
        ".kt": "Kotlin",
    }

    languages = []
    for ext, count in file_counts.items():
        if ext in language_map and count > 0:
            languages.append({
                "name": language_map[ext],
                "extension": ext,
                "file_count": count,
            })

    return sorted(languages, key=lambda x: x["file_count"], reverse=True)


def detect_frameworks(repo_path: Path) -> list:
    """Detect frameworks and tools used in the repository."""
    frameworks = []

    # Check for common framework indicators
    indicators = {
        "package.json": ["Node.js", "npm"],
        "pyproject.toml": ["Python", "Poetry/Hatch"],
        "requirements.txt": ["Python", "pip"],
        "Cargo.toml": ["Rust", "Cargo"],
        "go.mod": ["Go", "Go Modules"],
        "pom.xml": ["Java", "Maven"],
        "build.gradle": ["Java/Kotlin", "Gradle"],
        "Gemfile": ["Ruby", "Bundler"],
        "composer.json": ["PHP", "Composer"],
        "Dockerfile": ["Docker"],
        "docker-compose.yml": ["Docker Compose"],
        "kubernetes": ["Kubernetes"],
        "k8s": ["Kubernetes"],
        ".claude": ["Claude Code Skills"],
        "next.config.js": ["Next.js"],
        "next.config.mjs": ["Next.js"],
        "tailwind.config.js": ["Tailwind CSS"],
        "alembic.ini": ["Alembic (DB Migrations)"],
    }

    for indicator, framework_info in indicators.items():
        check_path = repo_path / indicator
        if check_path.exists():
            frameworks.append({
                "indicator": indicator,
                "frameworks": framework_info,
            })

    return frameworks


def find_documentation(repo_path: Path) -> list:
    """Find existing documentation files."""
    doc_patterns = [
        "README.md", "README.rst", "README.txt",
        "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE",
        "docs/", "documentation/", "wiki/",
        "CLAUDE.md", "AGENTS.md",
    ]

    found_docs = []
    for pattern in doc_patterns:
        check_path = repo_path / pattern
        if check_path.exists():
            found_docs.append(pattern)

    return found_docs


def analyze_repo(repo_path: str) -> dict:
    """Main analysis function."""
    path = Path(repo_path).resolve()

    if not path.exists():
        raise ValueError(f"Repository path does not exist: {path}")

    structure = analyze_directory_structure(path)
    languages = detect_languages(structure["file_counts"])
    frameworks = detect_frameworks(path)
    documentation = find_documentation(path)

    analysis = {
        "repo_path": str(path),
        "repo_name": path.name,
        "structure": {
            "directories": structure["directories"][:50],  # Limit for readability
            "total_directories": len(structure["directories"]),
            "total_files": structure["total_files"],
        },
        "languages": languages,
        "frameworks": frameworks,
        "documentation": documentation,
        "file_types": dict(structure["file_counts"]),
    }

    return analysis


def main():
    parser = argparse.ArgumentParser(description="Analyze repository for AGENTS.md generation")
    parser.add_argument("--path", default=".", help="Path to repository")
    parser.add_argument("--output", help="Output JSON file (optional)")
    args = parser.parse_args()

    try:
        analysis = analyze_repo(args.path)

        output = json.dumps(analysis, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"✓ Analysis saved to {args.output}")
        else:
            print(output)

        # Summary
        print(f"\n✓ Repository: {analysis['repo_name']}")
        print(f"✓ Total files: {analysis['structure']['total_files']}")
        print(f"✓ Languages: {', '.join(l['name'] for l in analysis['languages'][:5])}")
        print(f"✓ Frameworks: {len(analysis['frameworks'])} detected")

    except Exception as e:
        print(f"✗ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
