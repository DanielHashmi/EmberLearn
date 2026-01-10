#!/bin/bash
# Build and deploy Next.js application to Kubernetes

set -e

# Configuration
PROJECT_DIR="${1:-.}"
IMAGE_NAME="${2:-emberlearn/frontend}"
IMAGE_TAG="${3:-latest}"
NAMESPACE="${4:-default}"

echo "Building and deploying Next.js application..."
echo "  Project: $PROJECT_DIR"
echo "  Image: $IMAGE_NAME:$IMAGE_TAG"
echo "  Namespace: $NAMESPACE"
echo ""

# Check prerequisites
if ! command -v docker &> /dev/null; then
    echo "✗ docker not found"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "✗ kubectl not found"
    exit 1
fi

# Build Docker image
echo "Building Docker image..."
cd "$PROJECT_DIR"

if [ ! -f "Dockerfile" ]; then
    echo "✗ Dockerfile not found in $PROJECT_DIR"
    exit 1
fi

docker build -t "$IMAGE_NAME:$IMAGE_TAG" .
echo "✓ Docker image built: $IMAGE_NAME:$IMAGE_TAG"

# For Minikube, load image into cluster
if command -v minikube &> /dev/null; then
    echo "Loading image into Minikube..."
    minikube image load "$IMAGE_NAME:$IMAGE_TAG"
    echo "✓ Image loaded into Minikube"
fi

# Apply Kubernetes manifests
MANIFEST_DIR="k8s/frontend"
if [ -d "$MANIFEST_DIR" ]; then
    echo "Applying Kubernetes manifests..."
    kubectl apply -f "$MANIFEST_DIR/" -n "$NAMESPACE"
    echo "✓ Manifests applied"
else
    echo "⚠ Manifest directory not found: $MANIFEST_DIR"
    echo "  Run generate_k8s_deploy.py first"
fi

# Wait for deployment
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/emberlearn-frontend -n "$NAMESPACE" --timeout=120s

echo ""
echo "✓ Next.js application deployed successfully!"
echo ""
echo "Access the application:"
echo "  kubectl port-forward svc/emberlearn-frontend 3000:80 -n $NAMESPACE"
echo "  Then open: http://localhost:3000"
