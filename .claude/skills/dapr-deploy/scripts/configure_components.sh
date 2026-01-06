#!/bin/bash
set -euo pipefail

# Configure Dapr components (state store, pub/sub)

# WSL/Windows compatibility
if command -v minikube.exe &> /dev/null; then
    KUBECTL="minikube.exe kubectl --"
else
    KUBECTL="kubectl"
fi

COMPONENTS_DIR="$(dirname "$0")/dapr-components"
mkdir -p "$COMPONENTS_DIR"

echo "Creating Dapr component configurations..."

# State store component (PostgreSQL)
cat > "$COMPONENTS_DIR/statestore.yaml" <<'EOF'
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
  - name: connectionString
    secretKeyRef:
      name: postgres-secret
      key: connection-string
EOF

# Pub/sub component (Kafka)
cat > "$COMPONENTS_DIR/pubsub.yaml" <<'EOF'
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "kafka-service.kafka:9092"
  - name: consumerGroup
    value: "emberlearn"
  - name: authType
    value: "none"
EOF

# Apply components
$KUBECTL apply -f "$COMPONENTS_DIR/statestore.yaml"
$KUBECTL apply -f "$COMPONENTS_DIR/pubsub.yaml"

echo "✓ Dapr components configured (statestore, pubsub)"
