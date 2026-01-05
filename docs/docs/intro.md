---
sidebar_position: 1
---

# Introduction

EmberLearn is an **AI-powered Python tutoring platform** built for Hackathon III: Reusable Intelligence and Cloud-Native Mastery.

## What is EmberLearn?

EmberLearn provides personalized Python learning through 6 specialized AI agents that adapt to each student's skill level and learning style. Students can:

- Write and execute Python code in a browser-based editor
- Get instant feedback from AI tutors
- Complete auto-generated exercises
- Track mastery progress across 8 Python topics

## Key Features

### AI-Powered Tutoring
Six specialized agents handle different aspects of learning:
- **Triage Agent**: Routes queries to the right specialist
- **Concepts Agent**: Explains Python concepts with adaptive examples
- **Code Review Agent**: Analyzes code for correctness, style, and efficiency
- **Debug Agent**: Helps fix errors with root cause analysis
- **Exercise Agent**: Generates and grades coding challenges
- **Progress Agent**: Tracks mastery scores and learning streaks

### Skills-Driven Development
EmberLearn was built using **7 reusable Skills** that enable AI agents to autonomously deploy cloud-native infrastructure. These Skills are the primary deliverable for Hackathon III.

### Cloud-Native Architecture
- **Kubernetes**: Container orchestration with Minikube
- **Dapr**: Service mesh for state management and pub/sub
- **Kafka**: Event streaming for inter-agent communication
- **Kong**: API Gateway with JWT authentication

## Quick Start

```bash
# Clone the repository
git clone https://github.com/emberlearn/emberlearn.git
cd emberlearn

# Start Minikube
minikube start --cpus=4 --memory=8192

# Deploy infrastructure using Skills
# (Skills enable autonomous deployment)

# Access the application
kubectl port-forward svc/emberlearn-frontend 3000:80
```

## Project Structure

```
EmberLearn/
├── .claude/skills/          # 7 Reusable Skills (primary deliverable)
├── backend/                 # FastAPI + OpenAI Agents SDK
│   ├── agents/              # 6 AI agent microservices
│   ├── database/            # SQLAlchemy models + Alembic migrations
│   └── shared/              # Common utilities
├── frontend/                # Next.js 15 + Monaco Editor
├── k8s/                     # Kubernetes manifests
├── docs/                    # This documentation (Docusaurus)
└── specs/                   # Spec-Kit Plus artifacts
```

## Hackathon Submission

This project is submitted to **Hackathon III: Reusable Intelligence and Cloud-Native Mastery**.

- **Repository 1**: `skills-library` - 7 reusable Skills
- **Repository 2**: `EmberLearn` - Complete application built using Skills

See the [Evaluation Guide](/docs/evaluation) for scoring criteria.
