# ADR-0004: Event Ordering and Partitioning Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 001-hackathon-iii
- **Context:** Mastery calculation depends on correct event sequence (exercise submission → test results → score update → progress recalculation). Struggle detection counts consecutive errors. Out-of-order events break these calculations. Need scalable solution that processes different students in parallel while maintaining per-student ordering.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Kafka Partition Key = student_id** for event ordering:

- **Partition Key:** All events for student X use partitionKey=student_id (as string)
- **Ordering Guarantee:** Kafka guarantees FIFO ordering within partition
- **Scalability:** Different students processed in parallel across partitions
- **Kafka Native:** Leverages built-in partitioning, no custom ordering logic

**Implementation:**
```python
d.publish_event(
    pubsub_name='kafka-pubsub',
    topic_name='code.executed',
    data=json.dumps({
        'correlation_id': correlation_id,
        'student_id': 42,
        'payload': result
    }),
    metadata={'partitionKey': '42'}  # student_id as string
)
```

**Why Ordering Matters:**
- Mastery calculation: exercise completion → score update → progress recalculation (must be sequential)
- Struggle detection: counts consecutive errors (3+ same error type requires ordering)
- Progress agent: aggregates sequential events for mastery score calculation

## Consequences

### Positive

- **Ordering guarantee:** Kafka FIFO per partition ensures correct event sequence per student
- **Horizontal scalability:** Different students processed in parallel across partitions
- **Kafka native:** No custom ordering logic, leverages built-in mechanism
- **Simple implementation:** Single metadata field (partitionKey) solves problem
- **Consumer parallelism:** Multiple consumers can process different partitions concurrently

### Negative

- **Hot partition risk:** Popular student (high activity) could overload single partition
- **Partition rebalancing:** Consumer restarts cause brief ordering disruption during rebalance
- **String conversion:** student_id must be converted to string for partitionKey (type coercion)
- **Debug complexity:** Event order issues harder to debug (requires Kafka partition inspection)

## Alternatives Considered

### Alternative A: Timestamp-based Ordering
**Why rejected:** Vulnerable to clock skew between services, race conditions with concurrent events

### Alternative B: Sequence Numbers (Central Sequencer)
**Why rejected:** Requires centralized sequencer service (single point of failure), adds latency

### Alternative C: No Ordering Guarantee
**Why rejected:** Breaks mastery calculation and struggle detection (core features)

## References

- Feature Spec: specs/001-hackathon-iii/spec.md (FR-012, FR-019, FR-021)
- Implementation Plan: specs/001-hackathon-iii/plan.md (Architecture Decision 4, lines 423-456)
- Research: specs/001-hackathon-iii/research.md (Decision 4: Kafka Partitioning)
- Data Model: specs/001-hackathon-iii/data-model.md (Event entity, lines 404-433)
- Related ADRs: ADR-0002 (Dapr Sidecar - Kafka pub/sub component)
- Evaluator Evidence: history/prompts/001-hackathon-iii/0003-complete-implementation-plan-for-hackathon-iii.plan.prompt.md
