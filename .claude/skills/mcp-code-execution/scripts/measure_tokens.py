#!/usr/bin/env python3
"""Measure token efficiency of MCP code execution pattern vs direct MCP."""

import argparse
import json
from pathlib import Path


# Approximate tokens per character (GPT tokenizer average)
CHARS_PER_TOKEN = 4


def count_tokens(text: str) -> int:
    """Estimate token count from text."""
    return len(text) // CHARS_PER_TOKEN


def measure_skill(skill_dir: Path) -> dict:
    """Measure token usage for a skill."""
    skill_md = skill_dir / "SKILL.md"
    reference_md = skill_dir / "REFERENCE.md"
    scripts_dir = skill_dir / "scripts"

    result = {
        "skill_name": skill_dir.name,
        "skill_md_tokens": 0,
        "reference_md_tokens": 0,
        "scripts_tokens": 0,
        "total_context_tokens": 0,
    }

    # SKILL.md is always loaded
    if skill_md.exists():
        result["skill_md_tokens"] = count_tokens(skill_md.read_text(encoding='utf-8'))

    # REFERENCE.md is loaded on-demand (not counted in context)
    if reference_md.exists():
        result["reference_md_tokens"] = count_tokens(reference_md.read_text(encoding='utf-8'))

    # Scripts execute outside context (0 tokens)
    if scripts_dir.is_dir():
        total_script_chars = 0
        for script in scripts_dir.glob("*"):
            if script.is_file():
                try:
                    total_script_chars += len(script.read_text(encoding='utf-8'))
                except UnicodeDecodeError:
                    total_script_chars += len(script.read_bytes())
        result["scripts_tokens"] = count_tokens(str(total_script_chars))
        result["scripts_tokens_if_loaded"] = total_script_chars // CHARS_PER_TOKEN

    # Only SKILL.md counts toward context
    result["total_context_tokens"] = result["skill_md_tokens"]

    return result


def estimate_direct_mcp_tokens(skill_name: str) -> int:
    """Estimate tokens if using direct MCP tool loading."""
    # Based on typical MCP tool definitions
    ESTIMATES = {
        "kafka-k8s-setup": 800,      # Multiple Kafka management tools
        "postgres-k8s-setup": 600,   # Database tools
        "fastapi-dapr-agent": 500,   # Scaffolding tools
        "mcp-code-execution": 400,   # Meta-skill
        "nextjs-k8s-deploy": 700,    # Build and deploy tools
        "docusaurus-deploy": 500,    # Documentation tools
        "agents-md-gen": 300,        # Analysis tools
    }
    return ESTIMATES.get(skill_name, 500)


def main():
    parser = argparse.ArgumentParser(description="Measure token efficiency")
    parser.add_argument("skill_dir", type=Path, nargs="?",
                        help="Path to skill directory (or measure all)")
    parser.add_argument("--all", "-a", action="store_true",
                        help="Measure all skills in .claude/skills/")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    skills_to_measure = []

    if args.all or args.skill_dir is None:
        skills_root = Path(".claude/skills")
        if skills_root.exists():
            skills_to_measure = [d for d in skills_root.iterdir() if d.is_dir()]
    else:
        skills_to_measure = [args.skill_dir]

    results = []
    for skill_dir in skills_to_measure:
        measurement = measure_skill(skill_dir)
        measurement["direct_mcp_estimate"] = estimate_direct_mcp_tokens(skill_dir.name)
        measurement["savings_tokens"] = (
            measurement["direct_mcp_estimate"] - measurement["total_context_tokens"]
        )
        measurement["savings_percent"] = round(
            (measurement["savings_tokens"] / measurement["direct_mcp_estimate"]) * 100, 1
        )
        results.append(measurement)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    # Print report
    print("Token Efficiency Report")
    print("=" * 70)
    print()
    print(f"{'Skill':<25} {'Context':<10} {'Direct MCP':<12} {'Savings':<10} {'%':<8}")
    print("-" * 70)

    total_context = 0
    total_direct = 0

    for r in results:
        total_context += r["total_context_tokens"]
        total_direct += r["direct_mcp_estimate"]
        print(
            f"{r['skill_name']:<25} "
            f"{r['total_context_tokens']:<10} "
            f"{r['direct_mcp_estimate']:<12} "
            f"{r['savings_tokens']:<10} "
            f"{r['savings_percent']:<8}%"
        )

    print("-" * 70)
    total_savings = total_direct - total_context
    total_percent = round((total_savings / total_direct) * 100, 1) if total_direct > 0 else 0
    print(
        f"{'TOTAL':<25} "
        f"{total_context:<10} "
        f"{total_direct:<12} "
        f"{total_savings:<10} "
        f"{total_percent:<8}%"
    )
    print()
    print(f"💡 MCP Code Execution pattern saves ~{total_percent}% of context tokens")


if __name__ == "__main__":
    main()
