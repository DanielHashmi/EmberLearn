#!/bin/bash
# Check prerequisites for PostgreSQL deployment

set -e

echo "Checking PostgreSQL deployment prerequisites..."

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "✗ kubectl not found"
    exit 1
fi
echo "✓ kubectl found"

# Check helm
if ! command -v helm &> /dev/null; then
    echo "✗ helm not found"
    exit 1
fi
echo "✓ helm found"

# Check cluster access
if ! kubectl cluster-info &> /dev/null; then
    echo "✗ Cannot connect to Kubernetes cluster"
    exit 1
fi
echo "✓ Kubernetes cluster accessible"

# Check Bitnami repo
if ! helm repo list | grep -q bitnami; then
    echo "Adding Bitnami Helm repository..."
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
fi
echo "✓ Bitnami Helm repository available"

echo ""
echo "✓ All prerequisites met!"
