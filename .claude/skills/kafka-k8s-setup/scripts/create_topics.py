#!/usr/bin/env python3
"""Create Kafka topics for EmberLearn."""

import argparse
import subprocess
import sys


def create_topic(namespace: str, release: str, topic: str, partitions: int = 3) -> bool:
    """Create a Kafka topic."""
    cmd = [
        "kubectl", "-n", namespace, "exec", f"{release}-0", "--",
        "kafka-topics.sh", "--bootstrap-server", "localhost:9092",
        "--create", "--topic", topic,
        "--partitions", str(partitions),
        "--replication-factor", "1",
        "--if-not-exists"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Create Kafka topics")
    parser.add_argument("topics", nargs="*", default=[
        "learning.query", "learning.response",
        "code.submitted", "code.executed",
        "exercise.created", "exercise.completed",
        "struggle.detected", "struggle.resolved"
    ], help="Topics to create")
    parser.add_argument("--namespace", default="kafka", help="Kubernetes namespace")
    parser.add_argument("--release", default="kafka", help="Helm release name")
    parser.add_argument("--partitions", type=int, default=3, help="Number of partitions")
    args = parser.parse_args()

    print(f"Creating {len(args.topics)} Kafka topics...")

    success = 0
    for topic in args.topics:
        print(f"  Creating {topic}...", end=" ")
        if create_topic(args.namespace, args.release, topic, args.partitions):
            print("✓")
            success += 1
        else:
            print("✗")

    print(f"\n✓ Created {success}/{len(args.topics)} topics")

    if success < len(args.topics):
        sys.exit(1)


if __name__ == "__main__":
    main()
