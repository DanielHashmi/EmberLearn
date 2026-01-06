#!/bin/bash
set -euo pipefail

# Deploy Dapr control plane to Kubernetes using Helm

# WSL/Windows compatibility
if command -v minikube.exe &> /dev/null; then
    KUBECTL="minikube.exe kubectl --"
else
    KUBECTL="kubectl"
fi

echo "Deploying Dapr control plane..."

# Add Dapr Helm repo
helm repo add dapr https://dapr.github.io/helm-charts/ 2>/dev/null || true
helm repo update

# Create dapr-system namespace
$KUBECTL create namespace dapr-system --dry-run=client -o yaml | $KUBECTL apply -f -

# Install Dapr control plane
helm upgrade --install dapr dapr/dapr \
  --version=1.13.0 \
  --namespace dapr-system \
  --set global.ha.enabled=false \
  --set global.logAsJson=true \
  --wait \
  --timeout=5m

# Wait for Dapr pods to be ready
echo "Waiting for Dapr control plane to be ready..."
$KUBECTL wait --for=condition=ready pod -l app.kubernetes.io/name=dapr -n dapr-system --timeout=300s

echo "✓ Dapr control plane deployed to dapr-system namespace"
