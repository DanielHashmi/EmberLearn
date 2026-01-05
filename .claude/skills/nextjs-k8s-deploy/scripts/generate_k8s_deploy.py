#!/usr/bin/env python3
"""Generate Kubernetes deployment manifests for Next.js application."""

import argparse
from pathlib import Path


DEPLOYMENT_YAML = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: {namespace}
  labels:
    app: {name}
    component: frontend
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
        component: frontend
    spec:
      containers:
        - name: {name}
          image: {image}
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: "production"
            - name: NEXT_PUBLIC_API_URL
              value: "{api_url}"
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /api/health
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 10
'''


SERVICE_YAML = '''apiVersion: v1
kind: Service
metadata:
  name: {name}
  namespace: {namespace}
  labels:
    app: {name}
spec:
  selector:
    app: {name}
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
  type: ClusterIP
'''


INGRESS_YAML = '''apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {name}
  namespace: {namespace}
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
    - host: {host}
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: {name}
                port:
                  number: 80
'''


DOCKERFILE = '''# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built assets
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["node", "server.js"]
'''


def generate_manifests(
    name: str,
    namespace: str,
    image: str,
    replicas: int,
    api_url: str,
    host: str,
    output_dir: Path,
) -> None:
    """Generate Kubernetes manifests for Next.js deployment."""
    manifest_dir = output_dir / name
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Generate deployment
    deployment = DEPLOYMENT_YAML.format(
        name=name,
        namespace=namespace,
        image=image,
        replicas=replicas,
        api_url=api_url,
    )
    (manifest_dir / "deployment.yaml").write_text(deployment)
    print(f"✓ Created {manifest_dir}/deployment.yaml")

    # Generate service
    service = SERVICE_YAML.format(name=name, namespace=namespace)
    (manifest_dir / "service.yaml").write_text(service)
    print(f"✓ Created {manifest_dir}/service.yaml")

    # Generate ingress
    ingress = INGRESS_YAML.format(name=name, namespace=namespace, host=host)
    (manifest_dir / "ingress.yaml").write_text(ingress)
    print(f"✓ Created {manifest_dir}/ingress.yaml")

    print(f"\n✓ Manifests generated at {manifest_dir}")


def generate_dockerfile(project_dir: Path) -> None:
    """Generate Dockerfile for Next.js application."""
    dockerfile_path = project_dir / "Dockerfile"
    dockerfile_path.write_text(DOCKERFILE)
    print(f"✓ Created {dockerfile_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate K8s manifests for Next.js")
    parser.add_argument("name", help="Application name")
    parser.add_argument("--namespace", "-n", default="default", help="Kubernetes namespace")
    parser.add_argument("--image", "-i", required=True, help="Docker image name")
    parser.add_argument("--replicas", "-r", type=int, default=2, help="Number of replicas")
    parser.add_argument("--api-url", default="http://kong.default.svc.cluster.local",
                        help="Backend API URL")
    parser.add_argument("--host", default="emberlearn.local", help="Ingress hostname")
    parser.add_argument("--output", "-o", type=Path, default=Path("k8s/frontend"),
                        help="Output directory")
    parser.add_argument("--dockerfile", "-d", type=Path,
                        help="Also generate Dockerfile in this directory")
    args = parser.parse_args()

    generate_manifests(
        args.name,
        args.namespace,
        args.image,
        args.replicas,
        args.api_url,
        args.host,
        args.output,
    )

    if args.dockerfile:
        generate_dockerfile(args.dockerfile)


if __name__ == "__main__":
    main()
