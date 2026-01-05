#!/bin/bash
# Deploy all EmberLearn infrastructure components

set -e

echo "Deploying EmberLearn Infrastructure"
echo "===================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
if ! command -v kubectl &> /dev/null; then
    echo "✗ kubectl not found"
    exit 1
fi
echo "✓ kubectl found"

if ! command -v helm &> /dev/null; then
    echo "✗ helm not found"
    exit 1
fi
echo "✓ helm found"

if ! kubectl cluster-info &> /dev/null; then
    echo "✗ Cannot connect to Kubernetes cluster"
    exit 1
fi
echo "✓ Kubernetes cluster accessible"

# Deploy Kafka using skill
echo ""
echo "Deploying Kafka..."
if [ -f ".claude/skills/kafka-k8s-setup/scripts/deploy_kafka.sh" ]; then
    bash .claude/skills/kafka-k8s-setup/scripts/deploy_kafka.sh
    python3 .claude/skills/kafka-k8s-setup/scripts/create_topics.py
else
    echo "⚠ Kafka skill not found, skipping"
fi

# Deploy PostgreSQL using skill
echo ""
echo "Deploying PostgreSQL..."
if [ -f ".claude/skills/postgres-k8s-setup/scripts/deploy_postgres.sh" ]; then
    bash .claude/skills/postgres-k8s-setup/scripts/deploy_postgres.sh
    python3 .claude/skills/postgres-k8s-setup/scripts/run_migrations.py
else
    echo "⚠ PostgreSQL skill not found, skipping"
fi

# Apply Dapr components
echo ""
echo "Applying Dapr components..."
kubectl apply -f k8s/infrastructure/dapr/

# Deploy Kong
echo ""
echo "Deploying Kong API Gateway..."
helm repo add kong https://charts.konghq.com 2>/dev/null || true
helm repo update
helm upgrade --install kong kong/kong \
    --namespace default \
    --set ingressController.installCRDs=false \
    --set proxy.type=ClusterIP \
    --wait

# Apply Kong configuration
kubectl apply -f k8s/infrastructure/kong/

echo ""
echo "✓ Infrastructure deployment complete!"
echo ""
echo "Run validation:"
echo "  python3 backend/scripts/validate_infrastructure.py"
