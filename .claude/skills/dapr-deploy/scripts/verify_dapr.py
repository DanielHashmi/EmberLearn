#!/usr/bin/env python3
"""Verify Dapr installation and components."""

import subprocess
import sys
import json


def run_command(cmd: list[str]) -> tuple[bool, str]:
    """Run command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_dapr_pods():
    """Check if Dapr control plane pods are running."""
    # WSL/Windows compatibility
    try:
        kubectl = ["minikube.exe", "kubectl", "--"]
        subprocess.run(kubectl + ["version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        kubectl = ["kubectl"]

    success, output = run_command(
        kubectl + ["get", "pods", "-n", "dapr-system", "-o", "json"]
    )

    if not success:
        print("✗ Failed to get Dapr pods")
        return False

    try:
        pods = json.loads(output)
        running_pods = [
            p for p in pods["items"]
            if p["status"]["phase"] == "Running"
        ]

        if len(running_pods) >= 3:  # operator, placement, sidecar-injector
            print(f"✓ Dapr control plane running ({len(running_pods)} pods)")
            return True
        else:
            print(f"✗ Dapr control plane incomplete ({len(running_pods)}/3+ pods)")
            return False
    except (json.JSONDecodeError, KeyError) as e:
        print(f"✗ Failed to parse Dapr pods: {e}")
        return False


def check_dapr_components():
    """Check if Dapr components are configured."""
    try:
        kubectl = ["minikube.exe", "kubectl", "--"]
        subprocess.run(kubectl + ["version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        kubectl = ["kubectl"]

    success, output = run_command(
        kubectl + ["get", "components", "-o", "json"]
    )

    if not success:
        print("✗ Failed to get Dapr components")
        return False

    try:
        components = json.loads(output)
        component_names = [c["metadata"]["name"] for c in components["items"]]

        required = ["statestore", "kafka-pubsub"]
        missing = [c for c in required if c not in component_names]

        if not missing:
            print(f"✓ Dapr components configured: {', '.join(component_names)}")
            return True
        else:
            print(f"✗ Missing Dapr components: {', '.join(missing)}")
            return False
    except (json.JSONDecodeError, KeyError) as e:
        print(f"✗ Failed to parse Dapr components: {e}")
        return False


def main():
    print("Verifying Dapr installation...\n")

    checks = [
        check_dapr_pods(),
        check_dapr_components(),
    ]

    if all(checks):
        print("\n✓ Dapr deployed and configured")
        sys.exit(0)
    else:
        print("\n✗ Dapr verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
