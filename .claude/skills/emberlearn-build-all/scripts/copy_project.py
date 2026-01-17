#!/usr/bin/env python3
"""Copy the current EmberLearn working project into a fresh output directory.

This supports Hackathon III "functional exactness" regeneration:
- default behavior copies the current working tree (minus heavy/unsafe dirs)
- optional modes to include only local or k8s relevant subtrees

Design goals:
- deterministic copy rules
- minimal, parseable output
- safe defaults (avoid copying node_modules, venvs, caches, git metadata)
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_EXCLUDES = {
    ".git",
    "node_modules",
    "frontend/node_modules",
    "backend/venv",
    "backend/.venv",
    "__pycache__",
    ".pytest_cache",
    ".next",
    "dist",
    "build",
    "nul",
    "_regen",
    "frontend/tsconfig.tsbuildinfo",
}

# We intentionally DO copy `.claude/skills/` and `.specify/` because Hackathon III
# deliverables require the Skills library and spec artifacts to be present in the regenerated output.
# The heavy/generated subtrees above are still excluded.


def should_exclude(rel: Path) -> bool:
    rel_str = rel.as_posix()

    # Exact directory names at root
    if rel_str in DEFAULT_EXCLUDES:
        return True

    # Prefix exclusions (directories/files under excluded roots)
    for ex in DEFAULT_EXCLUDES:
        if rel_str == ex:
            return True
        if rel_str.startswith(ex.rstrip("/") + "/"):
            return True

    return False


def copy_tree(src: Path, dst: Path) -> None:
    for path in src.rglob("*"):
        rel = path.relative_to(src)

        if should_exclude(rel):
            continue

        target = dst / rel

        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--mode", choices=["local", "k8s", "both"], default="both")

    args = parser.parse_args()

    src = Path(args.src).resolve()
    dst = Path(args.dst).resolve()

    if not src.exists():
        raise SystemExit(f"✗ source not found: {src}")

    dst.mkdir(parents=True, exist_ok=True)

    # Copy the whole repo (minus excludes) first.
    copy_tree(src, dst)

    # Optionally prune based on mode
    if args.mode == "local":
        # keep backend/frontend/specs/docs and top-level scripts
        for rel in ["k8s"]:
            p = dst / rel
            if p.exists():
                shutil.rmtree(p)

    elif args.mode == "k8s":
        # keep k8s and agent services; prune local-only top-level convenience docs if desired
        # (We keep most things for now; verifier will enforce required k8s pieces.)
        pass

    print(f"OK Copied project to {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
