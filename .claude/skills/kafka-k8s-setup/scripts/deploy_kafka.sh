#!/bin/bash
# Deploy Kafka to Kubernetes using Confluent Platform images
# MCP Code Execution Pattern: Script executes outside context, only result enters context

set -e

# WSL/Windows compatibility - use minikube kubectl wrapper
KUBECTL="minikube.exe kubectl --"

NAMESPACE="${KAFKA_NAMESPACE:-kafka}"

echo "Deploying Kafka to Kubernetes..."
echo "  Namespace: $NAMESPACE"

# Create namespace if not exists
$KUBECTL create namespace "$NAMESPACE" --dry-run=client -o yaml | $KUBECTL apply -f - >/dev/null 2>&1

# Deploy Zookeeper
cat <<EOF | $KUBECTL apply -f -
apiVersion: v1
kind: Service
metadata:
  name: zookeeper
  namespace: $NAMESPACE
spec:
  ports:
  - port: 2181
    name: client
  clusterIP: None
  selector:
    app: zookeeper
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: zookeeper
  namespace: $NAMESPACE
spec:
  serviceName: zookeeper
  replicas: 1
  selector:
    matchLabels:
      app: zookeeper
  template:
    metadata:
      labels:
        app: zookeeper
    spec:
      containers:
      - name: zookeeper
        image: confluentinc/cp-zookeeper:7.5.0
        ports:
        - containerPort: 2181
        env:
        - name: ZOOKEEPER_CLIENT_PORT
          value: "2181"
        - name: ZOOKEEPER_TICK_TIME
          value: "2000"
EOF

echo "Waiting for Zookeeper..."
sleep 30

# Deploy Kafka
cat <<EOF | $KUBECTL apply -f -
apiVersion: v1
kind: Service
metadata:
  name: kafka
  namespace: $NAMESPACE
spec:
  ports:
  - port: 9092
    name: client
  clusterIP: None
  selector:
    app: kafka
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: kafka
  namespace: $NAMESPACE
spec:
  serviceName: kafka
  replicas: 1
  selector:
    matchLabels:
      app: kafka
  template:
    metadata:
      labels:
        app: kafka
    spec:
      containers:
      - name: kafka
        image: confluentinc/cp-kafka:7.5.0
        ports:
        - containerPort: 9092
        env:
        - name: KAFKA_BROKER_ID
          value: "1"
        - name: KAFKA_ZOOKEEPER_CONNECT
          value: "zookeeper.kafka.svc.cluster.local:2181"
        - name: KAFKA_ADVERTISED_LISTENERS
          value: "PLAINTEXT://kafka-0.kafka.kafka.svc.cluster.local:9092"
        - name: KAFKA_LISTENER_SECURITY_PROTOCOL_MAP
          value: "PLAINTEXT:PLAINTEXT"
        - name: KAFKA_INTER_BROKER_LISTENER_NAME
          value: "PLAINTEXT"
        - name: KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR
          value: "1"
        - name: KAFKA_AUTO_CREATE_TOPICS_ENABLE
          value: "true"
EOF

echo "Waiting for Kafka..."
sleep 60

echo ""
echo "✓ Kafka deployed successfully!"
echo ""
echo "Connection info:"
echo "  Internal: kafka-0.kafka.kafka.svc.cluster.local:9092"
