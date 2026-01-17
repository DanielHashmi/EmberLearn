# System Architecture

EmberLearn is a cloud-native AI-powered Python tutoring platform built with microservices architecture.

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         KUBERNETES CLUSTER                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ││
│  │  │   Next.js   │    │   FastAPI   │    │   FastAPI   │    ││
│  │  │  Frontend   │    │  Triage Svc │    │ Concepts Svc│    ││
│  │  │ +Monaco Ed  │    │ +Dapr+Agent │    │ +Dapr+Agent │    ││
│  │  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    ││
│  │         │                 │                  │             ││
│  │         └────────────┬────┴──────────────────┘             ││
│  │                      ▼                                      ││
│  │  ┌─────────────────────────────────────────────────────┐   ││
│  │  │                      KAFKA                          │   ││
│  │  │  learning.* | code.* | exercise.* | struggle.*      │   ││
│  │  └─────────────────────────────────────────────────────┘   ││
│  │                      │                                      ││
│  │         ┌────────────┴────────────┐                        ││
│  │         ▼                         ▼                        ││
│  │  ┌─────────────┐          ┌─────────────┐                  ││
│  │  │ PostgreSQL  │          │   Dapr      │                  ││
│  │  │  Neon DB    │          │  Sidecars   │                  ││
│  │  └─────────────┘          └─────────────┘                  ││
│  └─────────────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 15+ | User interface with Monaco Editor |
| Auth | Better Auth | JWT authentication (RS256) |
| Backend | FastAPI | AI agent microservices |
| AI | OpenAI SDK | GPT-4o-mini for tutoring |
| Service Mesh | Dapr 1.13+ | State, pub/sub, service invocation |
| Messaging | Kafka 3.6+ | Event-driven communication |
| Database | Neon PostgreSQL | User data, progress, submissions |
| Gateway | Kong 3.5+ | API routing, JWT validation |
| Orchestration | Kubernetes | Container orchestration |

## AI Agents

### Agent Architecture

Each agent is a FastAPI microservice with:
- Dapr sidecar for state and pub/sub
- OpenAI SDK for AI capabilities
- Structured logging with correlation IDs
- Health and readiness probes

### Agent Responsibilities

| Agent | Port | Responsibility |
|-------|------|----------------|
| Triage | 8001 | Route queries to specialists |
| Concepts | 8002 | Explain Python concepts |
| Code Review | 8003 | Analyze code quality |
| Debug | 8004 | Help fix errors |
| Exercise | 8005 | Generate and grade exercises |
| Progress | 8006 | Track mastery scores |
| Sandbox | 8007 | Execute code safely |

## Event-Driven Communication

### Kafka Topics

- `learning.events` - Concept explanations, chat sessions
- `code.events` - Code executions, reviews
- `exercise.events` - Exercise generation, submissions
- `struggle.alerts` - Student struggle detection

### Event Flow

1. User interacts with frontend
2. Request goes through Kong API Gateway
3. Triage Agent routes to specialist
4. Specialist processes and publishes event
5. Progress Agent updates mastery
6. Struggle Detector monitors for issues

## Security

### Authentication
- JWT tokens with RS256 signing
- 24-hour token expiry
- Refresh token rotation

### Code Sandbox
- 5-second execution timeout
- 50MB memory limit
- No network access
- No filesystem access (except temp)
- Standard library imports only

### API Security
- Kong JWT plugin validation
- Rate limiting per endpoint
- CORS configuration
- Request size limits

## Mastery Calculation

```
Mastery = 0.40 × Exercise Score
        + 0.30 × Quiz Score
        + 0.20 × Code Quality
        + 0.10 × Consistency (Streak)
```

### Mastery Levels
- 0-40%: Beginner (Red)
- 41-70%: Learning (Yellow)
- 71-90%: Proficient (Green)
- 91-100%: Mastered (Blue)
