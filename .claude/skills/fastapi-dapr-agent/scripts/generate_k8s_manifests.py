#!/usr/bin/env python3
"""Generate Kubernetes manifests for FastAPI + Dapr agent services."""

import argparse
from pathlib import Path


DEPLOYMENT_TEMPLATE = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: {namespace}
  labels:
    app: {service_name}
    component: agent
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
        component: agent
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{service_name}"
        dapr.io/app-port: "8000"
        dapr.io/enable-api-logging: "true"
    spec:
      containers:
        - name: {service_name}
          image: {image}
          ports:
            - containerPort: 8000
          env:
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: openai-secret
                  key: api-key
            - name: SERVICE_NAME
              value: "{service_name}"
            - name: LOG_LEVEL
              value: "INFO"
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
'''


SERVICE_TEMPLATE = '''apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: {namespace}
  labels:
    app: {service_name}
spec:
  selector:
    app: {service_name}
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
  type: ClusterIP
'''


DAPR_COMPONENT_PUBSUB = '''apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: {namespace}
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "{service_name}-group"
    - name: authRequired
      value: "false"
'''


DAPR_COMPONENT_STATE = '''apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: {namespace}
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      value: "host=postgresql.default.svc.cluster.local user=emberlearn password=emberlearn port=5432 dbname=emberlearn sslmode=disable"
'''


def generate_manifests(
    service_name: str,
    namespace: str,
    image: str,
    replicas: int,
    output_dir: Path,
) -> None:
    """Generate Kubernetes manifests for an agent service."""
    manifest_dir = output_dir / service_name
    manifest_dir.mkdir(parents=True, exist_ok=True)

    # Generate deployment
    deployment = DEPLOYMENT_TEMPLATE.format(
        service_name=service_name,
        namespace=namespace,
        image=image,
        replicas=replicas,
    )
    (manifest_dir / "deployment.yaml").write_text(deployment)
    print(f"✓ Created {manifest_dir}/deployment.yaml")

    # Generate service
    service = SERVICE_TEMPLATE.format(
        service_name=service_name,
        namespace=namespace,
    )
    (manifest_dir / "service.yaml").write_text(service)
    print(f"✓ Created {manifest_dir}/service.yaml")

    print(f"\n✓ Manifests generated at {manifest_dir}")


def generate_dapr_components(namespace: str, output_dir: Path) -> None:
    """Generate Dapr component manifests."""
    dapr_dir = output_dir / "dapr-components"
    dapr_dir.mkdir(parents=True, exist_ok=True)

    # Pub/sub component
    pubsub = DAPR_COMPONENT_PUBSUB.format(
        namespace=namespace,
        service_name="emberlearn",
    )
    (dapr_dir / "pubsub.yaml").write_text(pubsub)
    print(f"✓ Created {dapr_dir}/pubsub.yaml")

    # State store component
    state = DAPR_COMPONENT_STATE.format(namespace=namespace)
    (dapr_dir / "statestore.yaml").write_text(state)
    print(f"✓ Created {dapr_dir}/statestore.yaml")

    print(f"\n✓ Dapr components generated at {dapr_dir}")


def main():
    parser = argparse.ArgumentParser(description="Generate K8s manifests for agent")
    parser.add_argument("service_name", help="Name of the agent service")
    parser.add_argument("--namespace", "-n", default="default", help="Kubernetes namespace")
    parser.add_argument("--image", "-i", required=True, help="Docker image name")
    parser.add_argument("--replicas", "-r", type=int, default=1, help="Number of replicas")
    parser.add_argument("--output", "-o", type=Path, default=Path("k8s/agents"),
                        help="Output directory")
    parser.add_argument("--dapr-components", action="store_true",
                        help="Also generate Dapr component manifests")
    args = parser.parse_args()

    generate_manifests(
        args.service_name,
        args.namespace,
        args.image,
        args.replicas,
        args.output,
    )

    if args.dapr_components:
        generate_dapr_components(args.namespace, args.output)


if __name__ == "__main__":
    main()
