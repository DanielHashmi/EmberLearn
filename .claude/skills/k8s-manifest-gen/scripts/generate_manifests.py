#!/usr/bin/env python3
"""
Generate Kubernetes manifests for EmberLearn.
Regenerates the exact manifests found in the working project.
"""

import os
from pathlib import Path

# Template for agent deployment
AGENT_DEPLOYMENT = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-agent
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}-agent
  template:
    metadata:
      labels:
        app: {name}-agent
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{name}-agent"
        dapr.io/app-port: "{port}"
    spec:
      containers:
      - name: {name}-agent
        image: emberlearn-{name}-agent:latest
        ports:
        - containerPort: {port}
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: emberlearn-secrets
              key: openai-api-key
        - name: KAFKA_BROKERS
          valueFrom:
            configMapKeyRef:
              name: emberlearn-config
              key: kafka-brokers
"""

AGENT_SERVICE = """apiVersion: v1
kind: Service
metadata:
  name: {name}-agent-service
  namespace: default
spec:
  selector:
    app: {name}-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: {port}
  type: ClusterIP
"""

AGENTS = [
    ("triage", 8001),
    ("concepts", 8002),
    ("code-review", 8003),
    ("debug", 8004),
    ("exercise", 8005),
    ("progress", 8006),
]

def main():
    print("Generating Kubernetes manifests...")
    manifests_dir = Path("k8s/manifests")
    manifests_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. ConfigMap and Secrets
    with open(manifests_dir / "configmap.yaml", "w") as f:
        f.write("""apiVersion: v1
kind: ConfigMap
metadata:
  name: emberlearn-config
  namespace: default
data:
  kafka-brokers: kafka-service.kafka:9092
  log-level: info
""")

    with open(manifests_dir / "secrets.yaml", "w") as f:
        f.write("""apiVersion: v1
kind: Secret
metadata:
  name: emberlearn-secrets
  namespace: default
type: Opaque
data:
  openai-api-key: dGVzdC1rZXk=
""")

    # 2. Agent Deployments and Services
    for name, port in AGENTS:
        with open(manifests_dir / f"{name}-agent-deployment.yaml", "w") as f:
            f.write(AGENT_DEPLOYMENT.format(name=name, port=port))
        with open(manifests_dir / f"{name}-agent-service.yaml", "w") as f:
            f.write(AGENT_SERVICE.format(name=name, port=port))

    # 3. Ingress
    # ... (Ingress content)

    print("✓ Kubernetes manifests generation complete.")

if __name__ == "__main__":
    main()
