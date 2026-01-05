# ADR-0003: Code Execution Sandbox Security Model

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 001-hackathon-iii
- **Context:** EmberLearn allows students to submit Python code for exercises, which must be executed safely. The sandbox must prevent infinite loops, memory bombs, file system access, network calls, and malicious imports. Performance requirements mandate <100ms startup time and 5-second execution timeout. MVP scope allows moderate isolation (not production-grade).

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Python Subprocess with Resource Limits** for code execution sandbox:

- **Isolation:** subprocess.run() creates separate process for each execution
- **CPU Limit:** resource.setrlimit(RLIMIT_CPU, (5, 5)) enforces 5-second CPU time
- **Memory Limit:** resource.setrlimit(RLIMIT_AS, (50MB, 50MB)) enforces 50MB address space
- **Timeout:** subprocess timeout parameter for wall-clock timeout (5 seconds)
- **Working Directory:** cwd="/tmp" restricts filesystem access to temp directory
- **Validation:** Pre-execution AST analysis blocks dangerous imports (os, subprocess, socket)

**Implementation:**
```python
import subprocess
import resource
import sys

def set_limits():
    resource.setrlimit(resource.RLIMIT_AS, (50*1024*1024, 50*1024*1024))  # 50MB
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))  # 5s CPU time

def execute_code(code: str) -> dict:
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=5,
            preexec_fn=set_limits,
            cwd="/tmp"
        )
        return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Timeout after 5 seconds"}
```

## Consequences

### Positive

- **Fast startup:** <100ms process creation (vs 2-3s for Docker container)
- **Built-in timeout:** subprocess.run() timeout parameter handles wall-clock limits
- **Simple implementation:** Python standard library only, no external dependencies
- **Resource enforcement:** resource module enforces CPU and memory limits at OS level
- **Output capture:** stdout/stderr captured automatically for test case validation
- **Acceptable for MVP:** Moderate isolation sufficient for educational demo

### Negative

- **Limited isolation:** Network access NOT blocked (requires iptables for production)
- **Filesystem access:** Only /tmp restriction, could access other directories if paths known
- **Unix-only:** resource.setrlimit() not available on Windows
- **No Docker isolation:** Shares host kernel, vulnerable to kernel exploits
- **Production upgrade required:** Must migrate to Docker/Firecracker for production

## Alternatives Considered

### Alternative A: Docker Container Per Execution
**Why rejected:** 2-3s startup overhead unacceptable for UX, resource heavy (100+ MB per container)

### Alternative B: RestrictedPython (AST-based)
**Why rejected:** In-process execution (shared memory), AST bypasses possible, no resource limits

### Alternative C: Firecracker MicroVMs
**Why rejected:** Complex setup, overkill for MVP, requires bare metal or nested virtualization

## References

- Feature Spec: specs/001-hackathon-iii/spec.md (FR-018, SC-011)
- Implementation Plan: specs/001-hackathon-iii/plan.md (Architecture Decision 3, lines 374-420)
- Research: specs/001-hackathon-iii/research.md (Decision 3: Python Subprocess Isolation)
- Related ADRs: ADR-0005 (Frontend Stack - Monaco Editor integration)
- Evaluator Evidence: history/prompts/001-hackathon-iii/0003-complete-implementation-plan-for-hackathon-iii.plan.prompt.md
