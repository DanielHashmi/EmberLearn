# ADR-0005: Frontend Technology Stack

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2026-01-05
- **Feature:** 001-hackathon-iii
- **Context:** EmberLearn frontend requires browser-based Python code editor (Monaco Editor), student dashboard, exercise management, authentication, and responsive UI. Monaco Editor requires DOM access (cannot render server-side). Performance requirements: <3s first load, <1s subsequent loads.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

Use **Next.js 15+ with Monaco Editor (Client-Side Only)** for frontend:

- **Framework:** Next.js 15+ with App Router (React 18+, TypeScript 5.0+)
- **Code Editor:** @monaco-editor/react with SSR disabled via dynamic import
- **Styling:** Tailwind CSS v3
- **State Management:** React Context (simple, no Redux needed for MVP)
- **Deployment:** Kubernetes (via nextjs-k8s-deploy Skill)

**Monaco Editor Implementation:**
```typescript
import dynamic from 'next/dynamic';

const Editor = dynamic(() => import('@monaco-editor/react'), {
  ssr: false,  // CRITICAL: Monaco requires DOM, cannot render server-side
  loading: () => <div>Loading editor...</div>
});

export default function CodeEditor() {
  return <Editor language="python" theme="vs-dark" />;
}
```

## Consequences

### Positive

- **Next.js native solution:** dynamic() built-in, optimized for code splitting
- **Production-ready editor:** Monaco used by VS Code, CodeSandbox, StackBlitz
- **SSR compatibility:** ssr: false solves Monaco DOM requirement cleanly
- **TypeScript integration:** Full type safety across frontend
- **Fast hydration:** Client-only editor doesn't block initial page render
- **Proven pattern:** Standard approach for integrating client-only libraries in Next.js

### Negative

- **Client-side only:** Editor doesn't render on server (flash of loading state)
- **Bundle size:** Monaco Editor adds ~3MB to client bundle (mitigated by code splitting)
- **Complexity:** Next.js dynamic import pattern requires understanding SSR/CSR boundary
- **Loading delay:** First editor load may show loading spinner briefly
- **Framework coupling:** Tight coupling to Next.js dynamic import mechanism

## Alternatives Considered

### Alternative A: CodeMirror Editor
**Why rejected:** Less feature-rich than Monaco, manual configuration for Python syntax, no IntelliSense/autocomplete out-of-box

### Alternative B: Server-Side Rendering Monaco
**Why rejected:** Impossible - Monaco requires DOM APIs not available on server

### Alternative C: Plain Textarea
**Why rejected:** No syntax highlighting, no autocomplete, poor UX for code editing

## References

- Feature Spec: specs/001-hackathon-iii/spec.md (FR-016, FR-017, SC-007)
- Implementation Plan: specs/001-hackathon-iii/plan.md (Architecture Decision 5, lines 459-486)
- Research: specs/001-hackathon-iii/research.md (Decision 5: Next.js Monaco Editor Integration)
- Related ADRs: ADR-0003 (Code Execution Sandbox - Monaco submits to sandbox endpoint)
- Evaluator Evidence: history/prompts/001-hackathon-iii/0003-complete-implementation-plan-for-hackathon-iii.plan.prompt.md
