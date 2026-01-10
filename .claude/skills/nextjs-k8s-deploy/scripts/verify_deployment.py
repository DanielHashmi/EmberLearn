#!/usr/bin/env python3
"""Verify Next.js deployment to Kubernetes."""

import argparse
import subprocess
import sys
import time


def run_kubectl(args: list[str]) -> tuple[int, str]:
    """Run kubectl command and return result."""
    cmd = ["kubectl"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()


def check_deployment(name: str, namespace: str) -> bool:
    """Check if deployment is ready."""
    code, output = run_kubectl([
        "get", "deployment", name, "-n", namespace,
        "-o", "jsonpath={.status.readyReplicas}"
    ])
    if code != 0:
        return False
    try:
        ready = int(output) if output else 0
        return ready > 0
    except ValueError:
        return False


def check_service(name: str, namespace: str) -> bool:
    """Check if service exists."""
    code, _ = run_kubectl(["get", "service", name, "-n", namespace])
    return code == 0


def check_pods(name: str, namespace: str) -> tuple[bool, int, int]:
    """Check pod status."""
    code, output = run_kubectl([
        "get", "pods", "-n", namespace,
        "-l", f"app={name}",
        "-o", "jsonpath={.items[*].status.phase}"
    ])
    if code != 0:
        return False, 0, 0

    phases = output.split() if output else []
    running = sum(1 for p in phases if p == "Running")
    total = len(phases)
    return running == total and total > 0, running, total


def check_health_endpoint(name: str, namespace: str) -> bool:
    """Check if health endpoint responds."""
    # Port forward and check health
    code, output = run_kubectl([
        "exec", "-n", namespace,
        f"deployment/{name}", "--",
        "wget", "-q", "-O-", "http://localhost:3000/api/health"
    ])
    return code == 0


def verify_deployment(name: str, namespace: str) -> bool:
    """Run all verification checks."""
    print(f"Verifying Next.js deployment: {name}")
    print(f"Namespace: {namespace}")
    print()

    checks_passed = 0
    checks_failed = 0

    # Check deployment
    print("Checking deployment...", end=" ")
    if check_deployment(name, namespace):
        print("✓")
        checks_passed += 1
    else:
        print("✗")
        checks_failed += 1

    # Check service
    print("Checking service...", end=" ")
    if check_service(name, namespace):
        print("✓")
        checks_passed += 1
    else:
        print("✗")
        checks_failed += 1

    # Check pods
    print("Checking pods...", end=" ")
    pods_ok, running, total = check_pods(name, namespace)
    if pods_ok:
        print(f"✓ ({running}/{total} running)")
        checks_passed += 1
    else:
        print(f"✗ ({running}/{total} running)")
        checks_failed += 1

    # Summary
    print()
    if checks_failed > 0:
        print(f"✗ Verification failed: {checks_passed} passed, {checks_failed} failed")
        return False
    else:
        print(f"✓ All {checks_passed} checks passed!")
        print()
        print("Access the application:")
        print(f"  kubectl port-forward svc/{name} 3000:80 -n {namespace}")
        print("  Then open: http://localhost:3000")
        return True


def main():
    parser = argparse.ArgumentParser(description="Verify Next.js K8s deployment")
    parser.add_argument("name", help="Deployment name")
    parser.add_argument("--namespace", "-n", default="default", help="Kubernetes namespace")
    parser.add_argument("--wait", "-w", type=int, default=0,
                        help="Wait seconds for deployment to be ready")
    args = parser.parse_args()

    if args.wait > 0:
        print(f"Waiting {args.wait}s for deployment...")
        time.sleep(args.wait)

    success = verify_deployment(args.name, args.namespace)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
