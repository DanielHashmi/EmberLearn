# Feature Specification: Hackathon III - Reusable Intelligence and Cloud-Native Mastery

**Feature Branch**: `001-hackathon-iii`
**Created**: 2026-01-05
**Status**: Draft
**Input**: User description: "EmberLearn Hackathon III: Build Skills with MCP Code Execution for autonomous cloud-native application deployment, and create AI-powered Python tutoring platform"

## Clarifications

### Session 2026-01-05

- Q: What isolation mechanism should the code execution sandbox use for Python code? → A: Python subprocess with resource limits via `ulimit`/`resource` module (moderate isolation, simpler implementation)
- Q: How should entities (Students, Exercises, Topics) be uniquely identified in the database? → A: Numeric IDs with UUID fallback for cross-service references (balanced approach)
- Q: When OpenAI API fails (rate limit, timeout, service unavailable), how should AI agents respond? → A: Fall back to cached responses or predefined answers for common queries (graceful degradation)
- Q: What logging and observability approach should be implemented for debugging and monitoring? → A: Structured JSON logging to stdout with correlation IDs (simple, cloud-native)
- Q: How should the system handle event ordering when multiple agents publish events simultaneously for the same student? → A: Kafka partition key on student_id ensures ordered processing per student (leverages Kafka guarantees)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Foundation Skills (Priority: P1)

As a hackathon participant, I need to create 7 core reusable Skills with MCP Code Execution pattern so that AI agents (Claude Code and Goose) can autonomously deploy cloud-native infrastructure without manual intervention.

**Why this priority**: Foundation Skills are the product and represent 40% of evaluation score (Skills Autonomy 15% + Token Efficiency 10% + Cross-Agent Compatibility 5% + MCP Integration 10%). Without these, no other work can proceed.

**Independent Test**: Can be fully tested by providing a single prompt to Claude Code or Goose (e.g., "Deploy Kafka on Kubernetes") and verifying autonomous execution with zero manual steps, deployment success, and validation completion.

**Acceptance Scenarios**:

1. **Given** an AI agent has access to the `agents-md-gen` Skill, **When** user prompts "Generate AGENTS.md for this repository", **Then** the Skill executes autonomously, analyzes repository structure, generates comprehensive AGENTS.md file, and reports completion
2. **Given** Minikube is running and `kafka-k8s-setup` Skill exists, **When** user prompts "Deploy Kafka", **Then** Skill runs prerequisite checks, executes Helm deployment, verifies all pods are Running, and confirms successful deployment
3. **Given** the `postgres-k8s-setup` Skill exists, **When** user prompts "Set up PostgreSQL database", **Then** Skill deploys PostgreSQL via Helm, runs migrations, verifies schema, and reports success
4. **Given** `fastapi-dapr-agent` Skill exists, **When** user prompts "Create Triage agent service", **Then** Skill scaffolds FastAPI service with Dapr sidecar configuration, OpenAI Agents SDK integration, and Kafka pub/sub setup
5. **Given** `mcp-code-execution` Skill exists, **When** user prompts "Implement MCP code execution for this server", **Then** Skill wraps MCP server in executable scripts following the pattern: SKILL.md (~100 tokens) → scripts/*.py (0 tokens) → minimal result
6. **Given** `nextjs-k8s-deploy` Skill with Monaco Editor integration exists, **When** user prompts "Deploy frontend", **Then** Skill creates Dockerfile, K8s manifests, integrates Monaco Editor with SSR compatibility, and deploys to cluster
7. **Given** `docusaurus-deploy` Skill exists, **When** user prompts "Deploy documentation", **Then** Skill generates documentation from code, builds Docusaurus site, and deploys to Kubernetes

---

### User Story 2 - Test Cross-Agent Compatibility (Priority: P1)

As a hackathon participant, I need to verify that each Skill works identically on both Claude Code and Goose so that Skills meet the cross-agent compatibility requirement (5% of evaluation).

**Why this priority**: Cross-agent compatibility is mandatory for hackathon submission. Evaluation criteria explicitly require "Same skill works on Claude Code AND Goose" - failure here means disqualification.

**Independent Test**: Can be fully tested by running the same Skill prompt on both Claude Code and Goose in parallel and comparing execution steps, output format, and final results for consistency.

**Acceptance Scenarios**:

1. **Given** a Skill has been developed and tested on Claude Code, **When** the same Skill is executed on Goose with identical input, **Then** both agents produce equivalent results with the same validation success criteria
2. **Given** Skills use AAIF-compliant SKILL.md format with YAML frontmatter, **When** loaded by either agent, **Then** both agents parse metadata correctly and trigger on semantic description matches
3. **Given** Skills use universal tools (Bash, Python, kubectl, helm), **When** executed by different agents, **Then** no agent-specific tool failures occur
4. **Given** all 7 foundation Skills pass individual tests, **When** tested on both agents, **Then** compatibility matrix shows 100% pass rate across all Skills and both agents

---

### User Story 3 - Measure Token Efficiency (Priority: P2)

As a hackathon participant, I need to document token efficiency improvements achieved through Skills + Scripts pattern so that I can demonstrate 80-98% token reduction versus direct MCP integration (10% of evaluation).

**Why this priority**: Token efficiency is a key evaluation criterion and demonstrates understanding of MCP Code Execution innovation. This measurement justifies the architectural approach.

**Independent Test**: Can be fully tested by implementing one capability both ways (direct MCP vs Skills + Scripts), measuring tokens consumed before/during/after execution, and calculating reduction percentage.

**Acceptance Scenarios**:

1. **Given** a baseline MCP server loaded directly into agent context, **When** measuring token consumption, **Then** initial context load shows 15,000-50,000 tokens consumed
2. **Given** the same capability implemented as Skill + Scripts, **When** measuring token consumption, **Then** SKILL.md consumes ~100 tokens, scripts execute outside context (0 tokens), and only minimal result (~10 tokens) enters context
3. **Given** token measurements for both approaches, **When** calculating efficiency, **Then** Skills + Scripts achieves 80-98% reduction versus direct MCP
4. **Given** token efficiency data for all 7 Skills, **When** documented in README.md, **Then** each Skill shows clear before/after token measurements with percentage reduction

---

### User Story 4 - Build EmberLearn Infrastructure (Priority: P2)

As a hackathon participant, I need to use foundation Skills to autonomously deploy EmberLearn cloud-native infrastructure (Kafka, Dapr, PostgreSQL, Kong) so that microservices can communicate, persist data, and handle authentication.

**Why this priority**: Infrastructure deployment demonstrates Skills autonomy and enables application development. This directly tests the "single prompt → complete deployment" capability (15% Skills Autonomy criterion).

**Independent Test**: Can be fully tested by prompting AI agents to "Deploy EmberLearn infrastructure" and verifying all components (Kafka, PostgreSQL, Kong, Dapr) are running, healthy, and accessible without manual kubectl/helm commands.

**Acceptance Scenarios**:

1. **Given** `kafka-k8s-setup` Skill, **When** user prompts "Set up Kafka for EmberLearn", **Then** Kafka deploys with topics: learning.*, code.*, exercise.*, struggle.*, all brokers are Running, and test message pub/sub succeeds
2. **Given** `postgres-k8s-setup` Skill, **When** user prompts "Set up database", **Then** Neon PostgreSQL deploys, connection pooling is configured, initial schema migrations run, and database is accessible via Dapr state store
3. **Given** Kong API Gateway requirements, **When** user prompts "Deploy API gateway with JWT authentication", **Then** Kong deploys with JWT plugin configured, rate limiting enabled, and routes to backend services established
4. **Given** Dapr requirements, **When** user prompts "Set up Dapr", **Then** Dapr control plane deploys, sidecars are injectable, state management connects to PostgreSQL, and pub/sub connects to Kafka

---

### User Story 5 - Implement EmberLearn AI Agents (Priority: P3)

As a hackathon participant, I need to use `fastapi-dapr-agent` Skill to create 6 specialized AI agent microservices (Triage, Concepts, Code Review, Debug, Exercise, Progress) so that EmberLearn can provide intelligent Python tutoring.

**Why this priority**: AI agents are the core value proposition of EmberLearn but depend on infrastructure (P2). This demonstrates application-level Skills usage and completes 15% "EmberLearn Completion" criterion.

**Independent Test**: Can be fully tested by prompting AI agent to "Create [Agent Name] service" for each of the 6 agents and verifying each produces functional FastAPI service with OpenAI Agents SDK, Dapr sidecar, Kafka pub/sub, and state management.

**Acceptance Scenarios**:

1. **Given** `fastapi-dapr-agent` Skill, **When** user prompts "Create Triage agent service", **Then** FastAPI service is created with OpenAI Agents SDK, Dapr annotations, Kafka pub/sub configuration for routing queries, and deployed to K8s
2. **Given** Triage agent exists, **When** user sends query "How do for loops work?", **Then** Triage agent publishes to `learning.query.routed` topic with target=Concepts, and Concepts agent receives and processes
3. **Given** all 6 agents (Triage, Concepts, Code Review, Debug, Exercise, Progress) are deployed, **When** testing inter-agent communication, **Then** events flow through Kafka, state persists in PostgreSQL, and agents respond appropriately
4. **Given** Exercise agent exists, **When** user requests "Generate list comprehension exercise", **Then** agent creates exercise, stores in database, returns exercise ID, and publishes `exercise.created` event

---

### User Story 6 - Build EmberLearn Frontend (Priority: P3)

As a hackathon participant, I need to use `nextjs-k8s-deploy` Skill to create EmberLearn frontend with Monaco Editor integration so that students can interact with AI tutors and write Python code in the browser.

**Why this priority**: Frontend completes the user-facing application and demonstrates full-stack Skills usage. Required for "EmberLearn Completion" but depends on backend services (P3).

**Independent Test**: Can be fully tested by prompting AI agent to "Create EmberLearn frontend with code editor" and verifying Next.js app deploys with Monaco Editor, connects to backend APIs via Kong, handles authentication, and renders correctly.

**Acceptance Scenarios**:

1. **Given** `nextjs-k8s-deploy` Skill, **When** user prompts "Create frontend with Monaco Editor", **Then** Next.js 15+ app scaffolds with @monaco-editor/react, SSR-compatible dynamic imports, responsive UI, and authentication flow
2. **Given** Monaco Editor integration, **When** student writes Python code in editor, **Then** code syntax highlights correctly, auto-completion works for Python stdlib, and code submits to backend for execution
3. **Given** Frontend deployment, **When** student authenticates and navigates to dashboard, **Then** JWT token is obtained, stored in HTTP-only cookie, and included in all API requests via Kong
4. **Given** Frontend connects to Progress agent, **When** student views dashboard, **Then** mastery scores display correctly with color coding (Red: 0-40%, Yellow: 41-70%, Green: 71-90%, Blue: 91-100%)

---

### User Story 7 - Deploy Documentation (Priority: P4)

As a hackathon participant, I need to use `docusaurus-deploy` Skill to generate and deploy comprehensive documentation so that hackathon judges can understand the project architecture, Skills usage, and evaluation criteria.

**Why this priority**: Documentation is required (10% of evaluation) but depends on all other components being complete. Lowest priority as it's the final polish step.

**Independent Test**: Can be fully tested by prompting AI agent to "Generate and deploy documentation" and verifying Docusaurus site builds from code comments/README files, deploys to K8s, and is accessible via browser with search functionality.

**Acceptance Scenarios**:

1. **Given** `docusaurus-deploy` Skill, **When** user prompts "Generate documentation", **Then** Skill scans codebase, extracts README files, generates API docs, creates Docusaurus config, and builds static site
2. **Given** Documentation site exists, **When** deployed to Kubernetes, **Then** site is accessible at documentation URL, search is enabled, and all sections (Skills, Architecture, API Reference) are present
3. **Given** Documentation includes Skills development guide, **When** judge reviews submission, **Then** guide explains MCP Code Execution pattern, token efficiency measurements, and cross-agent testing process

---

### Edge Cases

- **What happens when Minikube is not running?** Skill prerequisite checks detect missing cluster, display clear error message with remediation steps ("Start Minikube with: minikube start --cpus=4 --memory=8192"), and exit gracefully
- **What happens when Helm chart installation fails?** Skill captures error output, attempts automated rollback, logs failure details, and suggests manual intervention commands if rollback fails
- **What happens when Skills are incompatible between agents?** Cross-agent testing identifies incompatibility, documents specific differences in compatibility matrix, and flags for manual review before submission
- **What happens when token efficiency doesn't reach 80% threshold?** Skills are refactored to move more logic into scripts, REFERENCE.md is used for large documentation instead of SKILL.md, and measurements are re-taken
- **What happens when AI agent execution hangs or times out?** Skill includes timeout detection (default 5 minutes), graceful termination, state cleanup, and retry logic with exponential backoff
- **What happens when Kafka topics already exist?** Skill checks for existing topics, reuses if compatible with required configuration, or reports conflict if configuration differs
- **What happens when database migrations fail?** Skill captures migration errors, preserves database state, suggests manual inspection, and provides rollback command if available
- **What happens when OpenAI API fails (rate limit, timeout, unavailable)?** AI agents fall back to cached responses for common queries or predefined answers, log the failure event, and display graceful degradation message to users while continuing to operate

## Requirements *(mandatory)*

### Functional Requirements

#### Skills Library

- **FR-001**: Skills library MUST contain minimum 7 Skills: agents-md-gen, kafka-k8s-setup, postgres-k8s-setup, fastapi-dapr-agent, mcp-code-execution, nextjs-k8s-deploy, docusaurus-deploy
- **FR-002**: Each Skill MUST follow MCP Code Execution pattern: SKILL.md (~100 tokens) + scripts/ directory (executable code) + REFERENCE.md (loaded on-demand)
- **FR-003**: Each Skill MUST use AAIF-compliant SKILL.md format with YAML frontmatter containing: name (lowercase-with-hyphens, max 64 chars), description (max 1024 chars for semantic matching), optional allowed-tools, optional model override
- **FR-004**: Skill scripts MUST be executable without modification, validate prerequisites before execution, return structured parseable output, and only log minimal final results
- **FR-005**: Each Skill MUST include validation scripts that verify successful execution and report pass/fail status with specific checks
- **FR-006**: Skills MUST be tested on both Claude Code AND Goose, with compatibility documented in README.md compatibility matrix
- **FR-007**: Skills MUST demonstrate autonomous execution capability: single prompt triggers complete workflow from prerequisite check through deployment to validation with zero manual steps
- **FR-008**: Skills library README.md MUST document: skill usage instructions, token efficiency measurements (before/after for each skill), cross-agent testing results, development process notes

#### EmberLearn Application

- **FR-009**: EmberLearn application MUST be built entirely using Skills (no manual application code), with commit history showing agentic workflow (commits like "Claude: implemented X using Y skill")
- **FR-010**: Application MUST implement 6 AI agent microservices using OpenAI Agents SDK: Triage (route queries), Concepts (explain Python), Code Review (analyze code quality), Debug (parse errors), Exercise (generate/grade challenges), Progress (track mastery)
- **FR-011**: Each AI agent MUST be a FastAPI service with Dapr sidecar, communicate via Kafka pub/sub through Dapr, store state in PostgreSQL via Dapr state API, and publish events for significant actions
- **FR-011a**: Each AI agent MUST implement graceful degradation for OpenAI API failures by falling back to cached responses for common queries or predefined answers, logging failure events to Kafka, and displaying informative messages to users
- **FR-011b**: All services MUST implement structured JSON logging to stdout with correlation IDs (using UUID from events) for request tracing, including fields: timestamp, level, service_name, correlation_id, event_type, message, metadata
- **FR-012**: Application MUST deploy Kafka with topics: learning.*, code.*, exercise.*, struggle.* for event-driven communication between services, with partition key set to student_id to ensure ordered event processing per student
- **FR-013**: Application MUST deploy PostgreSQL for state persistence with Alembic migrations for schema management; Neon's serverless PostgreSQL is RECOMMENDED for production (with connection pooling and automatic scaling) but any PostgreSQL instance is acceptable for MVP development
- **FR-014**: Application MUST deploy Kong API Gateway with JWT plugin for authentication, rate limiting, and request routing to backend services
- **FR-015**: Application MUST implement JWT authentication with RS256 signing, 24-hour token expiry, HTTP-only cookie storage for refresh tokens, and role-based access control (Student, Teacher, Admin)
- **FR-016**: Frontend MUST be Next.js 15+ with Monaco Editor integration using @monaco-editor/react, SSR-compatible dynamic imports, responsive UI, and JWT-based authentication
- **FR-017**: Frontend MUST integrate Monaco Editor for Python code editing with syntax highlighting, auto-completion for Python stdlib, and code submission to backend sandbox for execution
- **FR-018**: Application MUST implement code execution sandbox using Python subprocess with resource limits enforced via `resource` module (CPU time, memory), 5-second timeout, 50MB memory limit, restricted filesystem access (temp directory only), no network access, and Python stdlib only (MVP scope)
- **FR-019**: Application MUST calculate topic mastery using weighted formula: Exercise completion 40% + Quiz scores 30% + Code quality 20% + Consistency/streak 10%
- **FR-020**: Application MUST display mastery levels with color coding: 0-40% Beginner (Red), 41-70% Learning (Yellow), 71-90% Proficient (Green), 91-100% Mastered (Blue)
- **FR-021**: Application MUST detect student struggles and alert teachers when: same error type 3+ times, stuck on exercise >10 minutes, quiz score <50%, student says "I don't understand" or "I'm stuck", 5+ failed code executions in a row
- **FR-022**: Application MUST include comprehensive AGENTS.md file generated by `agents-md-gen` Skill describing repository structure, conventions, and guidelines for AI agents

#### Documentation

- **FR-023**: Documentation MUST be deployed via `docusaurus-deploy` Skill with auto-generation from code comments and README files
- **FR-024**: Documentation MUST include sections: Skills development guide (MCP Code Execution pattern, token efficiency, cross-agent testing), Architecture overview (tech stack, microservices, data flow), API reference (agent endpoints, Kafka topics, data schemas), Evaluation criteria (100-point breakdown)
- **FR-025**: Documentation site MUST be deployed to Kubernetes, accessible via browser, with search functionality enabled

#### Hackathon Submission

- **FR-026**: Two repositories MUST be submitted: skills-library (Skills only) and EmberLearn (application code)
- **FR-027**: skills-library README.md MUST document skill usage, token efficiency measurements, cross-agent compatibility results, and development process
- **FR-028**: EmberLearn repository MUST demonstrate autonomous construction via Skills with commit messages reflecting agentic workflow

### Key Entities

- **Skill**: Reusable capability for AI agents; contains SKILL.md (instructions), scripts/ (executable code), REFERENCE.md (detailed docs); follows AAIF format
- **AI Agent**: Specialized microservice for tutoring tasks; implemented as FastAPI service with OpenAI Agents SDK, Dapr sidecar, Kafka pub/sub, PostgreSQL state persistence
- **Student**: User learning Python; uniquely identified by numeric ID (primary key) with UUID for cross-service references; has authentication credentials, progress data, mastery scores per topic, exercise/quiz history
- **Teacher**: User monitoring class performance; uniquely identified by numeric ID (primary key) with UUID for cross-service references; receives struggle alerts, can generate custom exercises, views class-wide progress analytics
- **Topic**: Python curriculum module (Basics, Control Flow, Data Structures, Functions, OOP, Files, Errors, Libraries); uniquely identified by numeric ID; has mastery calculation, exercises, quizzes
- **Exercise**: Coding challenge generated by Exercise agent; uniquely identified by numeric ID with UUID for event correlation; has difficulty level, test cases, auto-grading criteria, student submissions, pass/fail status
- **Event**: Message published to Kafka topic; identified by UUID for distributed tracing; has type (query, error, exercise, struggle), payload (data), timestamp, source agent, target agent

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Skills Development**:

- **SC-001**: All 7 foundation Skills complete autonomous execution from single prompt to validated deployment in under 10 minutes per Skill
- **SC-002**: Skills achieve 80-98% token efficiency improvement versus direct MCP integration, measured and documented for each Skill
- **SC-003**: 100% of Skills pass cross-agent compatibility testing on both Claude Code and Goose with identical results
- **SC-004**: Skills library README.md receives passing grade from constitution compliance check (no unresolved placeholders, clear usage instructions, token measurements documented)

**EmberLearn Application**:

- **SC-005**: All 6 AI agent microservices deploy successfully and respond to test queries within 2 seconds average latency
- **SC-006**: Infrastructure (Kafka, PostgreSQL, Kong, Dapr) deploys autonomously via Skills and passes health checks (all pods Running, services responding)
- **SC-007**: Frontend deploys with Monaco Editor integration and loads within 3 seconds on first visit, <1 second on subsequent visits
- **SC-008**: Application handles 100 concurrent student sessions without degradation (code execution, AI agent responses, database queries)
- **SC-009**: Mastery calculation correctly computes scores across 100+ test student profiles with various exercise/quiz completion patterns
- **SC-010**: Struggle detection triggers alerts within 30 seconds of trigger condition being met (3+ same errors, timeout, low score, etc.)
- **SC-011**: Code execution sandbox enforces all security constraints (5s timeout, 50MB memory, no network/filesystem) and blocks violations
- **SC-012**: JWT authentication flow completes login, token issuance, and first authenticated request within 2 seconds total

**Documentation**:

- **SC-013**: Docusaurus site deploys successfully with search functionality returning relevant results within 1 second
- **SC-014**: Documentation covers 100% of required sections: Skills guide, Architecture, API Reference, Evaluation criteria
- **SC-015**: Documentation is accessible to hackathon judges within 5 seconds of deployment completion

**Hackathon Evaluation**:

- **SC-016**: Skills Autonomy score ≥12/15 points (80%+ threshold) based on single-prompt-to-deployment capability
- **SC-017**: Token Efficiency score ≥8/10 points (80%+ threshold) based on measured reduction and documentation
- **SC-018**: Cross-Agent Compatibility score ≥4/5 points (80%+ threshold) based on compatibility matrix results
- **SC-019**: Architecture score ≥16/20 points (80%+ threshold) based on correct Dapr patterns, Kafka pub/sub, stateless microservices
- **SC-020**: Overall hackathon score ≥80/100 points (80%+ threshold) to qualify for winner consideration

## Assumptions

1. **Development Environment**: Assumes Minikube 1.28+ running with 4 CPUs and 8GB RAM allocated; Docker 20+ installed; kubectl and helm CLIs available; Claude Code and Goose installed and authenticated
2. **Kubernetes Context**: Assumes kubectl is configured to use Minikube context; no production clusters accessed during development; namespace isolation used for EmberLearn components
3. **Skill Testing**: Assumes Skills can be tested independently without dependencies on other Skills; each Skill includes self-contained prerequisite checks and validation
4. **Token Measurement**: Assumes token counting mechanism available via agent debug output or API response headers; baseline measurements use same test scenario for fair comparison
5. **Cross-Agent Testing**: Assumes both Claude Code and Goose installed on same machine with access to same Skills directory (`.claude/skills/`); identical prompts used for compatibility testing
6. **EmberLearn Scope**: Assumes MVP scope for hackathon; 6 core AI agents sufficient for demonstration; Python curriculum limited to 8 modules; single-user code execution (no concurrent sandboxes)
7. **OpenAI Agents SDK**: Assumes familiarity with SDK; agent creation, tool definition, and conversation management patterns established; API keys and rate limits managed
8. **Neon PostgreSQL**: Assumes using Neon's serverless PostgreSQL; connection string managed via Kubernetes Secret; Alembic migrations handle schema evolution
9. **Security**: Assumes development/demo security model acceptable for hackathon; production-grade security (penetration testing, compliance audits, etc.) out of scope
10. **Documentation**: Assumes Docusaurus 3.0+ templates adequate for documentation needs; manual documentation enhancement out of scope; auto-generated content from code comments sufficient

## Out of Scope

1. **Production Deployment**: Cloud deployment (Azure, GCP, Oracle) beyond Minikube is Phase 9 (optional bonus); production-grade monitoring, logging, and alerting out of scope for MVP
2. **Argo CD + GitHub Actions**: GitOps workflow automation is Phase 10 (optional bonus); manual kubectl apply for MVP acceptable
3. **Advanced Security**: Penetration testing, security audits, compliance certifications (SOC2, HIPAA, etc.) out of scope; basic JWT authentication sufficient
4. **Performance Optimization**: Load testing beyond 100 concurrent users, caching strategies (Redis), CDN integration out of scope for MVP
5. **Teacher Features**: Advanced teacher dashboard (analytics, custom curriculum, bulk student management) limited to basic struggle alerts and exercise generation for MVP
6. **Multi-language Support**: EmberLearn focuses on Python only; support for JavaScript, Java, etc. out of scope
7. **Real-time Collaboration**: Multi-student code pairing, shared editor sessions out of scope; single-user code execution only
8. **Mobile Apps**: Native iOS/Android apps out of scope; responsive web UI sufficient for MVP
9. **Payment/Billing**: Subscription management, payment processing out of scope; free access for hackathon demo
10. **Content Management**: Admin interface for managing curriculum, exercises, quizzes out of scope; content managed via database migrations
11. **Third-party Integrations**: LMS integration (Canvas, Moodle), GitHub Classroom, Google Classroom out of scope
12. **Advanced AI Features**: Custom LLM fine-tuning, prompt engineering UI, A/B testing different models out of scope; OpenAI Agents SDK with default models sufficient

## Dependencies

1. **External Tools**: Requires Docker, Minikube, kubectl, helm, Claude Code, Goose installed and configured before starting
2. **OpenAI API Access**: Requires OpenAI API key with sufficient quota for agent SDK usage (GPT-4 or GPT-3.5-turbo)
3. **Bitnami Helm Charts**: Depends on Bitnami Helm repository for Kafka and PostgreSQL chart installations
4. **Dapr Installation**: Requires Dapr CLI and Dapr control plane deployment to Minikube cluster
5. **Kong Helm Chart**: Depends on Kong Helm repository for API gateway installation
6. **Constitution and CLAUDE.md**: Requires constitution v1.0.1+ and updated CLAUDE.md with EmberLearn-specific guidance before starting implementation
7. **Hackathon Documentation**: References external hackathon document (Hackathon III_ Reusable Intelligence and Cloud-Native Mastery.md) for evaluation criteria and requirements

## Notes

**Evaluation Criteria Alignment**: This specification directly addresses all 8 evaluation categories:
- Skills Autonomy (15%): User Stories 1, 2, 4 focus on autonomous execution
- Token Efficiency (10%): User Story 3 explicitly measures token reduction
- Cross-Agent Compatibility (5%): User Story 2 dedicated to compatibility testing
- Architecture (20%): User Stories 4, 5, 6 cover Dapr, Kafka, microservices patterns
- MCP Integration (10%): User Story 1 focuses on MCP Code Execution pattern
- Documentation (10%): User Story 7 and FR-023 to FR-025
- Spec-Kit Plus Usage (15%): This specification itself demonstrates spec-driven approach
- EmberLearn Completion (15%): User Stories 5, 6 cover full application implementation

**Critical Success Factors**:
1. **Skills as Product Mindset**: Remember Skills are evaluated more heavily than application code; invest 60% effort in Skills quality, 40% in EmberLearn application
2. **Autonomous Execution**: Single-prompt-to-deployment capability is the gold standard; any manual intervention reduces evaluation score
3. **Cross-Agent Testing**: Test EVERY Skill on BOTH agents before considering it complete; incompatibility discovered at submission time is fatal
4. **Token Efficiency Documentation**: Without measured before/after token counts, cannot demonstrate understanding of MCP Code Execution innovation

**Implementation Sequence**: Follow priority order (P1 → P2 → P3 → P4) for incremental value delivery and risk mitigation. User Stories 1 and 2 (both P1) are foundation; failure here blocks all subsequent work.
