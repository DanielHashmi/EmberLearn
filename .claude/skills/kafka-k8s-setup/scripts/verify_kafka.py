#!/usr/bin/env python3
"""Verify Kafka deployment and test pub/sub functionality.
MCP Code Execution Pattern: Script executes outside context, only result enters context.
"""

import argparse
import subprocess
import sys
import time


def run_kubectl(args: list[str], namespace: str = "kafka") -> tuple[int, str, str]:
    """Run kubectl command via minikube wrapper and return exit code, stdout, stderr."""
    # Use minikube kubectl wrapper for WSL/Windows compatibility
    cmd = ["minikube.exe", "kubectl", "--", "-n", namespace] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def check_pods_running(namespace: str, label: str) -> bool:
    """Check if pods with given label are running."""
    code, stdout, _ = run_kubectl(
        ["get", "pods", "-l", label, "-o", "jsonpath={.items[*].status.phase}"],
        namespace
    )
    if code != 0:
        return False
    phases = stdout.strip().split()
    return all(phase == "Running" for phase in phases) and len(phases) > 0


def check_kafka_brokers(namespace: str, release: str) -> bool:
    """Check if Kafka brokers are running."""
    return check_pods_running(namespace, f"app.kubernetes.io/instance={release}")


def check_zookeeper(namespace: str, release: str) -> bool:
    """Check if Zookeeper is running."""
    return check_pods_running(namespace, f"app.kubernetes.io/name=zookeeper,app.kubernetes.io/instance={release}")


def test_kafka_connection(namespace: str, release: str) -> bool:
    """Test Kafka connection by listing topics."""
    code, stdout, stderr = run_kubectl([
        "exec", f"{release}-0", "--",
        "kafka-topics.sh", "--bootstrap-server", "localhost:9092", "--list"
    ], namespace)
    return code == 0


def create_test_topic(namespace: str, release: str, topic: str) -> bool:
    """Create a test topic."""
    code, _, _ = run_kubectl([
        "exec", f"{release}-0", "--",
        "kafka-topics.sh", "--bootstrap-server", "localhost:9092",
        "--create", "--topic", topic, "--partitions", "1", "--replication-factor", "1",
        "--if-not-exists"
    ], namespace)
    return code == 0


def main():
    parser = argparse.ArgumentParser(description="Verify Kafka deployment")
    parser.add_argument("--namespace", default="kafka", help="Kubernetes namespace")
    parser.add_argument("--release", default="kafka", help="Helm release name")
    parser.add_argument("--create-topics", nargs="*", help="Topics to create")
    args = parser.parse_args()

    print("Verifying Kafka deployment...")
    print(f"  Namespace: {args.namespace}")
    print(f"  Release: {args.release}")
    print()

    # Check Kafka brokers
    print("Checking Kafka brokers...", end=" ")
    if check_kafka_brokers(args.namespace, args.release):
        print("✓ Running")
    else:
        print("✗ Not running")
        sys.exit(1)

    # Check Zookeeper
    print("Checking Zookeeper...", end=" ")
    if check_zookeeper(args.namespace, args.release):
        print("✓ Running")
    else:
        print("✗ Not running")
        sys.exit(1)

    # Test connection
    print("Testing Kafka connection...", end=" ")
    time.sleep(2)  # Give pods time to be fully ready
    if test_kafka_connection(args.namespace, args.release):
        print("✓ Connected")
    else:
        print("✗ Connection failed")
        sys.exit(1)

    # Create topics if specified
    if args.create_topics:
        print()
        print("Creating topics...")
        for topic in args.create_topics:
            print(f"  Creating {topic}...", end=" ")
            if create_test_topic(args.namespace, args.release, topic):
                print("✓")
            else:
                print("✗")

    print()
    print("✓ Kafka verification complete!")


if __name__ == "__main__":
    main()
