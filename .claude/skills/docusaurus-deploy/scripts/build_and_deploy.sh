#!/bin/bash
# Build and deploy Docusaurus documentation site

set -e

DOCS_DIR="${1:-docs-site}"
OUTPUT_DIR="${2:-docs-site/build}"
DEPLOY_TARGET="${3:-local}"

echo "Building Docusaurus documentation..."
echo "  Source: $DOCS_DIR"
echo "  Output: $OUTPUT_DIR"
echo "  Target: $DEPLOY_TARGET"
echo ""

# Check prerequisites
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found"
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

if ! command -v npm &> /dev/null; then
    echo "✗ npm not found"
    exit 1
fi
echo "✓ npm found: $(npm --version)"

# Navigate to docs directory
cd "$DOCS_DIR"

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo ""
    echo "Installing dependencies..."
    npm install
fi
echo "✓ Dependencies installed"

# Build the site
echo ""
echo "Building documentation site..."
npm run build

if [ -d "build" ]; then
    echo "✓ Build completed: $(du -sh build | cut -f1)"
else
    echo "✗ Build failed - no output directory"
    exit 1
fi

# Deploy based on target
case "$DEPLOY_TARGET" in
    "local")
        echo ""
        echo "Starting local server..."
        echo "Documentation available at: http://localhost:3000"
        npm run serve
        ;;
    "github-pages")
        echo ""
        echo "Deploying to GitHub Pages..."
        npm run deploy
        echo "✓ Deployed to GitHub Pages"
        ;;
    "kubernetes")
        echo ""
        echo "Building Docker image for Kubernetes..."

        # Create Dockerfile if not exists
        if [ ! -f "Dockerfile" ]; then
            cat > Dockerfile << 'EOF'
FROM nginx:alpine
COPY build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF
        fi

        docker build -t emberlearn/docs:latest .
        echo "✓ Docker image built: emberlearn/docs:latest"

        # For Minikube
        if command -v minikube &> /dev/null; then
            minikube image load emberlearn/docs:latest
            echo "✓ Image loaded into Minikube"
        fi
        ;;
    *)
        echo "Unknown deploy target: $DEPLOY_TARGET"
        echo "Available targets: local, github-pages, kubernetes"
        exit 1
        ;;
esac

echo ""
echo "✓ Documentation deployment complete!"
