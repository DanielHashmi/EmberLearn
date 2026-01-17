# Kafka Kubernetes Setup - Reference

## Overview

This skill deploys Apache Kafka on Kubernetes using the Bitnami Helm chart, providing a production-ready event streaming platform for microservices communication.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Kafka-0   │  │   Kafka-1   │  │   Kafka-2   │     │
│  │  (Broker)   │  │  (Broker)   │  │  (Broker)   │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │                              │
│                 ┌────────┴────────┐                     │
│                 │    Zookeeper    │                     │
│                 └─────────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `KAFKA_NAMESPACE` | `kafka` | Kubernetes namespace |
| `KAFKA_RELEASE` | `kafka` | Helm release name |
| `KAFKA_REPLICAS` | `1` | Number of Kafka brokers |

### Helm Values

```yaml
# Custom values.yaml
replicaCount: 3
persistence:
  enabled: true
  size: 20Gi
zookeeper:
  enabled: true
  replicaCount: 3
listeners:
  client:
    protocol: PLAINTEXT
  controller:
    protocol: PLAINTEXT
```

## EmberLearn Topics

| Topic | Purpose | Partition Key |
|-------|---------|---------------|
| `learning.query` | Student queries to AI agents | `student_id` |
| `learning.response` | AI agent responses | `student_id` |
| `code.submitted` | Code submissions for execution | `student_id` |
| `code.executed` | Execution results | `student_id` |
| `exercise.created` | New exercise generation | `topic_id` |
| `exercise.completed` | Exercise completion events | `student_id` |
| `struggle.detected` | Struggle detection alerts | `student_id` |
| `struggle.resolved` | Alert resolution events | `alert_id` |

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n kafka -l app.kubernetes.io/name=kafka

# Check pod logs
kubectl logs -n kafka kafka-0

# Check events
kubectl get events -n kafka --sort-by='.lastTimestamp'
```

### Connection Issues

```bash
# Test internal connectivity
kubectl exec -n kafka kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --list

# Port forward for local testing
kubectl port-forward -n kafka svc/kafka 9092:9092
```

### Topic Creation Failures

```bash
# List existing topics
kubectl exec -n kafka kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --list

# Describe topic
kubectl exec -n kafka kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic learning.query
```

## Performance Tuning

### For Development (Minikube)
- 1 broker, 1 Zookeeper
- 8Gi storage
- 3 partitions per topic

### For Production
- 3+ brokers across availability zones
- 3 Zookeeper nodes
- 20Gi+ storage with SSD
- 6+ partitions per topic
- Replication factor of 3

## Security Considerations

- Use SASL/SCRAM authentication in production
- Enable TLS for inter-broker communication
- Configure network policies to restrict access
- Use Kubernetes Secrets for credentials
