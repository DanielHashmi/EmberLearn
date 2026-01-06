#!/usr/bin/env python3
"""
Generate complete Kubernetes manifests for all EmberLearn microservices.

Creates Deployments with Dapr sidecars, Services, ConfigMaps, Secrets, and Ingress.
"""

import os
import yaml
from pathlib import Path


# Service specifications
SERVICES = [
    {
        "name": "triage-agent",
        "port": 8000,
        "replicas": 2,
        "env": {
            "OPENAI_API_KEY": {"secretKeyRef": {"name": "openai-secret", "key": "api-key"}},
            "DATABASE_URL": {"secretKeyRef": {"name": "postgres-secret", "key": "connection-string"}},
        }
    },
    {
        "name": "concepts-agent",
        "port": 8001,
        "replicas": 2,
        "env": {
            "OPENAI_API_KEY": {"secretKeyRef": {"name": "openai-secret", "key": "api-key"}},
        }
    },
    {
        "name": "code-review-agent",
        "port": 8002,
        "replicas": 2,
        "env": {
            "OPENAI_API_KEY": {"secretKeyRef": {"name": "openai-secret", "key": "api-key"}},
        }
    },
    {
        "name": "debug-agent",
        "port": 8003,
        "replicas": 2,
        "env": {
            "OPENAI_API_KEY": {"secretKeyRef": {"name": "openai-secret", "key": "api-key"}},
        }
    },
    {
        "name": "exercise-agent",
        "port": 8004,
        "replicas": 2,
        "env": {
            "OPENAI_API_KEY": {"secretKeyRef": {"name": "openai-secret", "key": "api-key"}},
        }
    },
    {
        "name": "progress-agent",
        "port": 8005,
        "replicas": 2,
        "env": {
            "OPENAI_API_KEY": {"secretKeyRef": {"name": "openai-secret", "key": "api-key"}},
            "DATABASE_URL": {"secretKeyRef": {"name": "postgres-secret", "key": "connection-string"}},
        }
    },
]


def generate_deployment(service: dict) -> dict:
    """Generate Deployment manifest with Dapr annotations."""
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": service["name"],
            "namespace": "default",
            "labels": {
                "app": service["name"],
            }
        },
        "spec": {
            "replicas": service["replicas"],
            "selector": {
                "matchLabels": {
                    "app": service["name"],
                }
            },
            "template": {
                "metadata": {
                    "labels": {
                        "app": service["name"],
                    },
                    "annotations": {
                        "dapr.io/enabled": "true",
                        "dapr.io/app-id": service["name"],
                        "dapr.io/app-port": str(service["port"]),
                        "dapr.io/log-level": "info",
                    }
                },
                "spec": {
                    "containers": [
                        {
                            "name": service["name"],
                            "image": f"emberlearn/{service['name']}:latest",
                            "imagePullPolicy": "IfNotPresent",
                            "ports": [
                                {
                                    "containerPort": service["port"],
                                    "name": "http",
                                }
                            ],
                            "env": [
                                {"name": k, "valueFrom": v}
                                for k, v in service["env"].items()
                            ],
                            "resources": {
                                "requests": {
                                    "cpu": "100m",
                                    "memory": "128Mi",
                                },
                                "limits": {
                                    "cpu": "500m",
                                    "memory": "512Mi",
                                }
                            },
                            "livenessProbe": {
                                "httpGet": {
                                    "path": "/health",
                                    "port": service["port"],
                                },
                                "initialDelaySeconds": 30,
                                "periodSeconds": 10,
                            },
                            "readinessProbe": {
                                "httpGet": {
                                    "path": "/ready",
                                    "port": service["port"],
                                },
                                "initialDelaySeconds": 10,
                                "periodSeconds": 5,
                            }
                        }
                    ]
                }
            }
        }
    }


def generate_service(service: dict) -> dict:
    """Generate Service manifest."""
    return {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{service['name']}-service",
            "namespace": "default",
            "labels": {
                "app": service["name"],
            }
        },
        "spec": {
            "type": "ClusterIP",
            "selector": {
                "app": service["name"],
            },
            "ports": [
                {
                    "port": 80,
                    "targetPort": service["port"],
                    "protocol": "TCP",
                    "name": "http",
                }
            ]
        }
    }


def generate_secrets() -> dict:
    """Generate Secrets manifest (values should be base64 encoded)."""
    return {
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": "openai-secret",
            "namespace": "default",
        },
        "type": "Opaque",
        "stringData": {
            "api-key": "REPLACE_WITH_OPENAI_API_KEY",
        }
    }


def generate_configmap() -> dict:
    """Generate ConfigMap for shared configuration."""
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": "emberlearn-config",
            "namespace": "default",
        },
        "data": {
            "kafka-brokers": "kafka-service.kafka:9092",
            "log-level": "info",
        }
    }


def generate_ingress() -> dict:
    """Generate Ingress manifest for external access."""
    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": "emberlearn-ingress",
            "namespace": "default",
            "annotations": {
                "nginx.ingress.kubernetes.io/rewrite-target": "/",
            }
        },
        "spec": {
            "rules": [
                {
                    "host": "emberlearn.local",
                    "http": {
                        "paths": [
                            {
                                "path": f"/{service['name']}",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": f"{service['name']}-service",
                                        "port": {"number": 80},
                                    }
                                }
                            }
                            for service in SERVICES
                        ]
                    }
                }
            ]
        }
    }


def main():
    output_dir = Path("k8s/manifests")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate manifests for each service
    for service in SERVICES:
        # Deployment
        deployment = generate_deployment(service)
        with open(output_dir / f"{service['name']}-deployment.yaml", 'w') as f:
            yaml.dump(deployment, f, default_flow_style=False, sort_keys=False)

        # Service
        svc = generate_service(service)
        with open(output_dir / f"{service['name']}-service.yaml", 'w') as f:
            yaml.dump(svc, f, default_flow_style=False, sort_keys=False)

    # Generate shared resources
    secrets = generate_secrets()
    with open(output_dir / "secrets.yaml", 'w') as f:
        yaml.dump(secrets, f, default_flow_style=False, sort_keys=False)

    configmap = generate_configmap()
    with open(output_dir / "configmap.yaml", 'w') as f:
        yaml.dump(configmap, f, default_flow_style=False, sort_keys=False)

    ingress = generate_ingress()
    with open(output_dir / "ingress.yaml", 'w') as f:
        yaml.dump(ingress, f, default_flow_style=False, sort_keys=False)

    print(f"✓ Generated manifests for {len(SERVICES)} services in {output_dir}/")
    print(f"  - {len(SERVICES)} Deployments with Dapr sidecars")
    print(f"  - {len(SERVICES)} Services")
    print(f"  - 1 Secrets manifest")
    print(f"  - 1 ConfigMap")
    print(f"  - 1 Ingress")


if __name__ == "__main__":
    main()
