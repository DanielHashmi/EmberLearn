#!/usr/bin/env python3
"""Validate EmberLearn infrastructure components."""

import argparse
import subprocess
import sys
import json


def run_kubectl(args: list[str]) -> tuple[int, str, str]:
    """Run kubectl command and return result."""
    cmd = ["kubectl"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_pods(namespace: str, label: str, expected_count: int = 1) -> tuple[bool, str]:
    """Check if pods are running."""
    code, stdout, _ = run_kubectl([
        "get", "pods", "-n", namespace, "-l", label,
        "-o", "jsonpath={.items[*].status.phase}"
    ])
    if code != 0:
        return False, "Failed to get pods"

    phases = stdout.split() if stdout else []
    running = sum(1 for p in phases if p == "Running")

    if running >= expected_count:
        return True, f"{running} pod(s) running"
    return False, f"Only {running}/{expected_count} pod(s) running"


def check_service(namespace: str, name: str) -> tuple[bool, str]:
    """Check if service exists."""
    code, _, _ = run_kubectl(["get", "service", name, "-n", namespace])
    if code == 0:
        return True, "Service exists"
    return False, "Service not found"


def check_dapr_component(name: str) -> tuple[bool, str]:
    """Check if Dapr component is loaded."""
    code, stdout, _ = run_kubectl([
        "get", "components.dapr.io", name, "-o", "jsonpath={.metadata.name}"
    ])
    if code == 0 and stdout == name:
        return True, "Component loaded"
    return False, "Component not found"


def validate_infrastructure() -> bool:
    """Run all infrastructure validation checks."""
    print("EmberLearn Infrastructure Validation")
    print("=" * 50)
    print()

    checks = []

    # Kafka checks
    print("Kafka:")
    ok, msg = check_pods("kafka", "app.kubernetes.io/name=kafka")
    print(f"  {'✓' if ok else '✗'} Kafka broker: {msg}")
    checks.append(ok)

    ok, msg = check_service("kafka", "kafka")
    print(f"  {'✓' if ok else '✗'} Kafka service: {msg}")
    checks.append(ok)

    # PostgreSQL checks
    print("\nPostgreSQL:")
    ok, msg = check_pods("default", "app.kubernetes.io/name=postgresql")
    print(f"  {'✓' if ok else '✗'} PostgreSQL pod: {msg}")
    checks.append(ok)

    ok, msg = check_service("default", "postgresql")
    print(f"  {'✓' if ok else '✗'} PostgreSQL service: {msg}")
    checks.append(ok)

    # Dapr checks
    print("\nDapr Components:")
    ok, msg = check_dapr_component("statestore")
    print(f"  {'✓' if ok else '✗'} State store: {msg}")
    checks.append(ok)

    ok, msg = check_dapr_component("kafka-pubsub")
    print(f"  {'✓' if ok else '✗'} Pub/sub: {msg}")
    checks.append(ok)

    # Kong checks
    print("\nKong API Gateway:")
    ok, msg = check_pods("default", "app.kubernetes.io/name=kong")
    print(f"  {'✓' if ok else '✗'} Kong pod: {msg}")
    checks.append(ok)

    ok, msg = check_service("default", "kong-proxy")
    print(f"  {'✓' if ok else '✗'} Kong proxy service: {msg}")
    checks.append(ok)

    # Summary
    print()
    print("=" * 50)
    passed = sum(checks)
    total = len(checks)

    if passed == total:
        print(f"✓ All {total} checks passed!")
        return True
    else:
        print(f"✗ {passed}/{total} checks passed")
        return False


def main():
    parser = argparse.ArgumentParser(description="Validate EmberLearn infrastructure")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    success = validate_infrastructure()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
