# ADR-0002: Cloud-Native Infrastructure Pattern

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 001-hackathon-iii
- **Context:** EmberLearn microservices need to persist state, publish/subscribe to events, and communicate reliably. The system requires polyglot support (Python now, potential Node.js later), built-in resiliency (retries, circuit breakers), backend portability (PostgreSQL, Redis, Kafka), and automatic observability for debugging distributed systems.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Dapr Sidecar Pattern** for all microservice infrastructure concerns:

- **Pattern:** Dapr sidecar container deployed alongside each agent service
- **State Management:** Dapr State API with PostgreSQL state store component
- **Event Communication:** Dapr Pub/Sub API with Kafka component
- **Service Invocation:** Dapr Service-to-Service calls with automatic retries
- **Observability:** Built-in OpenTelemetry tracing via Dapr

**Kubernetes Deployment:**
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "triage-agent"
  dapr.io/app-port: "8000"
```

**Python Implementation:**
```python
from dapr.clients import DaprClient

# Save state
with DaprClient() as d:
    d.save_state(store_name="statestore", key="student:42:topic:2", value=json.dumps(data))

# Publish event
with DaprClient() as d:
    d.publish_event(
        pubsub_name='kafka-pubsub',
        topic_name='learning.response',
        data=json.dumps(event),
        metadata={'partitionKey': str(student_id)}
    )
```

**Dapr Components:**
```yaml
# PostgreSQL State Store
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v2
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connectionString

# Kafka Pub/Sub
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "emberlearn-agents"
```

## Consequences

### Positive

- **Polyglot support:** Language-agnostic APIs enable future Node.js or Go services without rewriting infrastructure code
- **Built-in resiliency:** Automatic retries, circuit breakers, timeouts for all service calls and pub/sub
- **Backend portability:** Switch from PostgreSQL to Redis or Kafka to NATS by changing component config (no code changes)
- **Automatic observability:** OpenTelemetry tracing across all Dapr calls for distributed debugging
- **Reduced boilerplate:** No need to write retry logic, connection pooling, or event handling code
- **Cloud-native patterns:** Dapr is CNCF project, follows Kubernetes best practices

### Negative

- **Additional complexity:** Each service requires Dapr sidecar container (doubles pod count)
- **Learning curve:** Team must understand Dapr concepts (components, building blocks, APIs)
- **Debugging overhead:** Failures can occur in application OR sidecar, requires debugging both
- **Network hop latency:** All calls go through sidecar (localhost → sidecar → target), adds ~1-2ms per call
- **Resource overhead:** Each Dapr sidecar consumes ~50MB memory + CPU
- **Version management:** Must coordinate Dapr version upgrades across all services

## Alternatives Considered

### Alternative A: Direct Client Libraries

**Approach:** Use native Kafka clients (kafka-python) and PostgreSQL clients (psycopg2) directly in services

**Why rejected:**
- More boilerplate code (retry logic, connection pooling, error handling)
- Language-specific implementations (Python Kafka client ≠ Node.js Kafka client)
- No built-in resiliency patterns (must implement circuit breakers manually)
- Harder to switch backends (Kafka → NATS requires code changes across all services)

### Alternative B: Istio Service Mesh

**Approach:** Use Istio for service-to-service communication, traffic management, observability

**Why rejected:**
- Too complex for MVP (Istio control plane + sidecars heavier than Dapr)
- Focuses on traffic management (not state or pub/sub)
- Still need separate solutions for state persistence and event streaming
- Higher learning curve and operational burden for hackathon scope

### Alternative C: Redis for State + Direct Kafka

**Approach:** Use Redis for state caching, Kafka clients for pub/sub, no abstraction layer

**Why rejected:**
- Redis for state limits query capabilities (no SQL joins, aggregations like PostgreSQL)
- Direct Kafka clients require more code (producers, consumers, error handling)
- No built-in resiliency (must implement retries, circuit breakers)
- Harder to switch backends later (tightly coupled to Redis + Kafka)

## References

- Feature Spec: specs/001-hackathon-iii/spec.md (FR-011, FR-012, FR-013)
- Implementation Plan: specs/001-hackathon-iii/plan.md (Architecture Decision 2, lines 330-371)
- Research: specs/001-hackathon-iii/research.md (Decision 2: Dapr Sidecar Pattern)
- Quickstart: specs/001-hackathon-iii/quickstart.md (lines 110-174)
- Related ADRs: ADR-0001 (AI Agents), ADR-0004 (Event Ordering)
- Evaluator Evidence: history/prompts/001-hackathon-iii/0003-complete-implementation-plan-for-hackathon-iii.plan.prompt.md
