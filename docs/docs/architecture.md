---
sidebar_position: 2
---

# Architecture

EmberLearn follows a cloud-native microservices architecture with event-driven communication.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Kong API Gateway                          │
│                    (JWT Auth, Rate Limiting)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   Frontend    │     │  Triage Agent │     │ Sandbox       │
│  (Next.js)    │     │  (Router)     │     │ (Executor)    │
└───────────────┘     └───────────────┘     └───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │           │         │         │           │
        ▼           ▼         ▼         ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│Concepts │ │  Code   │ │  Debug  │ │Exercise │ │Progress │
│ Agent   │ │ Review  │ │  Agent  │ │  Agent  │ │  Agent  │
└─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘
        │           │         │         │           │
        └───────────┴─────────┴─────────┴───────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
            ┌───────────────┐   ┌───────────────┐
            │     Kafka     │   │  PostgreSQL   │
            │   (Pub/Sub)   │   │   (State)     │
            └───────────────┘   └───────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Frontend | Next.js 15, Monaco Editor | Code editor, UI |
| API Gateway | Kong 3.5+ | Auth, routing, rate limiting |
| Agents | FastAPI, OpenAI Agents SDK | AI tutoring logic |
| Service Mesh | Dapr 1.13+ | State, pub/sub, invocation |
| Messaging | Kafka 3.6+ (Bitnami) | Event streaming |
| Database | PostgreSQL (Neon) | Persistent storage |
| Orchestration | Kubernetes (Minikube) | Container management |

## AI Agents

Each agent is a FastAPI microservice with a Dapr sidecar:

### Triage Agent
- **Purpose**: Route student queries to specialist agents
- **Model**: GPT-4o-mini (fast routing)
- **Endpoint**: `POST /api/triage/query`

### Concepts Agent
- **Purpose**: Explain Python concepts with adaptive examples
- **Model**: GPT-4o (detailed explanations)
- **Endpoint**: `POST /api/concepts/explain`

### Code Review Agent
- **Purpose**: Analyze code for correctness, style, efficiency
- **Model**: GPT-4o
- **Endpoint**: `POST /api/code-review/analyze`
- **Output**: Rating (0-100), categorized issues

### Debug Agent
- **Purpose**: Parse errors, identify root cause, suggest fixes
- **Model**: GPT-4o
- **Endpoint**: `POST /api/debug/analyze-error`

### Exercise Agent
- **Purpose**: Generate challenges, auto-grade submissions
- **Model**: GPT-4o
- **Endpoints**: `POST /api/exercise/generate`, `POST /api/exercise/submit`

### Progress Agent
- **Purpose**: Calculate mastery scores, track streaks
- **Model**: GPT-4o-mini
- **Endpoint**: `GET /api/progress/dashboard`

## Data Flow

### Query Flow
1. Student submits question via frontend
2. Kong validates JWT, routes to Triage Agent
3. Triage classifies query, delegates to specialist
4. Specialist processes with OpenAI, returns response
5. Events published to Kafka for analytics

### Exercise Flow
1. Student requests exercise for topic
2. Exercise Agent generates challenge via OpenAI
3. Student submits solution
4. Sandbox executes code (5s timeout, 50MB limit)
5. Exercise Agent grades, invokes Code Review
6. Progress Agent updates mastery scores

## Kafka Topics

| Topic | Publisher | Subscriber | Purpose |
|-------|-----------|------------|---------|
| `learning.query` | Triage | Analytics | Track queries |
| `learning.response` | All Agents | Analytics | Track responses |
| `code.executed` | Sandbox | Debug, Progress | Execution events |
| `code.reviewed` | Code Review | Progress | Review results |
| `exercise.created` | Exercise | Progress | New exercises |
| `exercise.completed` | Exercise | Progress | Submissions |
| `struggle.detected` | All Agents | Progress | Struggle alerts |
| `progress.updated` | Progress | Frontend | Mastery changes |

## Mastery Calculation

```
Mastery Score = (Exercise × 0.4) + (Quiz × 0.3) + (CodeQuality × 0.2) + (Streak × 0.1)
```

### Mastery Levels
| Level | Score Range | Color |
|-------|-------------|-------|
| Beginner | 0-39% | Red |
| Learning | 40-69% | Yellow |
| Proficient | 70-89% | Green |
| Mastered | 90-100% | Blue |

## Security

- **Authentication**: JWT tokens with RS256 signing (24h expiry)
- **Secrets**: Kubernetes Secrets for API keys
- **Sandbox**: Isolated code execution (no network, limited resources)
- **PII**: Tokenized before sending to AI models
