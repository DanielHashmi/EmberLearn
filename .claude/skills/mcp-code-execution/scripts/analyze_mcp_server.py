#!/usr/bin/env python3
"""Analyze an MCP server to understand its tools and capabilities."""

import argparse
import json
import sys
from pathlib import Path


def analyze_mcp_config(config_path: Path) -> dict:
    """Analyze MCP server configuration."""
    if not config_path.exists():
        return {"error": f"Config not found: {config_path}"}

    with open(config_path) as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    analysis = {
        "servers": [],
        "total_servers": len(servers),
    }

    for name, server_config in servers.items():
        server_info = {
            "name": name,
            "command": server_config.get("command", "unknown"),
            "args": server_config.get("args", []),
            "env_vars": list(server_config.get("env", {}).keys()),
        }
        analysis["servers"].append(server_info)

    return analysis


def estimate_token_cost(server_info: dict) -> dict:
    """Estimate token cost of loading MCP tools into context."""
    # Rough estimates based on typical MCP tool definitions
    TOKENS_PER_TOOL = 150  # Average tokens per tool definition
    TOKENS_PER_SCHEMA = 50  # Average tokens per parameter schema

    # Common MCP servers and their typical tool counts
    KNOWN_SERVERS = {
        "filesystem": {"tools": 8, "description": "File operations"},
        "github": {"tools": 15, "description": "GitHub API operations"},
        "postgres": {"tools": 5, "description": "PostgreSQL queries"},
        "sqlite": {"tools": 5, "description": "SQLite operations"},
        "puppeteer": {"tools": 10, "description": "Browser automation"},
        "brave-search": {"tools": 2, "description": "Web search"},
        "fetch": {"tools": 1, "description": "HTTP fetch"},
    }

    server_name = server_info.get("name", "").lower()

    # Try to match known server
    for known, info in KNOWN_SERVERS.items():
        if known in server_name:
            tool_count = info["tools"]
            return {
                "server": server_info["name"],
                "estimated_tools": tool_count,
                "estimated_tokens": tool_count * TOKENS_PER_TOOL,
                "description": info["description"],
            }

    # Default estimate for unknown servers
    return {
        "server": server_info["name"],
        "estimated_tools": 5,
        "estimated_tokens": 5 * TOKENS_PER_TOOL,
        "description": "Unknown server type",
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze MCP server configuration")
    parser.add_argument("--config", "-c", type=Path,
                        default=Path.home() / ".claude" / "claude_desktop_config.json",
                        help="Path to MCP config file")
    parser.add_argument("--json", "-j", action="store_true",
                        help="Output as JSON")
    args = parser.parse_args()

    analysis = analyze_mcp_config(args.config)

    if "error" in analysis:
        print(f"✗ {analysis['error']}")
        sys.exit(1)

    if args.json:
        print(json.dumps(analysis, indent=2))
        return

    print("MCP Server Analysis")
    print("=" * 50)
    print(f"Total servers configured: {analysis['total_servers']}")
    print()

    total_tokens = 0
    for server in analysis["servers"]:
        token_estimate = estimate_token_cost(server)
        total_tokens += token_estimate["estimated_tokens"]

        print(f"Server: {server['name']}")
        print(f"  Command: {server['command']}")
        print(f"  Args: {' '.join(server['args'])}")
        print(f"  Env vars: {', '.join(server['env_vars']) or 'none'}")
        print(f"  Est. tools: {token_estimate['estimated_tools']}")
        print(f"  Est. tokens: {token_estimate['estimated_tokens']}")
        print()

    print("=" * 50)
    print(f"Total estimated context tokens: {total_tokens}")
    print()
    print("💡 Using MCP Code Execution pattern can reduce this to ~100 tokens per skill")


if __name__ == "__main__":
    main()
