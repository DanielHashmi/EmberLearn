#!/bin/bash
# Rollback Kafka deployment

set -e

NAMESPACE="${KAFKA_NAMESPACE:-kafka}"
RELEASE_NAME="${KAFKA_RELEASE:-kafka}"

echo "Rolling back Kafka deployment..."
echo "  Namespace: $NAMESPACE"
echo "  Release: $RELEASE_NAME"

# Uninstall Helm release
helm uninstall "$RELEASE_NAME" --namespace "$NAMESPACE" || true

# Delete PVCs (optional - uncomment to delete data)
# kubectl delete pvc -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE

echo ""
echo "✓ Kafka rollback complete!"
echo ""
echo "Note: PVCs were preserved. To delete data, run:"
echo "  kubectl delete pvc -l app.kubernetes.io/instance=$RELEASE_NAME -n $NAMESPACE"
