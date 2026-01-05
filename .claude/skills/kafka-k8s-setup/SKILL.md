---
name: kafka-k8s-setup
description: Deploy Kafka on Kubernetes via Bitnami Helm
---

# Kafka Kubernetes Setup

## When to Use
- Deploy Kafka for event streaming
- Setup messaging infrastructure

## Instructions
1. `./scripts/check_prereqs.sh`
2. `./scripts/deploy_kafka.sh`
3. `python scripts/create_topics.py`
4. `python scripts/verify_kafka.py`

Rollback: `./scripts/rollback_kafka.sh`

See [REFERENCE.md](./REFERENCE.md) for configuration.
