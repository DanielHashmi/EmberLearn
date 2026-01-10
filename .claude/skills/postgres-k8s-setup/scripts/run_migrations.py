#!/usr/bin/env python3
"""Run Alembic migrations against PostgreSQL."""

import argparse
import os
import subprocess
import sys


def run_migrations(migrations_path: str, database_url: str) -> bool:
    """Run Alembic migrations."""
    env = os.environ.copy()
    env["DATABASE_URL"] = database_url

    # Change to migrations directory
    original_dir = os.getcwd()
    os.chdir(migrations_path)

    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            env=env,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✓ Migrations applied successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("✗ Migration failed")
            print(result.stderr)
            return False
    finally:
        os.chdir(original_dir)


def main():
    parser = argparse.ArgumentParser(description="Run Alembic migrations")
    parser.add_argument("--migrations-path", default="backend/database",
                        help="Path to migrations directory")
    parser.add_argument("--database-url",
                        default="postgresql+asyncpg://emberlearn:emberlearn@localhost:5432/emberlearn",
                        help="Database connection URL")
    args = parser.parse_args()

    print("Running database migrations...")
    print(f"  Migrations path: {args.migrations_path}")

    if not os.path.exists(args.migrations_path):
        print(f"✗ Migrations path not found: {args.migrations_path}")
        sys.exit(1)

    if run_migrations(args.migrations_path, args.database_url):
        print("\n✓ All migrations complete!")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
