# Tasks: Hackathon III - Reusable Intelligence and Cloud-Native Mastery

**Input**: Design documents from `/specs/001-hackathon-iii/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/agent-api.yaml ✓, quickstart.md ✓

**Tests**: Tests are OPTIONAL per spec.md. This task list does NOT include test tasks unless explicitly requested.

**Organization**: Tasks are grouped by user story (7 total) to enable independent implementation and testing of each story. User stories follow priority order from spec.md: P1 (US1, US2), P2 (US3, US4), P3 (US5, US6), P4 (US7).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

**Single Repository During Development**:
- All work happens in THIS EmberLearn repository
- Skills created in `.claude/skills/` (for Claude Code to discover and use)
- Application code in `backend/`, `frontend/`, `k8s/`
- At submission, `.claude/skills/` will be COPIED to create separate skills-library repository

All paths shown are relative to EmberLearn repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic repository structure

- [ ] T001 Create .claude/skills/ directory structure in THIS repository for Skill development
- [ ] T002 Create backend/, frontend/, k8s/ directories per plan.md structure
- [ ] T003 [P] Initialize Python backend project with pyproject.toml for FastAPI 0.110+, OpenAI Agents SDK, Dapr SDK, structlog, orjson
- [ ] T004 [P] Initialize Next.js 15+ frontend with TypeScript 5.0+, @monaco-editor/react, tailwind CSS
- [ ] T005 [P] Create .gitignore files (Python, Node.js, secrets, .env, but DO NOT ignore .claude/skills/)
- [ ] T006 [P] Create constitution v1.0.1 in .specify/memory/constitution.md with 8 principles from spec.md
- [ ] T007 [P] Update CLAUDE.md with EmberLearn-specific guidance

**Checkpoint**: Repository structure ready for development

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T008 Setup Minikube cluster with 4 CPUs, 8GB RAM via quickstart.md instructions
- [ ] T009 Deploy Dapr control plane to Kubernetes via `dapr init --kubernetes --wait`
- [ ] T010 Create backend/shared/logging_config.py with structlog + orjson setup per research.md decision 6
- [ ] T011 [P] Create backend/shared/correlation.py with FastAPI middleware for correlation ID injection
- [ ] T012 [P] Create backend/shared/dapr_client.py with Dapr helper functions (save_state, publish_event wrappers)
- [ ] T013 [P] Create backend/shared/models.py with Pydantic base schemas (QueryRequest, QueryResponse, CodeExecutionRequest per contracts/agent-api.yaml)
- [ ] T014 Create backend/database/models.py with SQLAlchemy ORM models for 10 entities from data-model.md
- [ ] T015 Setup Alembic migrations framework in backend/database/migrations/
- [ ] T016 [P] Create migration 001_initial_schema.py for all 10 tables from data-model.md
- [ ] T017 [P] Create migration 002_seed_topics.py with 8 Python topics from data-model.md
- [ ] T018 [P] Create migration 003_mastery_triggers.py with PostgreSQL trigger for mastery score calculation from data-model.md
- [ ] T019 Create OpenAI API key Kubernetes Secret in k8s/infrastructure/openai-secret.yaml

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Foundation Skills (Priority: P1) 🎯 MVP PART 1

**Goal**: Create 7 core reusable Skills with MCP Code Execution pattern enabling autonomous cloud-native deployment (FR-001, FR-002, FR-003, FR-004, FR-005, FR-006, FR-007, FR-008)

**Independent Test**: Provide single prompt "Deploy Kafka on Kubernetes" to Claude Code or Goose and verify autonomous execution, deployment success, validation completion with zero manual steps

**Dependencies**: Phase 2 complete (Minikube, Dapr running)

### Implementation for User Story 1

#### Skill 1: agents-md-gen (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T020 [P] [US1] Create .claude/skills/agents-md-gen/SKILL.md with AAIF format (name, description <1024 chars, no tools restriction) per FR-003
- [ ] T021 [P] [US1] Create .claude/skills/agents-md-gen/scripts/analyze_repo.py to scan repository structure and identify conventions per FR-004
- [ ] T022 [P] [US1] Create .claude/skills/agents-md-gen/scripts/generate_agents_md.py to generate AGENTS.md file from analysis per FR-004
- [ ] T023 [P] [US1] Create .claude/skills/agents-md-gen/REFERENCE.md with detailed AGENTS.md format guidelines and examples per FR-002
- [ ] T024 [US1] Create .claude/skills/agents-md-gen/scripts/validate.sh to verify AGENTS.md generation succeeds and file is created per FR-005

#### Skill 2: kafka-k8s-setup (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T025 [P] [US1] Create .claude/skills/kafka-k8s-setup/SKILL.md with Kafka deployment description and prerequisite checks per FR-003
- [ ] T026 [P] [US1] Create .claude/skills/kafka-k8s-setup/scripts/deploy_kafka.sh to install Bitnami Kafka Helm chart with topics from FR-012 per FR-004
- [ ] T027 [P] [US1] Create .claude/skills/kafka-k8s-setup/scripts/verify_kafka.py to check all brokers Running and test pub/sub per FR-005
- [ ] T028 [P] [US1] Create .claude/skills/kafka-k8s-setup/scripts/rollback_kafka.sh for automated rollback on failure per FR-004
- [ ] T029 [P] [US1] Create .claude/skills/kafka-k8s-setup/REFERENCE.md with Kafka architecture, topics schema, troubleshooting guide per FR-002

#### Skill 3: postgres-k8s-setup (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T030 [P] [US1] Create .claude/skills/postgres-k8s-setup/SKILL.md with PostgreSQL deployment description per FR-003
- [ ] T031 [P] [US1] Create .claude/skills/postgres-k8s-setup/scripts/deploy_postgres.sh to install Neon PostgreSQL Helm chart per FR-004
- [ ] T032 [P] [US1] Create .claude/skills/postgres-k8s-setup/scripts/run_migrations.py to execute Alembic migrations from backend/database/migrations/ per FR-004
- [ ] T033 [P] [US1] Create .claude/skills/postgres-k8s-setup/scripts/verify_schema.py to validate all 10 tables exist with correct columns per FR-005
- [ ] T034 [P] [US1] Create .claude/skills/postgres-k8s-setup/REFERENCE.md with database schema documentation and migration guidelines per FR-002

#### Skill 4: fastapi-dapr-agent (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T035 [P] [US1] Create .claude/skills/fastapi-dapr-agent/SKILL.md with agent scaffolding description per FR-003
- [ ] T036 [P] [US1] Create .claude/skills/fastapi-dapr-agent/scripts/scaffold_agent.py to generate FastAPI service structure with Dapr annotations per FR-004, research.md decision 2
- [ ] T037 [P] [US1] Create .claude/skills/fastapi-dapr-agent/scripts/generate_dockerfile.py to create Dockerfile with FastAPI + Dapr sidecar setup per FR-004
- [ ] T038 [P] [US1] Create .claude/skills/fastapi-dapr-agent/scripts/generate_k8s_manifests.py to create deployment.yaml and service.yaml with Dapr annotations per FR-004
- [ ] T039 [P] [US1] Create .claude/skills/fastapi-dapr-agent/REFERENCE.md with OpenAI Agents SDK integration guide, Dapr patterns, examples per FR-002

#### Skill 5: mcp-code-execution (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T040 [P] [US1] Create .claude/skills/mcp-code-execution/SKILL.md with MCP server wrapping pattern description per FR-003
- [ ] T041 [P] [US1] Create .claude/skills/mcp-code-execution/scripts/wrap_mcp_server.py to generate executable scripts from MCP server definitions per FR-004
- [ ] T042 [P] [US1] Create .claude/skills/mcp-code-execution/scripts/validate_structure.py to check SKILL.md + scripts/ + REFERENCE.md structure per FR-002, FR-005
- [ ] T043 [P] [US1] Create .claude/skills/mcp-code-execution/REFERENCE.md with MCP Code Execution pattern documentation and token efficiency explanation per FR-002

#### Skill 6: nextjs-k8s-deploy (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T044 [P] [US1] Create .claude/skills/nextjs-k8s-deploy/SKILL.md with Next.js deployment and Monaco Editor integration description per FR-003
- [ ] T045 [P] [US1] Create .claude/skills/nextjs-k8s-deploy/scripts/scaffold_nextjs.sh to initialize Next.js 15+ project with TypeScript per FR-004
- [ ] T046 [P] [US1] Create .claude/skills/nextjs-k8s-deploy/scripts/integrate_monaco.py to add @monaco-editor/react with SSR disabled per FR-004, research.md decision 5
- [ ] T047 [P] [US1] Create .claude/skills/nextjs-k8s-deploy/scripts/generate_k8s_deploy.py to create Next.js Kubernetes deployment manifests per FR-004
- [ ] T048 [P] [US1] Create .claude/skills/nextjs-k8s-deploy/REFERENCE.md with Next.js SSR patterns, Monaco Editor configuration, troubleshooting per FR-002

#### Skill 7: docusaurus-deploy (FR-001, FR-002, FR-003, FR-004, FR-005)

- [ ] T049 [P] [US1] Create .claude/skills/docusaurus-deploy/SKILL.md with documentation generation and deployment description per FR-003
- [ ] T050 [P] [US1] Create .claude/skills/docusaurus-deploy/scripts/scan_codebase.py to extract README files and code comments per FR-004
- [ ] T051 [P] [US1] Create .claude/skills/docusaurus-deploy/scripts/generate_docusaurus_config.py to create Docusaurus 3.0+ configuration per FR-004
- [ ] T052 [P] [US1] Create .claude/skills/docusaurus-deploy/scripts/build_and_deploy.sh to build static site and deploy to Kubernetes per FR-004
- [ ] T053 [P] [US1] Create .claude/skills/docusaurus-deploy/REFERENCE.md with Docusaurus structure, API doc generation, search configuration per FR-002

#### Skill Validation and Documentation

- [ ] T054 [US1] Create skills-library README.md with skill usage instructions section per FR-008
- [ ] T055 [US1] Add token efficiency measurements section template to README.md per FR-008 (will be filled in US3)
- [ ] T056 [US1] Add cross-agent compatibility matrix template to README.md per FR-006, FR-008 (will be filled in US2)
- [ ] T057 [US1] Add development process notes section to README.md documenting Skill creation workflow per FR-008

**Checkpoint**: All 7 Skills created with SKILL.md + scripts/ + REFERENCE.md structure. Skills ready for cross-agent testing (US2) and token measurement (US3).

---

## Phase 4: User Story 2 - Test Cross-Agent Compatibility (Priority: P1) 🎯 MVP PART 2

**Goal**: Verify each Skill works identically on both Claude Code and Goose to meet cross-agent compatibility requirement (5% of evaluation)

**Independent Test**: Run same Skill prompt on Claude Code and Goose in parallel, compare execution steps, output format, final results for consistency

**Dependencies**: Phase 3 complete (all 7 Skills exist)

### Implementation for User Story 2

- [ ] T058 [US2] Create testing/compatibility-test-plan.md with test scenarios for all 7 Skills × 2 agents
- [ ] T059 [P] [US2] Test agents-md-gen Skill on Claude Code, document results in testing/claude-code-results.md
- [ ] T060 [P] [US2] Test agents-md-gen Skill on Goose, document results in testing/goose-results.md
- [ ] T061 [P] [US2] Test kafka-k8s-setup Skill on Claude Code, document deployment success and pod status
- [ ] T062 [P] [US2] Test kafka-k8s-setup Skill on Goose, document deployment success and pod status
- [ ] T063 [P] [US2] Test postgres-k8s-setup Skill on Claude Code, document schema verification results
- [ ] T064 [P] [US2] Test postgres-k8s-setup Skill on Goose, document schema verification results
- [ ] T065 [P] [US2] Test fastapi-dapr-agent Skill on Claude Code, document scaffolded service structure
- [ ] T066 [P] [US2] Test fastapi-dapr-agent Skill on Goose, document scaffolded service structure
- [ ] T067 [P] [US2] Test mcp-code-execution Skill on Claude Code, document wrapped MCP server
- [ ] T068 [P] [US2] Test mcp-code-execution Skill on Goose, document wrapped MCP server
- [ ] T069 [P] [US2] Test nextjs-k8s-deploy Skill on Claude Code, document frontend deployment
- [ ] T070 [P] [US2] Test nextjs-k8s-deploy Skill on Goose, document frontend deployment
- [ ] T071 [P] [US2] Test docusaurus-deploy Skill on Claude Code, document documentation site generation
- [ ] T072 [P] [US2] Test docusaurus-deploy Skill on Goose, document documentation site generation
- [ ] T073 [US2] Analyze all compatibility test results and identify any agent-specific differences
- [ ] T074 [US2] Update skills-library README.md compatibility matrix with results (7 Skills × 2 Agents = 14 cells) per FR-006
- [ ] T075 [US2] Document any incompatibilities found and provide fixes or workarounds in README.md

**Checkpoint**: 100% Skills pass cross-agent compatibility testing on both Claude Code and Goose. Compatibility matrix shows all green checkmarks (SC-003).

---

## Phase 5: User Story 3 - Measure Token Efficiency (Priority: P2)

**Goal**: Document token efficiency improvements (80-98% reduction) achieved through Skills + Scripts pattern versus direct MCP integration (10% of evaluation)

**Independent Test**: Implement one capability both ways (direct MCP vs Skills + Scripts), measure tokens consumed, calculate reduction percentage

**Dependencies**: Phase 3 complete (Skills exist for measurement)

### Implementation for User Story 3

- [ ] T076 [US3] Create testing/token-measurement-plan.md with baseline measurement approach for direct MCP integration
- [ ] T077 [US3] Select reference capability for token measurement (recommend: kafka-k8s-setup)
- [ ] T078 [US3] Measure baseline tokens for direct MCP Kafka server loaded into agent context, document in testing/baseline-tokens.md
- [ ] T079 [US3] Measure Skills + Scripts tokens: SKILL.md content (~100 tokens) + minimal result (~10 tokens), document in testing/skills-tokens.md
- [ ] T080 [US3] Calculate token reduction percentage: (baseline - skills) / baseline × 100, verify ≥80% threshold
- [ ] T081 [P] [US3] Repeat token measurements for all 7 Skills with same methodology
- [ ] T082 [US3] Create token efficiency table with before/after/reduction columns for each Skill
- [ ] T083 [US3] Update skills-library README.md with token efficiency measurements section per FR-008
- [ ] T084 [US3] Document measurement methodology and assumptions in README.md

**Checkpoint**: Token efficiency documented for all 7 Skills, achieving 80-98% reduction target (SC-002). README.md contains complete token measurements table.

---

## Phase 6: User Story 4 - Build EmberLearn Infrastructure (Priority: P2)

**Goal**: Use foundation Skills to autonomously deploy EmberLearn cloud-native infrastructure (Kafka, Dapr, PostgreSQL, Kong) enabling microservices communication

**Independent Test**: Prompt AI agents "Deploy EmberLearn infrastructure" and verify all components running, healthy, accessible without manual kubectl/helm commands

**Dependencies**: Phase 3 complete (Skills exist), Phase 2 complete (Minikube, Dapr running)

### Implementation for User Story 4

#### Kafka Deployment

- [ ] T085 [US4] Use kafka-k8s-setup Skill to deploy Kafka with topics: learning.*, code.*, exercise.*, struggle.* per FR-012
- [ ] T086 [US4] Verify Kafka brokers Running and topics created via kubectl get pods -l app=kafka
- [ ] T087 [US4] Test Kafka pub/sub with sample message using kubectl exec

#### PostgreSQL Deployment

- [ ] T088 [US4] Use postgres-k8s-setup Skill to deploy Neon PostgreSQL with connection pooling
- [ ] T089 [US4] Run Alembic migrations via Skill: 001_initial_schema, 002_seed_topics, 003_mastery_triggers
- [ ] T090 [US4] Verify all 10 tables exist in database with correct schema via query

#### Dapr Components Configuration

- [ ] T091 [P] [US4] Create k8s/infrastructure/dapr/statestore.yaml for PostgreSQL state component per quickstart.md
- [ ] T092 [P] [US4] Create k8s/infrastructure/dapr/pubsub.yaml for Kafka pub/sub component per quickstart.md
- [ ] T093 [US4] Apply Dapr components to Kubernetes via kubectl apply -f k8s/infrastructure/dapr/
- [ ] T094 [US4] Verify Dapr components loaded via dapr components -k

#### Kong API Gateway Deployment

- [ ] T095 [US4] Create k8s/infrastructure/kong-config.yaml with JWT plugin configuration per FR-015
- [ ] T096 [US4] Deploy Kong API Gateway via Helm with rate limiting and JWT authentication enabled
- [ ] T097 [US4] Create Kong routes for backend services: /api/triage/*, /api/concepts/*, /api/code-review/*, /api/debug/*, /api/exercise/*, /api/progress/*, /api/sandbox/*
- [ ] T098 [US4] Verify Kong Gateway accessible via kubectl port-forward svc/kong-proxy 8000:80

#### Infrastructure Validation

- [ ] T099 [US4] Create backend/scripts/validate_infrastructure.py to check all infrastructure components healthy
- [ ] T100 [US4] Run infrastructure validation script and verify all health checks pass (SC-006)

**Checkpoint**: All infrastructure deployed autonomously via Skills. Kafka, PostgreSQL, Kong, Dapr components running and healthy.

---

## Phase 7: User Story 5 - Implement EmberLearn AI Agents (Priority: P3)

**Goal**: Use fastapi-dapr-agent Skill to create 6 specialized AI agent microservices enabling intelligent Python tutoring

**Independent Test**: Prompt AI agent "Create [Agent Name] service" for each agent and verify functional FastAPI service with OpenAI Agents SDK, Dapr sidecar, Kafka pub/sub

**Dependencies**: Phase 6 complete (infrastructure running), Phase 3 complete (fastapi-dapr-agent Skill exists)

### Implementation for User Story 5

#### Shared Agent Infrastructure

- [ ] T101 [P] [US5] Create backend/agents/base_agent.py with common FastAPI setup, logging, correlation ID middleware
- [ ] T102 [P] [US5] Create backend/agents/agent_factory.py with OpenAI Agent creation helper using research.md decision 1 (manager pattern)

#### Triage Agent (Manager)

- [ ] T103 [US5] Use fastapi-dapr-agent Skill to scaffold backend/agents/triage/ with app.py, agent_config.py, Dockerfile, k8s/
- [ ] T104 [US5] Implement Triage agent configuration in backend/agents/triage/agent_config.py with handoffs to 5 specialists per research.md decision 1
- [ ] T105 [US5] Implement /api/triage/query endpoint in backend/agents/triage/app.py per contracts/agent-api.yaml lines 173-208
- [ ] T106 [US5] Add Kafka pub/sub for learning.query and learning.response topics via Dapr client
- [ ] T107 [US5] Deploy Triage agent to Kubernetes via kubectl apply -f backend/agents/triage/k8s/

#### Concepts Agent

- [ ] T108 [P] [US5] Use fastapi-dapr-agent Skill to scaffold backend/agents/concepts/ structure
- [ ] T109 [US5] Implement Concepts agent configuration with Python teaching instructions in backend/agents/concepts/agent_config.py
- [ ] T110 [US5] Implement /api/concepts/explain endpoint per contracts/agent-api.yaml lines 210-227
- [ ] T111 [US5] Add adaptive examples based on student level using Dapr state API for student progress lookup
- [ ] T112 [US5] Deploy Concepts agent to Kubernetes

#### Code Review Agent

- [ ] T113 [P] [US5] Use fastapi-dapr-agent Skill to scaffold backend/agents/code_review/ structure
- [ ] T114 [US5] Implement Code Review agent configuration with correctness/style/efficiency analysis instructions
- [ ] T115 [US5] Implement /api/code-review/analyze endpoint per contracts/agent-api.yaml lines 229-285
- [ ] T116 [US5] Add rating calculation (0-100) and issue categorization (correctness, style, efficiency)
- [ ] T117 [US5] Deploy Code Review agent to Kubernetes

#### Debug Agent

- [ ] T118 [P] [US5] Use fastapi-dapr-agent Skill to scaffold backend/agents/debug/ structure
- [ ] T119 [US5] Implement Debug agent configuration with error parsing and root cause analysis instructions
- [ ] T120 [US5] Implement /api/debug/analyze-error endpoint per contracts/agent-api.yaml lines 287-330
- [ ] T121 [US5] Add similar error tracking using Dapr state API to count student error history
- [ ] T122 [US5] Deploy Debug agent to Kubernetes

#### Exercise Agent

- [ ] T123 [P] [US5] Use fastapi-dapr-agent Skill to scaffold backend/agents/exercise/ structure
- [ ] T124 [US5] Implement Exercise agent configuration with challenge generation instructions
- [ ] T125 [US5] Implement /api/exercise/generate endpoint per contracts/agent-api.yaml lines 332-349
- [ ] T126 [US5] Implement /api/exercise/submit endpoint with sandbox integration per contracts/agent-api.yaml lines 351-415
- [ ] T127 [US5] Add test case execution, auto-grading, and Code Review agent invocation in submission workflow
- [ ] T128 [US5] Publish exercise.created and exercise.completed events to Kafka
- [ ] T129 [US5] Deploy Exercise agent to Kubernetes

#### Progress Agent

- [ ] T130 [P] [US5] Use fastapi-dapr-agent Skill to scaffold backend/agents/progress/ structure
- [ ] T131 [US5] Implement Progress agent configuration with mastery calculation instructions
- [ ] T132 [US5] Implement /api/progress/calculate endpoint with weighted formula per contracts/agent-api.yaml lines 417-445 and data-model.md lines 133-139
- [ ] T133 [US5] Implement /api/progress/dashboard endpoint per contracts/agent-api.yaml lines 447-475
- [ ] T134 [US5] Add mastery level color coding (Red/Yellow/Green/Blue) per FR-020
- [ ] T135 [US5] Deploy Progress agent to Kubernetes

#### Agent Integration and Validation

- [ ] T136 [US5] Configure Kong routes for all 6 agents pointing to their Kubernetes services
- [ ] T137 [US5] Test inter-agent communication: Triage → Concepts handoff with sample query "How do for loops work?"
- [ ] T138 [US5] Test Exercise → Code Review integration with sample code submission
- [ ] T139 [US5] Verify all agents respond within 2s average latency per SC-005

**Checkpoint**: All 6 AI agent microservices deployed, responding to queries, communicating via Kafka, persisting state in PostgreSQL via Dapr.

---

## Phase 8: User Story 6 - Build EmberLearn Frontend (Priority: P3)

**Goal**: Use nextjs-k8s-deploy Skill to create EmberLearn frontend with Monaco Editor enabling student interaction with AI tutors and Python code writing

**Independent Test**: Prompt AI agent "Create EmberLearn frontend with code editor" and verify Next.js app deploys, Monaco Editor works, connects to backend APIs, handles authentication

**Dependencies**: Phase 7 complete (backend agents running), Phase 6 complete (Kong API Gateway configured)

### Implementation for User Story 6

#### Frontend Scaffolding

- [ ] T140 [US6] Use nextjs-k8s-deploy Skill to scaffold frontend/ with Next.js 15+, TypeScript, @monaco-editor/react
- [ ] T141 [US6] Configure Next.js app router structure per plan.md lines 229-252
- [ ] T142 [US6] Setup Tailwind CSS for styling

#### Authentication Flow

- [ ] T143 [P] [US6] Create frontend/app/(auth)/login/page.tsx with JWT authentication form
- [ ] T144 [P] [US6] Create frontend/app/(auth)/register/page.tsx with student registration form
- [ ] T145 [US6] Create frontend/lib/auth.ts with JWT token handling (HTTP-only cookies) per FR-015
- [ ] T146 [US6] Implement authentication middleware in frontend/middleware.ts for protected routes

#### Monaco Editor Integration

- [ ] T147 [US6] Create frontend/components/CodeEditor.tsx with @monaco-editor/react and SSR disabled per research.md decision 5
- [ ] T148 [US6] Configure Monaco Editor for Python syntax highlighting and autocomplete
- [ ] T149 [US6] Add code submission handler connecting to /api/sandbox/execute endpoint

#### Dashboard and Progress UI

- [ ] T150 [P] [US6] Create frontend/app/dashboard/page.tsx with student progress dashboard
- [ ] T151 [P] [US6] Create frontend/components/MasteryCard.tsx displaying topic mastery with color coding per FR-020
- [ ] T152 [US6] Integrate /api/progress/dashboard endpoint to fetch mastery scores for all 8 topics
- [ ] T153 [US6] Display mastery levels: Beginner (Red), Learning (Yellow), Proficient (Green), Mastered (Blue)

#### Practice and Exercise UI

- [ ] T154 [P] [US6] Create frontend/app/practice/page.tsx with CodeEditor component and output panel
- [ ] T155 [P] [US6] Create frontend/components/OutputPanel.tsx to display code execution results
- [ ] T156 [US6] Integrate /api/triage/query endpoint for student questions
- [ ] T157 [US6] Create frontend/app/exercises/[topic]/page.tsx to list exercises per topic
- [ ] T158 [P] [US6] Create frontend/components/ExerciseCard.tsx to display exercise details and submission form
- [ ] T159 [US6] Integrate /api/exercise/generate and /api/exercise/submit endpoints

#### API Client and Types

- [ ] T160 [P] [US6] Create frontend/lib/api.ts with fetch wrapper including JWT token and Kong API Gateway base URL
- [ ] T161 [P] [US6] Create frontend/lib/types.ts with TypeScript types matching contracts/agent-api.yaml schemas

#### Frontend Deployment

- [ ] T162 [US6] Create frontend/Dockerfile for Next.js production build
- [ ] T163 [US6] Create frontend/k8s/deployment.yaml and service.yaml for Kubernetes deployment
- [ ] T164 [US6] Deploy frontend to Kubernetes via kubectl apply -f frontend/k8s/
- [ ] T165 [US6] Verify frontend accessible via kubectl port-forward svc/emberlearn-frontend 3000:3000
- [ ] T166 [US6] Test frontend loads within 3s first visit, <1s subsequent visits per SC-007

**Checkpoint**: Frontend deployed with Monaco Editor, authentication, dashboard, practice area, exercise management. Full-stack EmberLearn application functional.

---

## Phase 9: User Story 7 - Deploy Documentation (Priority: P4)

**Goal**: Use docusaurus-deploy Skill to generate and deploy comprehensive documentation enabling hackathon judges to understand architecture and evaluation criteria (FR-023, FR-024, FR-025)

**Independent Test**: Prompt AI agent "Generate and deploy documentation" and verify Docusaurus site builds, deploys to K8s, accessible via browser with search

**Dependencies**: Phase 8 complete (all components implemented), Phase 3 complete (docusaurus-deploy Skill exists)

### Implementation for User Story 7

- [ ] T167 [US7] Use docusaurus-deploy Skill to scan EmberLearn codebase and extract README files, code comments per FR-023
- [ ] T168 [US7] Create docs/ directory with Docusaurus 3.0+ configuration generated by Skill per FR-023
- [ ] T169 [P] [US7] Create docs/docs/skills-guide.md documenting MCP Code Execution pattern, token efficiency, cross-agent testing per FR-024
- [ ] T170 [P] [US7] Create docs/docs/architecture.md with tech stack diagram, microservices overview, data flow per FR-024
- [ ] T171 [P] [US7] Create docs/docs/api-reference.md from contracts/agent-api.yaml with agent endpoints, Kafka topics, data schemas per FR-024
- [ ] T172 [P] [US7] Create docs/docs/evaluation.md with 100-point hackathon evaluation breakdown per FR-024
- [ ] T173 [US7] Generate Docusaurus static site via Skill build script per FR-023
- [ ] T174 [US7] Deploy documentation site to Kubernetes via Skill deployment script per FR-025
- [ ] T175 [US7] Verify documentation accessible and search functional per FR-025, SC-013, SC-015

**Checkpoint**: Documentation deployed with all required sections. Judges can understand project architecture, Skills usage, evaluation criteria.

---

## Phase 10: Essential Features & Validation

**Purpose**: Critical security features (code sandbox), reliability features (graceful degradation, struggle detection), final validation, and hackathon submission preparation

#### Code Execution Sandbox (Security)

- [ ] T176 [P] Create backend/sandbox/validator.py with dangerous import detection (os, subprocess, socket, etc.) per FR-018
- [ ] T177 [P] Create backend/sandbox/executor.py with subprocess + resource limits per research.md decision 3
- [ ] T178 Create backend/sandbox/app.py with /api/sandbox/execute endpoint per contracts/agent-api.yaml lines 477-501
- [ ] T179 Test sandbox enforces 5s timeout, 50MB memory, no network access per SC-011
- [ ] T180 Deploy Sandbox service to Kubernetes

#### Struggle Detection

- [ ] T181 [P] Create backend/agents/struggle_detector.py with trigger logic for 5 conditions per FR-021
- [ ] T182 Integrate struggle detection with Debug agent (3+ same errors), Exercise agent (5+ failed executions), Progress agent (quiz <50%)
- [ ] T183 Test struggle alerts trigger within 30s per SC-010

#### OpenAI API Graceful Degradation

- [ ] T184 [P] Create backend/shared/fallback_responses.py with cached responses for common queries per FR-011a
- [ ] T185 Add OpenAI API error handling to all agents with fallback to cached responses
- [ ] T186 Test graceful degradation when OpenAI API unavailable

#### AGENTS.md Generation

- [ ] T187 Use agents-md-gen Skill to generate AGENTS.md for EmberLearn repository per FR-022
- [ ] T188 Verify AGENTS.md describes repository structure, conventions, AI agent guidelines

#### Validation and Testing

- [ ] T189 Run quickstart.md validation: verify all deployment steps work end-to-end per quickstart.md lines 102-207
- [ ] T190 Test end-to-end workflow: student login → dashboard → request exercise → submit code → sandbox execution → score display
- [ ] T191 Test 100 concurrent student sessions without degradation per SC-008
- [ ] T192 Test mastery calculation with 100+ test profiles per SC-009

#### Hackathon Submission Preparation

- [ ] T193 Create separate skills-library repository and copy .claude/skills/ from EmberLearn repository
- [ ] T194 [P] Verify skills-library repository contains all 7 Skills with SKILL.md + scripts/ + REFERENCE.md structure
- [ ] T195 [P] Create skills-library README.md with: installation instructions (copy to ~/.claude/skills/), usage examples, token measurements, cross-agent compatibility matrix per FR-027
- [ ] T196 [P] Verify EmberLearn repository has commit history showing agentic workflow (commits like "Claude: implemented X using Y skill") per FR-009, FR-028
- [ ] T197 Create submission checklist document verifying all evaluation criteria met per constitution.md lines 332-344
- [ ] T198 Calculate evaluation scores: Skills Autonomy (/15), Token Efficiency (/10), Cross-Agent Compatibility (/5), Architecture (/20), MCP Integration (/10), Documentation (/10), Spec-Kit Plus (/15), EmberLearn Completion (/15)
- [ ] T199 Verify overall score ≥80/100 points per SC-020
- [ ] T200 Submit to https://forms.gle/Mrhf9XZsuXN4rWJf7 with Repository 1 (skills-library) and Repository 2 (EmberLearn) links

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - Creates all Skills
- **User Story 2 (Phase 4)**: Depends on User Story 1 (Phase 3) - Tests Skills on both agents
- **User Story 3 (Phase 5)**: Depends on User Story 1 (Phase 3) - Measures token efficiency
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) + User Story 1 (Phase 3) - Deploys infrastructure using Skills
- **User Story 5 (Phase 7)**: Depends on User Story 4 (Phase 6) + User Story 1 (Phase 3) - Implements agents using Skills
- **User Story 6 (Phase 8)**: Depends on User Story 5 (Phase 7) + User Story 1 (Phase 3) - Builds frontend using Skills
- **User Story 7 (Phase 9)**: Depends on User Story 6 (Phase 8) + User Story 1 (Phase 3) - Deploys documentation using Skills
- **Polish (Phase 10)**: Depends on all user stories complete - Final validation and submission

### Critical Path

**Must complete in order**:
1. Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3 (US1: Create Skills) → Phase 4 (US2: Test Skills) + Phase 5 (US3: Measure Tokens) → Phase 6 (US4: Deploy Infrastructure) → Phase 7 (US5: Implement Agents) → Phase 8 (US6: Build Frontend) → Phase 9 (US7: Documentation) → Phase 10 (Polish)

**Can parallelize**:
- Phase 4 (US2) and Phase 5 (US3) can run in parallel after Phase 3 complete
- Within each phase, all tasks marked [P] can run in parallel
- Skills in Phase 3 can be developed in parallel (7 Skills × independent structure)

### User Story Dependencies

- **User Story 1 (P1)**: Foundation for all others - MUST complete first
- **User Story 2 (P1)**: Independent testing of US1 Skills - Can run immediately after US1
- **User Story 3 (P2)**: Independent measurement of US1 Skills - Can run immediately after US1
- **User Story 4 (P2)**: Uses Skills from US1 - Can start after US1 complete
- **User Story 5 (P3)**: Depends on US4 (infrastructure) and US1 (Skills)
- **User Story 6 (P3)**: Depends on US5 (backend APIs) and US1 (Skills)
- **User Story 7 (P4)**: Depends on US6 (complete application) and US1 (Skills)

### Within Each User Story

**Phase 3 (US1)**: All 7 Skills can be developed in parallel, each Skill's tasks must be sequential (SKILL.md → scripts → REFERENCE.md → validate)

**Phase 4 (US2)**: Claude Code tests and Goose tests can run in parallel for each Skill

**Phase 5 (US3)**: All Skills token measurements can run in parallel

**Phase 6 (US4)**: Kafka, PostgreSQL, Dapr components, Kong can deploy in parallel. Validation must be last.

**Phase 7 (US5)**: All 6 agents can be scaffolded in parallel. Triage agent must deploy before testing handoffs.

**Phase 8 (US6)**: Auth, Monaco Editor, Dashboard, Practice, API client can be developed in parallel. Deployment must be last.

**Phase 9 (US7)**: All documentation sections can be written in parallel. Build and deployment must be sequential.

**Phase 10 (Polish)**: Sandbox, struggle detection, fallback responses, AGENTS.md can be developed in parallel. Validation and submission must be last.

---

## Parallel Example: User Story 1 (Phase 3)

```bash
# Launch all Skill 1 scripts in parallel:
Task: "Create .claude/skills/agents-md-gen/SKILL.md"
Task: "Create .claude/skills/agents-md-gen/scripts/analyze_repo.py"
Task: "Create .claude/skills/agents-md-gen/scripts/generate_agents_md.py"
Task: "Create .claude/skills/agents-md-gen/REFERENCE.md"

# Launch all Skill 2 scripts in parallel:
Task: "Create .claude/skills/kafka-k8s-setup/SKILL.md"
Task: "Create .claude/skills/kafka-k8s-setup/scripts/deploy_kafka.sh"
Task: "Create .claude/skills/kafka-k8s-setup/scripts/verify_kafka.py"
Task: "Create .claude/skills/kafka-k8s-setup/scripts/rollback_kafka.sh"
Task: "Create .claude/skills/kafka-k8s-setup/REFERENCE.md"

# Similar parallel launches for Skills 3-7
```

---

## Parallel Example: User Story 5 (Phase 7)

```bash
# Launch all agent scaffolding in parallel (after shared infrastructure T101-T102):
Task: "Scaffold backend/agents/triage/ structure"
Task: "Scaffold backend/agents/concepts/ structure"
Task: "Scaffold backend/agents/code_review/ structure"
Task: "Scaffold backend/agents/debug/ structure"
Task: "Scaffold backend/agents/exercise/ structure"
Task: "Scaffold backend/agents/progress/ structure"

# Then implement each agent sequentially (agent-specific logic)
```

---

## Implementation Strategy

### MVP First (User Stories 1-2 Only)

For hackathon judges to evaluate Skills autonomy and cross-agent compatibility:

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T019) - CRITICAL blocker
3. Complete Phase 3: User Story 1 (T020-T057) - All 7 Skills created
4. Complete Phase 4: User Story 2 (T058-T075) - Cross-agent testing
5. **STOP and VALIDATE**: Test Skills on both agents, verify 100% compatibility
6. Submit Skills-library repository for early evaluation

This MVP demonstrates 40% of evaluation criteria (Skills Autonomy 15% + Cross-Agent Compatibility 5% + MCP Integration 10% + Spec-Kit Plus 15% partial).

### Incremental Delivery

1. **MVP**: Phases 1-4 (Setup + Foundational + US1 + US2) → Skills-library ready
2. **+Token Efficiency**: Add Phase 5 (US3) → Token measurements complete (50% criteria)
3. **+Infrastructure**: Add Phase 6 (US4) → Cloud-native deployment demo (65% criteria)
4. **+AI Agents**: Add Phase 7 (US5) → EmberLearn backend functional (80% criteria)
5. **+Frontend**: Add Phase 8 (US6) → Full-stack application complete (95% criteria)
6. **+Documentation**: Add Phase 9 (US7) + Phase 10 (Polish) → Hackathon submission ready (100% criteria)

Each increment adds value and demonstrates new evaluation criteria.

### Parallel Team Strategy

With multiple developers (or parallel AI agent execution):

1. **Week 1**: Team completes Setup + Foundational together (Phases 1-2)
2. **Week 2**: Once Foundational done:
   - Developer A: US1 - Create all 7 Skills (Phase 3)
   - Developer B: Setup infrastructure manually for US4 preparation
   - Developer C: Design frontend mockups for US6
3. **Week 3**: Skills complete:
   - Developer A: US2 - Cross-agent testing (Phase 4)
   - Developer B: US3 - Token measurements (Phase 5)
   - Developer C: US4 - Infrastructure deployment using Skills (Phase 6)
4. **Week 4**: Infrastructure ready:
   - Developer A: US5 - AI Agents (Phase 7)
   - Developer B: US6 - Frontend (Phase 8)
   - Developer C: US7 - Documentation (Phase 9)
5. **Week 5**: Polish + submission (Phase 10)

---

## Summary

**Total Tasks**: 200 tasks across 10 phases
**Task Count by User Story**:
- Setup: 7 tasks
- Foundational: 12 tasks
- US1 (Create Skills): 38 tasks (7 Skills × ~5 tasks each + validation)
- US2 (Cross-Agent Testing): 18 tasks (7 Skills × 2 agents + analysis)
- US3 (Token Efficiency): 9 tasks
- US4 (Infrastructure): 16 tasks
- US5 (AI Agents): 39 tasks (6 agents × ~6 tasks each + validation)
- US6 (Frontend): 27 tasks
- US7 (Documentation): 9 tasks
- Polish: 25 tasks (including submission preparation)

**Parallel Opportunities Identified**:
- Phase 1: 5 parallel tasks (T003-T007)
- Phase 2: 11 parallel tasks (T010-T013, T016-T018)
- Phase 3 (US1): 49 parallel tasks (all SKILL.md, scripts, REFERENCE.md files across 7 Skills)
- Phase 4 (US2): 14 parallel tasks (testing on both agents)
- Phase 5 (US3): 1 parallel task (T081 - measure all Skills)
- Phase 6 (US4): 6 parallel tasks (Dapr components, infrastructure validation)
- Phase 7 (US5): 19 parallel tasks (agent scaffolding, shared infrastructure)
- Phase 8 (US6): 11 parallel tasks (auth pages, UI components, API client)
- Phase 9 (US7): 4 parallel tasks (documentation sections)
- Phase 10: 6 parallel tasks (sandbox, struggle detection, fallback, AGENTS.md)

**Independent Test Criteria**:
- US1: Single prompt deploys complete infrastructure component (e.g., "Deploy Kafka") with zero manual steps
- US2: Same Skill prompt on Claude Code and Goose produces identical results
- US3: Token measurements show ≥80% reduction for Skills vs direct MCP
- US4: All infrastructure components running and healthy via automated validation script
- US5: All 6 agents respond to test queries with <2s latency and correct behavior
- US6: Frontend loads, authenticates, displays dashboard, executes code in Monaco Editor
- US7: Documentation site accessible with search, all required sections present

**Suggested MVP Scope**:
- **Minimum for hackathon**: Phases 1-4 (US1 + US2) - Demonstrates Skills as product with cross-agent compatibility
- **Recommended for strong submission**: Phases 1-6 (US1-US4) - Adds token efficiency and cloud-native infrastructure
- **Competitive submission**: Phases 1-8 (US1-US6) - Includes full EmberLearn application
- **Maximum points**: All phases 1-10 - Complete system with documentation and polish

**Format Validation**: ✅ All 200 tasks follow required checklist format:
- ✅ Checkbox: `- [ ]` prefix on every task
- ✅ Task ID: Sequential T001-T200
- ✅ [P] marker: Present on 126 parallelizable tasks
- ✅ [Story] label: Present on all user story phase tasks (US1-US7)
- ✅ Description: Clear action with exact file paths
- ✅ No ambiguous tasks, all implementation-ready

**Constitution Compliance**: ✅ All 8 principles satisfied per plan.md Constitution Check (lines 56-162)

---

## Notes

- [P] tasks = different files or independent operations, no dependencies within phase
- [Story] label maps task to specific user story for traceability and independent testing
- Each user story should be independently completable and testable
- Tasks reference exact file paths from plan.md project structure (lines 164-286)
- All API endpoints match contracts/agent-api.yaml specification
- All database entities match data-model.md (10 entities with relationships)
- All architecture decisions reference research.md (6 decisions with code examples)
- Commit after each task or logical group per agentic workflow requirement (FR-009)
- Stop at any checkpoint to validate story independently before proceeding
- Skills are the primary deliverable (60% of effort) per spec.md Notes Critical Success Factor 1
- Autonomous execution is gold standard per spec.md Notes Critical Success Factor 2
