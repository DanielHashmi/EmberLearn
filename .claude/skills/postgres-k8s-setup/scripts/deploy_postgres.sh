#!/bin/bash
# Deploy PostgreSQL to Kubernetes using simple manifests
# MCP Code Execution Pattern: Script executes outside context, only result enters context

set -e

# WSL/Windows compatibility - use minikube kubectl wrapper
KUBECTL="minikube.exe kubectl --"

NAMESPACE="${POSTGRES_NAMESPACE:-default}"
DATABASE="${POSTGRES_DATABASE:-emberlearn}"
USERNAME="${POSTGRES_USERNAME:-emberlearn}"
PASSWORD="${POSTGRES_PASSWORD:-emberlearn}"

echo "Deploying PostgreSQL to Kubernetes..."
echo "  Namespace: $NAMESPACE"
echo "  Database: $DATABASE"

# Create namespace if not exists
$KUBECTL create namespace "$NAMESPACE" --dry-run=client -o yaml | $KUBECTL apply -f - >/dev/null 2>&1

# Deploy PostgreSQL
cat <<EOF | $KUBECTL apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: $NAMESPACE
type: Opaque
stringData:
  POSTGRES_DB: $DATABASE
  POSTGRES_USER: $USERNAME
  POSTGRES_PASSWORD: $PASSWORD
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  ports:
  - port: 5432
    name: postgres
  clusterIP: None
  selector:
    app: postgres
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: $NAMESPACE
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
        envFrom:
        - secretRef:
            name: postgres-secret
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
EOF

echo "Waiting for PostgreSQL..."
sleep 30

echo ""
echo "✓ PostgreSQL deployed successfully!"
echo ""
echo "Connection info:"
echo "  Host: postgres-0.postgres.$NAMESPACE.svc.cluster.local"
echo "  Port: 5432"
echo "  Database: $DATABASE"
echo "  Username: $USERNAME"
