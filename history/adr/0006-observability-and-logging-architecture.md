# ADR-0006: Observability and Logging Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 001-hackathon-iii
- **Context:** 6 microservices (AI agents + sandbox) communicate via Kafka events. Need to trace requests across services for debugging distributed workflows. Requirements: correlation IDs for request tracing, structured JSON logs for aggregation (ELK, CloudWatch), cloud-native pattern (logs to stdout), high performance (minimal serialization overhead).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **structlog with orjson for JSON Logging and Correlation IDs**:

- **Logging Library:** structlog (structured logging with context binding)
- **Serializer:** orjson (fastest JSON serializer for Python)
- **Output:** JSON to stdout (cloud-native, Kubernetes captures)
- **Correlation:** FastAPI middleware binds correlation_id to all logs automatically
- **Format:** ISO timestamps, log level, service name, correlation_id, custom fields

**Implementation:**
```python
import structlog
import orjson

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(serializer=orjson.dumps)
    ]
)

# FastAPI middleware binds correlation_id
structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

# All logs include correlation_id automatically
log.info("query_received", student_id=42, query_length=25)
```

**Log Output:**
```json
{
  "event": "query_received",
  "level": "info",
  "timestamp": "2026-01-05T10:30:45.123456Z",
  "service_name": "triage-agent",
  "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "student_id": 42,
  "query_length": 25
}
```

## Consequences

### Positive

- **Structured output:** JSON logs parseable by ELK, CloudWatch, Datadog
- **Performance:** orjson is fastest JSON serializer (2-3x faster than standard json)
- **Context binding:** Correlation IDs automatically included in all logs (no manual passing)
- **Cloud-native:** Logs to stdout for Kubernetes container log collection
- **Type safety:** structlog supports type hints for log fields
- **Async-safe:** structlog works with Python async/await

### Negative

- **Learning curve:** structlog API different from standard logging module
- **JSON verbosity:** Human-readability reduced (must pipe through jq for local dev)
- **Dependency:** Requires structlog + orjson packages (not stdlib)
- **Migration cost:** Existing logging.getLogger() calls must be refactored
- **Configuration complexity:** Processor chain requires understanding

## Alternatives Considered

### Alternative A: python-json-logger
**Why rejected:** Less features (no context binding), slower JSON serialization, no async safety guarantees

### Alternative B: loguru
**Why rejected:** Not async-safe (can cause issues with FastAPI), no built-in JSON output, less structured logging support

### Alternative C: Standard logging Module
**Why rejected:** No structured output (plain text only), manual JSON serialization, no context binding for correlation IDs

## References

- Feature Spec: specs/001-hackathon-iii/spec.md (FR-011b, SC-010)
- Implementation Plan: specs/001-hackathon-iii/plan.md (Architecture Decision 6, lines 489-537)
- Research: specs/001-hackathon-iii/research.md (Decision 6: Structured JSON Logging)
- Related ADRs: ADR-0001 (AI Agents - correlation IDs in agent workflows), ADR-0002 (Dapr Sidecar - OpenTelemetry integration)
- Evaluator Evidence: history/prompts/001-hackathon-iii/0003-complete-implementation-plan-for-hackathon-iii.plan.prompt.md
