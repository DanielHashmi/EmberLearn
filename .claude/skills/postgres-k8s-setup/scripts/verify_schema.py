#!/usr/bin/env python3
"""Verify PostgreSQL schema after migrations."""

import argparse
import subprocess
import sys


EXPECTED_TABLES = [
    "users", "topics", "progress", "exercises", "test_cases",
    "exercise_submissions", "quizzes", "quiz_attempts", "struggle_alerts"
]


def run_psql(namespace: str, release: str, query: str) -> tuple[int, str]:
    """Run psql query and return result."""
    cmd = [
        "kubectl", "-n", namespace, "exec", f"{release}-0", "--",
        "psql", "-U", "emberlearn", "-d", "emberlearn", "-t", "-c", query
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def check_table_exists(namespace: str, release: str, table: str) -> bool:
    """Check if a table exists."""
    query = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');"
    code, output = run_psql(namespace, release, query)
    return code == 0 and "t" in output.lower()


def get_table_columns(namespace: str, release: str, table: str) -> list[str]:
    """Get column names for a table."""
    query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table}';"
    code, output = run_psql(namespace, release, query)
    if code == 0:
        return [col.strip() for col in output.split("\n") if col.strip()]
    return []


def main():
    parser = argparse.ArgumentParser(description="Verify PostgreSQL schema")
    parser.add_argument("--namespace", default="default", help="Kubernetes namespace")
    parser.add_argument("--release", default="postgresql", help="Helm release name")
    args = parser.parse_args()

    print("Verifying PostgreSQL schema...")
    print(f"  Namespace: {args.namespace}")
    print(f"  Release: {args.release}")
    print()

    # Check each expected table
    missing = []
    for table in EXPECTED_TABLES:
        print(f"  Checking {table}...", end=" ")
        if check_table_exists(args.namespace, args.release, table):
            columns = get_table_columns(args.namespace, args.release, table)
            print(f"✓ ({len(columns)} columns)")
        else:
            print("✗ Missing")
            missing.append(table)

    print()
    if missing:
        print(f"✗ Missing tables: {', '.join(missing)}")
        sys.exit(1)
    else:
        print(f"✓ All {len(EXPECTED_TABLES)} tables verified!")


if __name__ == "__main__":
    main()
