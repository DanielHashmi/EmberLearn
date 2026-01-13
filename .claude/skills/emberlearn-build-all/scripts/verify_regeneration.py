#!/usr/bin/env python3
"""Verify a regenerated EmberLearn output directory.

Definition of "exact" here is *functional exactness*:
- required directories exist
- required entrypoints exist
- key dependencies are present

Output is intentionally minimal for Hackathon III scoring/logging.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def require_path(root: Path, rel: str) -> None:
    p = root / rel
    if not p.exists():
        raise AssertionError(f"missing: {rel}")


def require_any(root: Path, rels: list[str], label: str) -> str:
    for rel in rels:
        if (root / rel).exists():
            return rel
    raise AssertionError(f"missing: {label}")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: verify_regeneration.py <output_dir>")
        return 2

    root = Path(argv[1]).resolve()

    try:
        require_path(root, "backend")
        require_path(root, "frontend")
        require_path(root, "docs")
        require_path(root, "specs")

        # Local monolith backend expectations
        require_path(root, "backend/main.py")
        require_path(root, "backend/routers")
        require_any(
            root,
            [
                "backend/routers/auth.py",
                "backend/routers/chat.py",
                "backend/routers/exercises.py",
                "backend/routers/execute.py",
                "backend/routers/progress.py",
            ],
            "backend routers",
        )

        # Frontend expectations
        require_path(root, "frontend/package.json")
        require_path(root, "frontend/app")
        require_any(root, ["frontend/app/layout.tsx", "frontend/app/layout.ts"], "frontend layout")

        pkg = read_json(root / "frontend/package.json")
        deps = {
            **(pkg.get("dependencies") or {}),
            **(pkg.get("devDependencies") or {}),
        }

        for dep in ["next", "react", "tailwindcss", "@monaco-editor/react"]:
            if dep not in deps:
                raise AssertionError(f"frontend missing dependency: {dep}")

        # Production-grade hints (should be present in current repo)
        for dep in ["framer-motion", "next-themes"]:
            if dep not in deps:
                raise AssertionError(f"frontend missing expected dep: {dep}")

        # K8s expectations (for target=both; we keep it permissive but check structure if present)
        if (root / "k8s").exists():
            require_any(root, ["k8s/agents", "k8s/manifests"], "k8s agents/manifests")
            require_any(root, ["k8s/dapr"], "k8s dapr")
            require_any(root, ["k8s/kong"], "k8s kong")
            require_any(root, ["k8s/frontend"], "k8s frontend")

        # Docs expectations (current repo uses docs/docs)
        require_any(root, ["docs/docs"], "docs content")

    except AssertionError as e:
        print(f"ERROR verify failed: {e}")
        return 1

    print("OK verify passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
