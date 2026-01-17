# Cross-Agent Compatibility Test Plan

## Overview

This document outlines the test plan for verifying that all 7 Skills work identically on both Claude Code and Goose AI coding agents.

## Test Environment

### Claude Code
- Version: Latest
- Skills Location: `.claude/skills/`
- Invocation: Natural language prompts

### Goose
- Version: Latest
- Skills Location: `.claude/skills/` (reads AAIF format)
- Invocation: Natural language prompts

## Test Scenarios

### 1. agents-md-gen Skill

**Test Prompt**: "Generate an AGENTS.md file for this repository"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/analyze_repo.py` to scan codebase
3. Runs `scripts/generate_agents_md.py` to create AGENTS.md
4. Runs `scripts/validate.sh` to verify output

**Success Criteria**:
- [ ] AGENTS.md file created at repository root
- [ ] Contains Overview, Project Structure, Coding Conventions sections
- [ ] Detects Python and TypeScript as primary languages
- [ ] Lists all 7 Skills in the structure

### 2. kafka-k8s-setup Skill

**Test Prompt**: "Deploy Kafka to Kubernetes using the kafka-k8s-setup skill"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/check_prereqs.sh` to verify kubectl, helm, cluster access
3. Runs `scripts/deploy_kafka.sh` to deploy via Helm
4. Runs `scripts/create_topics.py` to create EmberLearn topics
5. Runs `scripts/verify_kafka.py` to confirm deployment

**Success Criteria**:
- [ ] Kafka pods running in `kafka` namespace
- [ ] 8 EmberLearn topics created
- [ ] Verification script passes all checks

### 3. postgres-k8s-setup Skill

**Test Prompt**: "Deploy PostgreSQL with migrations using the postgres-k8s-setup skill"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/check_prereqs.sh` to verify prerequisites
3. Runs `scripts/deploy_postgres.sh` to deploy via Helm
4. Runs `scripts/run_migrations.py` to apply Alembic migrations
5. Runs `scripts/verify_schema.py` to confirm schema

**Success Criteria**:
- [ ] PostgreSQL pod running in `default` namespace
- [ ] All 10 tables created (users, topics, progress, etc.)
- [ ] Mastery calculation trigger installed

### 4. fastapi-dapr-agent Skill

**Test Prompt**: "Scaffold a concepts agent using the fastapi-dapr-agent skill"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/scaffold_agent.py concepts` to generate service
3. Runs `scripts/generate_k8s_manifests.py` for Kubernetes configs
4. Runs `scripts/verify_structure.py` to validate output

**Success Criteria**:
- [ ] `backend/concepts_agent/` directory created
- [ ] Contains main.py, Dockerfile, requirements.txt
- [ ] K8s manifests generated in `k8s/agents/concepts_agent/`
- [ ] Structure validation passes

### 5. mcp-code-execution Skill

**Test Prompt**: "Create a new skill called 'test-skill' using the mcp-code-execution skill"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/wrap_mcp_server.py test-skill` to create skill structure
3. Runs `scripts/validate_structure.py` to verify AAIF compliance

**Success Criteria**:
- [ ] `.claude/skills/test-skill/` directory created
- [ ] Contains SKILL.md with AAIF frontmatter
- [ ] Contains scripts/ directory with templates
- [ ] Contains REFERENCE.md

### 6. nextjs-k8s-deploy Skill

**Test Prompt**: "Scaffold a Next.js frontend with Monaco Editor using the nextjs-k8s-deploy skill"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/scaffold_nextjs.sh` to create project structure
3. Runs `scripts/integrate_monaco.py` to add Monaco components
4. Runs `scripts/generate_k8s_deploy.py` for Kubernetes configs

**Success Criteria**:
- [ ] `frontend/` directory with Next.js structure
- [ ] Monaco Editor component with SSR disabled
- [ ] K8s deployment manifests generated
- [ ] package.json includes @monaco-editor/react

### 7. docusaurus-deploy Skill

**Test Prompt**: "Generate documentation site using the docusaurus-deploy skill"

**Expected Behavior**:
1. Agent reads SKILL.md instructions
2. Runs `scripts/scan_codebase.py` to find documentation sources
3. Runs `scripts/generate_docusaurus_config.py` to create config
4. Runs `scripts/generate_docs.py` to create documentation pages

**Success Criteria**:
- [ ] `docs-site/` directory created
- [ ] docusaurus.config.js generated
- [ ] Skills documentation pages generated
- [ ] sidebars.js configured

## Test Matrix

| Skill | Claude Code | Goose | Notes |
|-------|-------------|-------|-------|
| agents-md-gen | ⬜ | ⬜ | |
| kafka-k8s-setup | ⬜ | ⬜ | Requires K8s cluster |
| postgres-k8s-setup | ⬜ | ⬜ | Requires K8s cluster |
| fastapi-dapr-agent | ⬜ | ⬜ | |
| mcp-code-execution | ⬜ | ⬜ | |
| nextjs-k8s-deploy | ⬜ | ⬜ | |
| docusaurus-deploy | ⬜ | ⬜ | |

Legend: ⬜ Not tested | ✅ Passed | ❌ Failed | ⚠️ Partial

## Test Execution Process

1. **Prepare Environment**
   - Ensure Minikube is running (for K8s skills)
   - Ensure Dapr is installed
   - Clean any previous test artifacts

2. **Execute on Claude Code**
   - Open Claude Code in project directory
   - Issue test prompt
   - Document execution steps
   - Record output and any errors
   - Verify success criteria

3. **Execute on Goose**
   - Open Goose in project directory
   - Issue identical test prompt
   - Document execution steps
   - Record output and any errors
   - Verify success criteria

4. **Compare Results**
   - Compare execution steps between agents
   - Compare final outputs
   - Note any differences in behavior
   - Document compatibility issues

## Compatibility Requirements

Per AAIF standard, Skills must:
1. Use YAML frontmatter with `name`, `description` fields
2. Use universal tools (Bash, Python) not proprietary APIs
3. Return structured, parseable output
4. Be idempotent (safe to re-run)

## Known Considerations

### Claude Code
- Native support for `.claude/skills/` directory
- Automatic skill discovery via semantic matching
- Full AAIF format support

### Goose
- Reads skills from `.claude/skills/` directory
- May require explicit skill invocation
- AAIF format compatible

## Test Schedule

| Phase | Skills | Duration |
|-------|--------|----------|
| 1 | agents-md-gen, mcp-code-execution | Day 1 |
| 2 | fastapi-dapr-agent, nextjs-k8s-deploy | Day 1 |
| 3 | docusaurus-deploy | Day 1 |
| 4 | kafka-k8s-setup, postgres-k8s-setup | Day 2 (requires K8s) |

## Reporting

Results will be documented in:
- `testing/claude-code-results.md` - Claude Code test results
- `testing/goose-results.md` - Goose test results
- `testing/compatibility-analysis.md` - Comparison and analysis
- `.claude/skills/README.md` - Updated compatibility matrix
