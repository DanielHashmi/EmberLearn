# ADR-0001: AI Agents Orchestration Architecture

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 001-hackathon-iii
- **Context:** EmberLearn requires 6 specialized AI agents (Triage, Concepts, Code Review, Debug, Exercise, Progress) to provide intelligent Python tutoring. The system needs a way to orchestrate multi-agent interactions, route queries to appropriate specialists, maintain conversation context, and debug complex agent workflows.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **OpenAI Agents SDK with Manager Pattern** for AI agent orchestration:

- **Framework:** OpenAI Agents SDK (openai-agents-python)
- **Pattern:** Triage agent as manager with handoffs to 5 specialist agents
- **Control Model:** Manager retains conversation control, specialists act as tools
- **Execution:** Async-native Python (async/await) for non-blocking I/O
- **Tracing:** Built-in tracing via OpenAI Agents SDK for debugging

**Implementation:**
```python
from agents import Agent, Runner

# Specialists
concepts_agent = Agent(name="Concepts", handoff_description="Explain Python concepts", ...)
code_review_agent = Agent(name="Code Review", handoff_description="Analyze code quality", ...)
debug_agent = Agent(name="Debug", handoff_description="Parse errors", ...)
exercise_agent = Agent(name="Exercise", handoff_description="Generate challenges", ...)
progress_agent = Agent(name="Progress", handoff_description="Track mastery", ...)

# Manager
triage_agent = Agent(
    name="Triage",
    instructions="Route queries to appropriate specialist",
    handoffs=[concepts_agent, code_review_agent, debug_agent, exercise_agent, progress_agent]
)

# Execution
result = await Runner.run(triage_agent, user_input)
```

## Consequences

### Positive

- **Built-in orchestration:** Agent.handoffs handles delegation automatically without custom routing logic
- **Conversation control:** Triage agent retains control flow, preventing specialist agents from going off-track
- **Async-native:** Python async/await throughout enables non-blocking I/O for concurrent agent operations
- **Built-in tracing:** OpenAI SDK provides debugging and observability for multi-agent workflows
- **Simpler codebase:** Less orchestration code to write and maintain compared to custom solutions
- **Proven pattern:** Manager pattern is recommended by OpenAI for multi-agent systems

### Negative

- **Vendor lock-in:** Tight coupling to OpenAI Agents SDK makes switching to other LLM providers difficult
- **Black box behavior:** SDK handles delegation internally, less visibility into routing decisions
- **API dependency:** Requires OpenAI API access, vulnerable to rate limits and service outages
- **Limited customization:** Handoff mechanism is fixed by SDK, cannot implement custom delegation logic easily
- **MVP constraint:** Graceful degradation via cached responses required for API failures (adds complexity)

## Alternatives Considered

### Alternative A: LangChain Multi-Agent Framework

**Approach:** Use LangChain's Agent + Tools pattern with custom orchestration

**Why rejected:**
- Heavy dependency with complex abstractions (chains, agents, tools, memory)
- Over-engineered for EmberLearn's needs (6 agents with simple routing)
- Steeper learning curve and more boilerplate code
- Less mature multi-agent patterns compared to OpenAI SDK

### Alternative B: Direct OpenAI API Calls

**Approach:** Manually orchestrate agents using OpenAI Chat Completions API

**Why rejected:**
- No built-in handoff mechanism, must implement custom routing logic
- Manual conversation context management across agents
- No tracing/debugging tools for multi-agent workflows
- Reinventing patterns already solved by OpenAI Agents SDK

### Alternative C: Custom Multi-Agent Framework

**Approach:** Build custom orchestration framework from scratch

**Why rejected:**
- Reinventing the wheel when proven solution exists
- Significant development time for framework itself (not core value)
- No tracing, testing, or debugging tools
- Higher maintenance burden for hackathon project

## References

- Feature Spec: specs/001-hackathon-iii/spec.md (FR-010, FR-011)
- Implementation Plan: specs/001-hackathon-iii/plan.md (Architecture Decision 1, lines 291-327)
- Research: specs/001-hackathon-iii/research.md (Decision 1: OpenAI Agents SDK)
- Related ADRs: ADR-0002 (Dapr Sidecar), ADR-0006 (Observability)
- Evaluator Evidence: history/prompts/001-hackathon-iii/0003-complete-implementation-plan-for-hackathon-iii.plan.prompt.md
