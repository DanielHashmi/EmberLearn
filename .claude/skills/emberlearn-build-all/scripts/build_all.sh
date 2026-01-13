#!/bin/bash
set -euo pipefail

# EmberLearn Build All - Master orchestrator script
# Goal: single prompt -> regenerate current EmberLearn project into a fresh output directory

SKILLS_DIR=".claude/skills"
ROOT_DIR="$(pwd)"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# -----------------------
# Python launcher
# -----------------------
PYTHON_CMD=""
PYTHON_ARGS=()

try_python() {
  local cmd="$1"; shift
  if ! command -v "$cmd" >/dev/null 2>&1; then
    return 1
  fi
  # Some Windows environments have a Microsoft Store alias `python` that prints a message.
  # We only accept interpreters that can successfully execute a trivial script.
  # shellcheck disable=SC2068
  "$cmd" $@ -c "print('ok')" >/dev/null 2>&1
}

if try_python python3; then
  PYTHON_CMD="python3"
elif try_python python; then
  PYTHON_CMD="python"
elif try_python py -3; then
  PYTHON_CMD="py"
  PYTHON_ARGS=("-3")
else
  echo "✗ Python not found (need python3, python, or py -3 on PATH)" >&2
  exit 127
fi

pyexec() {
  "$PYTHON_CMD" "${PYTHON_ARGS[@]}" "$@"
}

# -----------------------
# Config (env override)
# -----------------------
OUTPUT_DIR="${OUTPUT_DIR:-"./_regen/emberlearn-$(date +%Y%m%d-%H%M%S)"}"
SPEC_DIR="${SPEC_DIR:-"specs/002-hackathon-iii-updated"}"
MODE="${MODE:-both}"              # local|k8s|both
DEPLOY_K8S="${DEPLOY_K8S:-0}"      # 0|1
REGENERATE="${REGENERATE:-0}"      # 0|1 (0 = copy current working project for functional exactness)

AGENTS=("triage" "concepts" "code_review" "debug" "exercise" "progress")

# kubectl selection (WSL/Windows compatibility)
if command -v minikube.exe &> /dev/null; then
  KUBECTL="minikube.exe kubectl --"
else
  KUBECTL="kubectl"
fi

echo "Using Python: ${PYTHON_CMD} ${PYTHON_ARGS[*]:-}"
echo "=========================================="
echo "EmberLearn Build All - Regenerate Project"
echo "=========================================="
echo ""
echo "Config:"
echo "  OUTPUT_DIR=${OUTPUT_DIR}"
echo "  SPEC_DIR=${SPEC_DIR}"
echo "  MODE=${MODE}"
echo "  DEPLOY_K8S=${DEPLOY_K8S}"
echo "  REGENERATE=${REGENERATE}"
echo ""

mkdir -p "${OUTPUT_DIR}"

# -----------------------
# Phase 0: Copy project
# -----------------------
echo "Phase 0: Copying current working project..."
echo "------------------------------------------"
pyexec "${SCRIPT_DIR}/copy_project.py" \
  --src "${ROOT_DIR}" \
  --dst "${OUTPUT_DIR}" \
  --mode "${MODE}"
echo "OK Copied project into ${OUTPUT_DIR}"
echo ""

# -----------------------
# Phase 1: Regeneration
# -----------------------
echo "Phase 1: Regenerating entire project from skills..."
echo "------------------------------------------------------"

# 1. Root files
echo "→ Generating root files..."
pyexec "$SKILLS_DIR/emberlearn-root-gen/scripts/generate_root.py"

# 2. Backend Shared
echo "→ Generating backend shared utilities..."
pyexec "$SKILLS_DIR/shared-utils-gen/scripts/generate_shared.py"

# 3. Backend Database Models
echo "→ Generating database models..."
pyexec "$SKILLS_DIR/database-schema-gen/scripts/generate_models.py"

# 4. Backend Core (Monolith)
echo "→ Generating backend core monolith..."
pyexec "$SKILLS_DIR/backend-core-gen/scripts/generate_core.py"

# 5. Microservice Agents
echo "→ Generating agent microservices..."
for agent in "${AGENTS[@]}"; do
  pyexec "$SKILLS_DIR/fastapi-dapr-agent/scripts/generate_complete_agent.py" \
    "$agent" \
    "backend/${agent}_agent"
done

# 6. Frontend
echo "→ Generating Next.js production frontend..."
pyexec "$SKILLS_DIR/nextjs-production-gen/scripts/generate_complete_app.py" \
  --output-dir "frontend"

# 7. K8s Manifests
echo "→ Generating Kubernetes manifests..."
pyexec "$SKILLS_DIR/k8s-manifest-gen/scripts/generate_manifests.py"

echo "OK Project regenerated successfully"
echo ""


# -----------------------
# Phase 2: Verify output
# -----------------------
echo "Phase 2: Verifying regeneration output..."
echo "----------------------------------------"
pyexec "${SCRIPT_DIR}/verify_regeneration.py" "${OUTPUT_DIR}"
echo ""

# -----------------------
# Phase 3: Optional K8s deploy
# -----------------------
if [[ "${DEPLOY_K8S}" == "1" && ( "${MODE}" == "k8s" || "${MODE}" == "both" ) ]]; then
  echo "Phase 3: Deploying to Kubernetes (optional)..."
  echo "---------------------------------------------"

  echo "→ Deploying PostgreSQL..."
  bash "$SKILLS_DIR/postgres-k8s-setup/scripts/check_prereqs.sh"
  bash "$SKILLS_DIR/postgres-k8s-setup/scripts/deploy_postgres.sh"
  pyexec "$SKILLS_DIR/postgres-k8s-setup/scripts/run_migrations.py" || true
  pyexec "$SKILLS_DIR/postgres-k8s-setup/scripts/verify_schema.py"
  echo "OK PostgreSQL deployed"

  echo "→ Deploying Kafka..."
  bash "$SKILLS_DIR/kafka-k8s-setup/scripts/check_prereqs.sh"
  bash "$SKILLS_DIR/kafka-k8s-setup/scripts/deploy_kafka.sh"
  pyexec "$SKILLS_DIR/kafka-k8s-setup/scripts/create_topics.py" || true
  pyexec "$SKILLS_DIR/kafka-k8s-setup/scripts/verify_kafka.py"
  echo "OK Kafka deployed"

  echo "→ Deploying Dapr control plane + components..."
  bash "$SKILLS_DIR/dapr-deploy/scripts/deploy_dapr.sh"
  bash "$SKILLS_DIR/dapr-deploy/scripts/configure_components.sh"
  pyexec "$SKILLS_DIR/dapr-deploy/scripts/verify_dapr.py"
  echo "OK Dapr deployed and configured"

  echo "→ Applying manifests from output dir..."
  $KUBECTL apply -f "${OUTPUT_DIR}/k8s/manifests/secrets.yaml"
  $KUBECTL apply -f "${OUTPUT_DIR}/k8s/manifests/configmap.yaml"
  for agent in "${AGENTS[@]}"; do
    $KUBECTL apply -f "${OUTPUT_DIR}/k8s/manifests/${agent}-agent-deployment.yaml"
    $KUBECTL apply -f "${OUTPUT_DIR}/k8s/manifests/${agent}-agent-service.yaml"
  done
  $KUBECTL apply -f "${OUTPUT_DIR}/k8s/manifests/ingress.yaml"

  echo "→ Waiting for pods to be ready..."
  for agent in "${AGENTS[@]}"; do
    $KUBECTL wait --for=condition=ready pod -l app="${agent}-agent" --timeout=180s 2>/dev/null || echo "  ${agent}-agent: pending..."
  done

  echo "OK K8s deploy attempted"
  echo ""
fi

echo "=========================================="
echo "OK EmberLearn regeneration complete"
echo "=========================================="
echo "Output directory: ${OUTPUT_DIR}"
if [[ "${DEPLOY_K8S}" != "1" ]]; then
  echo "Note: K8s deployment skipped (set DEPLOY_K8S=1 to deploy)."
fi

# Minimal output line for hackathon logs
echo "OK EmberLearn regenerated"
