# QuickStart Guide: EmberLearn Hackathon III

**Date**: 2026-01-05
**Feature**: 001-hackathon-iii
**Prerequisites**: Docker, Minikube, kubectl, helm, OpenAI API key

---

## Phase-by-Phase Implementation Order

### Phase 1: Skills Library Creation (P1 - Foundation)
**Goal**: Create 7 core Skills with MCP Code Execution pattern

1. **agents-md-gen**: Generate AGENTS.md files
2. **kafka-k8s-setup**: Deploy Kafka via Helm
3. **postgres-k8s-setup**: Deploy PostgreSQL via Helm
4. **fastapi-dapr-agent**: Scaffold FastAPI + Dapr + OpenAI Agent service
5. **mcp-code-execution**: Wrap MCP server in executable scripts
6. **nextjs-k8s-deploy**: Deploy Next.js + Monaco Editor
7. **docusaurus-deploy**: Deploy documentation site

**Output**: `.claude/skills/<skill-name>/` with SKILL.md + scripts/ + REFERENCE.md

### Phase 2: Cross-Agent Testing (P1 - Blocking)
**Goal**: Test each Skill on both Claude Code and Goose

1. Run each Skill on Claude Code → Document results
2. Run same Skill on Goose → Document results
3. Create compatibility matrix (7 Skills × 2 Agents = 14 tests)
4. Document any incompatibilities and fixes

**Output**: `skills-library/README.md` with compatibility matrix

### Phase 3: Token Efficiency Measurement (P2)
**Goal**: Demonstrate 80-98% token reduction

1. Measure baseline (direct MCP integration) for 1 capability
2. Measure Skills + Scripts approach for same capability
3. Calculate reduction percentage
4. Document measurements for all 7 Skills

**Output**: Token efficiency table in README.md

### Phase 4: Infrastructure Deployment (P2)
**Goal**: Deploy EmberLearn cloud-native stack using Skills

1. Use `kafka-k8s-setup` Skill → Deploy Kafka
2. Use `postgres-k8s-setup` Skill → Deploy Neon PostgreSQL
3. Deploy Kong API Gateway via Helm
4. Deploy Dapr control plane
5. Verify all pods Running and healthy

**Output**: Running Kubernetes cluster with infrastructure

### Phase 5: AI Agent Microservices (P3)
**Goal**: Implement 6 specialized agents with OpenAI Agents SDK

1. Use `fastapi-dapr-agent` Skill → Create Triage agent
2. Use `fastapi-dapr-agent` Skill → Create Concepts agent
3. Use `fastapi-dapr-agent` Skill → Create Code Review agent
4. Use `fastapi-dapr-agent` Skill → Create Debug agent
5. Use `fastapi-dapr-agent` Skill → Create Exercise agent
6. Use `fastapi-dapr-agent` Skill → Create Progress agent
7. Configure Dapr components (PostgreSQL state store, Kafka pub/sub)

**Output**: 6 FastAPI services deployed with Dapr sidecars

### Phase 6: Frontend (P3)
**Goal**: Build Next.js app with Monaco Editor

1. Use `nextjs-k8s-deploy` Skill → Scaffold Next.js app
2. Integrate @monaco-editor/react with SSR disabled
3. Implement authentication (JWT via Kong)
4. Connect to backend agents via Kong API Gateway
5. Add student dashboard with mastery scores

**Output**: Next.js frontend deployed and accessible

### Phase 7: Code Execution Sandbox (P3)
**Goal**: Secure Python code execution

1. Implement subprocess + resource limits sandbox
2. Add validation for dangerous imports
3. Integrate with Exercise Agent submission workflow
4. Test security constraints (5s timeout, 50MB memory)

**Output**: Functional code execution endpoint

### Phase 8: Documentation (P4)
**Goal**: Deploy Docusaurus site via Skill

1. Use `docusaurus-deploy` Skill → Generate docs from code
2. Add Skills development guide
3. Add architecture overview
4. Add API reference (from OpenAPI spec)
5. Add evaluation criteria breakdown

**Output**: Docusaurus site accessible via browser

---

## Local Development Setup

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192 --kubernetes-version=v1.28.0
```

### 2. Install Dapr

```bash
dapr init --kubernetes --wait
dapr status -k
```

### 3. Deploy Infrastructure (Using Skills)

**Kafka**:
```bash
# Using kafka-k8s-setup Skill
claude code "Deploy Kafka on Kubernetes for EmberLearn"
```

**PostgreSQL**:
```bash
# Using postgres-k8s-setup Skill
claude code "Deploy PostgreSQL database for EmberLearn with migrations"
```

**Kong API Gateway**:
```bash
helm repo add kong https://charts.konghq.com
helm install kong kong/kong --namespace default --set ingressController.installCRDs=false
```

### 4. Configure Dapr Components

**PostgreSQL State Store** (`components/statestore.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.postgresql
  version: v2
  metadata:
    - name: connectionString
      secretKeyRef:
        name: postgres-secret
        key: connectionString
```

**Kafka Pub/Sub** (`components/pubsub.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "kafka.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "emberlearn-agents"
```

Apply components:
```bash
kubectl apply -f components/
```

### 5. Deploy AI Agents (Using Skills)

```bash
# Using fastapi-dapr-agent Skill for each agent
claude code "Create Triage agent microservice with Dapr and OpenAI Agents SDK"
claude code "Create Concepts agent microservice with Dapr and OpenAI Agents SDK"
# ... repeat for all 6 agents
```

### 6. Deploy Frontend

```bash
# Using nextjs-k8s-deploy Skill
claude code "Deploy EmberLearn frontend with Monaco Editor integration"
```

### 7. Verify Deployment

```bash
# Check all pods
kubectl get pods

# Check Dapr components
dapr components -k

# Check Kafka topics
kubectl exec -it kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --list

# Forward ports for local access
kubectl port-forward svc/kong-proxy 8000:80 &
kubectl port-forward svc/emberlearn-frontend 3000:3000 &
```

### 8. Access Application

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Health Checks**: http://localhost:8000/health

---

## Testing Workflow

### 1. Test Single Skill

```bash
# Example: Test kafka-k8s-setup
claude code "Deploy Kafka using the kafka-k8s-setup Skill"

# Verify deployment
kubectl get pods -l app=kafka
kubectl exec -it kafka-0 -- kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### 2. Test Cross-Agent Compatibility

**On Claude Code**:
```bash
claude code "Deploy Kafka using kafka-k8s-setup Skill"
# Document: Success, 3 pods Running, topics created
```

**On Goose**:
```bash
goose session start
> Deploy Kafka using kafka-k8s-setup Skill
# Document: Success, 3 pods Running, topics created
```

**Compatibility Matrix Entry**:
| Skill | Claude Code | Goose | Compatible? |
|-------|-------------|-------|-------------|
| kafka-k8s-setup | ✅ Pass | ✅ Pass | ✅ Yes |

### 3. Test Agent Microservice

```bash
# Send test query to Triage agent
curl -X POST http://localhost:8000/api/triage/query \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -d '{
    "student_id": 1,
    "message": "How do for loops work?"
  }'
```

### 4. Test Code Execution Sandbox

```bash
curl -X POST http://localhost:8000/api/sandbox/execute \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "code": "for i in range(5):\n    print(i)"
  }'

# Expected output:
# {
#   "success": true,
#   "stdout": "0\n1\n2\n3\n4\n",
#   "stderr": "",
#   "returncode": 0
# }
```

### 5. Test End-to-End Workflow

1. Student logs in → JWT issued
2. Student views dashboard → Progress agent returns mastery scores
3. Student requests exercise → Exercise agent generates challenge
4. Student submits code → Sandbox executes → Test cases run → Score calculated
5. Student views updated progress → Mastery score recalculated

---

## Troubleshooting

### Pods Not Starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl logs <pod-name> -c daprd  # Check Dapr sidecar
```

### Kafka Connection Issues
```bash
# Check Kafka service
kubectl get svc kafka

# Test connection from within cluster
kubectl run kafka-test --rm -it --image=bitnami/kafka:latest -- \
  kafka-topics.sh --bootstrap-server kafka:9092 --list
```

### OpenAI API Errors
```bash
# Check API key secret
kubectl get secret openai-api-key -o yaml

# Check agent logs for API failures
kubectl logs triage-agent-xxx | grep "openai"
```

### Dapr Component Issues
```bash
# Check component status
dapr components -k

# Check Dapr logs
kubectl logs <pod-name> -c daprd
```

---

## Key Metrics to Track

### Skills Autonomy (15%)
- Single prompt → Complete deployment
- Execution time < 10 minutes per Skill
- Zero manual intervention required

### Token Efficiency (10%)
- Baseline tokens (direct MCP): ~50,000
- Skills + Scripts tokens: ~1,000
- Reduction: 98% (50,000 → 1,000)

### Cross-Agent Compatibility (5%)
- 7 Skills × 2 Agents = 14 tests
- Target: 100% pass rate (14/14)

### Architecture (20%)
- Event-driven: All services use Kafka pub/sub
- Stateless: State in PostgreSQL via Dapr
- Dapr sidecars: All agents use Dapr pattern
- Health checks: All services have /health endpoints

### Performance (SC-005 to SC-012)
- Agent response time: < 2s average
- Frontend load time: < 3s first visit, < 1s subsequent
- Code execution: 5s timeout enforced
- Concurrent sessions: 100+ without degradation

---

## Submission Checklist

### Repository 1: skills-library
- [ ] 7 Skills with SKILL.md + scripts/ + REFERENCE.md
- [ ] README.md with usage instructions
- [ ] Token efficiency measurements (table with before/after)
- [ ] Cross-agent compatibility matrix (7×2 grid)
- [ ] Development process notes

### Repository 2: EmberLearn
- [ ] 6 AI agent microservices deployed
- [ ] Kafka + PostgreSQL + Kong + Dapr deployed
- [ ] Frontend with Monaco Editor
- [ ] AGENTS.md generated by agents-md-gen Skill
- [ ] Commit history shows agentic workflow
- [ ] Documentation deployed via Docusaurus

### Evaluation Scores
- [ ] Skills Autonomy: ≥12/15 points
- [ ] Token Efficiency: ≥8/10 points
- [ ] Cross-Agent Compatibility: ≥4/5 points
- [ ] Architecture: ≥16/20 points
- [ ] Overall: ≥80/100 points

---

## Next Steps After QuickStart

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Follow task order (dependency-sorted)
3. Test each component before proceeding
4. Document all measurements (tokens, performance, compatibility)
5. Create ADRs for significant architectural decisions
6. Submit to hackathon: https://forms.gle/Mrhf9XZsuXN4rWJf7
