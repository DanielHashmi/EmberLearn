#!/bin/bash
# Check prerequisites for Kafka deployment

set -e

echo "Checking Kafka deployment prerequisites..."

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "✗ kubectl not found. Please install kubectl."
    exit 1
fi
echo "✓ kubectl found"

# Check helm
if ! command -v helm &> /dev/null; then
    echo "✗ helm not found. Please install Helm 3.x."
    exit 1
fi
echo "✓ helm found"

# Check Kubernetes cluster access
if ! kubectl cluster-info &> /dev/null; then
    echo "✗ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi
echo "✓ Kubernetes cluster accessible"

# Check if Bitnami repo is added
if ! helm repo list | grep -q bitnami; then
    echo "Adding Bitnami Helm repository..."
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo update
fi
echo "✓ Bitnami Helm repository available"

echo ""
echo "✓ All prerequisites met for Kafka deployment!"
