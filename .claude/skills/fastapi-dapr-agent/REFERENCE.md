# FastAPI + Dapr + OpenAI Agent - Reference

## Overview

This skill scaffolds FastAPI microservices with Dapr sidecar integration and OpenAI Agents SDK for building AI-powered agent services.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Pod                            │
│  ┌─────────────────────┐  ┌─────────────────────┐          │
│  │   FastAPI Service   │  │    Dapr Sidecar     │          │
│  │  ┌───────────────┐  │  │  ┌─────────────┐   │          │
│  │  │ OpenAI Agent  │  │◄─┤  │  Pub/Sub    │   │          │
│  │  │   (GPT-4o)    │  │  │  │  (Kafka)    │   │          │
│  │  └───────────────┘  │  │  └─────────────┘   │          │
│  │  ┌───────────────┐  │  │  ┌─────────────┐   │          │
│  │  │   Endpoints   │  │──┤  │   State     │   │          │
│  │  │ /query /health│  │  │  │ (PostgreSQL)│   │          │
│  │  └───────────────┘  │  │  └─────────────┘   │          │
│  └─────────────────────┘  └─────────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Agent Types

| Agent | Purpose | Subscribe Topic | Publish Topic |
|-------|---------|-----------------|---------------|
| `triage` | Route queries to specialists | `learning.query` | `learning.routed` |
| `concepts` | Explain Python concepts | `learning.routed` | `learning.response` |
| `code_review` | Analyze code quality | `code.submitted` | `code.reviewed` |
| `debug` | Parse errors, provide hints | `code.error` | `learning.response` |
| `exercise` | Generate/grade challenges | `exercise.request` | `exercise.created` |
| `progress` | Track mastery scores | `progress.query` | `progress.response` |

## Generated Files

```
backend/{agent_type}_agent/
├── main.py           # FastAPI app with OpenAI Agent
├── Dockerfile        # Container image definition
├── requirements.txt  # Python dependencies
└── __init__.py       # Package marker
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for agent |
| `SERVICE_NAME` | No | Service identifier for logging |
| `LOG_LEVEL` | No | Logging level (default: INFO) |

### Dapr Annotations

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "{service_name}"
  dapr.io/app-port: "8000"
  dapr.io/enable-api-logging: "true"
```

## API Endpoints

### POST /query

Process a student query through the agent.

**Request:**
```json
{
  "student_id": "uuid",
  "query": "How do Python decorators work?",
  "topic": "decorators",
  "context": {}
}
```

**Response:**
```json
{
  "response": "Decorators are functions that modify...",
  "agent": "concepts",
  "correlation_id": "uuid"
}
```

### GET /health

Health check for Kubernetes probes.

**Response:**
```json
{
  "status": "healthy",
  "service": "concepts_agent"
}
```

### POST /dapr/subscribe

Returns Dapr subscription configuration.

## OpenAI Agents SDK Integration

### Agent Definition

```python
from agents import Agent, Runner

agent = Agent(
    name="ConceptsAgent",
    instructions="Your role is to explain Python concepts...",
    model="gpt-4o-mini",
)

# Run the agent
result = await Runner.run(agent, input=query)
response = result.final_output
```

### Adding Tools

```python
from agents import Agent, function_tool

@function_tool
def get_student_progress(student_id: str) -> dict:
    """Retrieve student's current progress."""
    # Implementation
    return {"mastery": 0.75, "topics_completed": 5}

agent = Agent(
    name="ProgressAgent",
    instructions="...",
    tools=[get_student_progress],
)
```

## Dapr Integration

### Publishing Events

```python
from shared.dapr_client import publish_event

await publish_event(
    topic="learning.response",
    data={"student_id": "...", "response": "..."},
    partition_key=student_id,  # Ensures ordering
)
```

### State Management

```python
from shared.dapr_client import get_state, save_state

# Save state
await save_state(
    key=f"student:{student_id}:session",
    value={"context": [], "last_topic": "loops"},
)

# Get state
session = await get_state(f"student:{student_id}:session")
```

## Kubernetes Deployment

### Generate Manifests

```bash
python scripts/generate_k8s_manifests.py concepts_agent \
  --image emberlearn/concepts-agent:latest \
  --namespace default \
  --replicas 2 \
  --dapr-components
```

### Apply Manifests

```bash
kubectl apply -f k8s/agents/concepts_agent/
kubectl apply -f k8s/agents/dapr-components/
```

## Troubleshooting

### Agent Not Responding

```bash
# Check pod status
kubectl get pods -l app=concepts_agent

# Check logs
kubectl logs -l app=concepts_agent -c concepts_agent

# Check Dapr sidecar
kubectl logs -l app=concepts_agent -c daprd
```

### Pub/Sub Issues

```bash
# Verify Dapr component
kubectl get components.dapr.io kafka-pubsub -o yaml

# Check Kafka connectivity
kubectl exec -n kafka kafka-0 -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --list
```

### OpenAI API Errors

```bash
# Verify secret exists
kubectl get secret openai-secret

# Check API key is set
kubectl exec <pod> -- printenv OPENAI_API_KEY | head -c 10
```

## Best Practices

1. **Correlation IDs**: Always propagate correlation IDs for tracing
2. **Structured Logging**: Use structlog with JSON output
3. **Graceful Shutdown**: Handle SIGTERM for clean pod termination
4. **Health Checks**: Implement both liveness and readiness probes
5. **Resource Limits**: Set appropriate CPU/memory limits
6. **Idempotency**: Design event handlers to be idempotent
