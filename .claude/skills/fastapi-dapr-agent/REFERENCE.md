# FastAPI Dapr Agent - Reference Documentation

## Overview

Generates **complete production-ready AI agent microservices** with FastAPI, OpenAI Agents SDK, Dapr, and Kafka integration.

## Token Efficiency

- **Without Skill**: ~15,000 tokens per agent (load docs, specs, examples)
- **With Skill**: ~150 tokens (SKILL.md + result)
- **Reduction**: 99%

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `KAFKA_BROKERS`: Kafka broker addresses

### Agent Specifications

6 pre-configured agents:
1. **Triage**: Routes queries to specialists
2. **Concepts**: Explains Python concepts
3. **Code Review**: Analyzes code quality
4. **Debug**: Parses errors and suggests fixes
5. **Exercise**: Generates and grades challenges
6. **Progress**: Tracks mastery scores

## Troubleshooting

**Agent not responding**: Check OPENAI_API_KEY in secrets, verify Dapr sidecar
**Kafka events not publishing**: Verify Kafka pod running, check Dapr component
**High latency**: Increase K8s resources, use faster model (gpt-4o-mini)
