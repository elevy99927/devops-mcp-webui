#!/bin/bash
# Script 03: Use Existing Kubernetes Cluster

set -e

echo "Setting up existing Kubernetes cluster connection..."
echo "====================================================="

# Check if kubectl is installed
if ! command -v kubectl >/dev/null 2>&1; then
    echo "❌ kubectl is not installed. Please install kubectl first:"
    echo "   https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

# Check if user has a kubeconfig
if [ ! -f "$HOME/.kube/config" ]; then
    echo "❌ No kubeconfig found at ~/.kube/config"
    echo "   Please ensure you have a valid Kubernetes configuration"
    exit 1
fi

# Test connection to existing cluster
echo "Testing connection to existing cluster..."
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "   Please check your kubeconfig and cluster connectivity"
    exit 1
fi

# Get cluster info
CLUSTER_NAME=$(kubectl config current-context)
echo "✅ Connected to cluster: $CLUSTER_NAME"

# Create kube directory and copy config
echo "Copying kubeconfig to ./kube/config..."
mkdir -p ./kube
cp "$HOME/.kube/config" ./kube/config

# Create a flag file to indicate we're using existing cluster
echo "existing" > ./kube/.cluster-type

# Verify the copied config works
echo "Verifying copied kubeconfig..."
if KUBECONFIG=./kube/config kubectl cluster-info >/dev/null 2>&1; then
    echo "✅ Kubeconfig copied successfully!"
else
    echo "❌ Copied kubeconfig is not working"
    exit 1
fi

# Show cluster information
echo ""
echo "Cluster Information:"
echo "   Context: $(KUBECONFIG=./kube/config kubectl config current-context)"
echo "   Server: $(KUBECONFIG=./kube/config kubectl cluster-info | grep 'Kubernetes control plane' | awk '{print $NF}')"
echo "   Nodes: $(KUBECONFIG=./kube/config kubectl get nodes --no-headers | wc -l | xargs) node(s)"

echo ""
echo "✅ Existing cluster setup complete!"
echo "   Kubeconfig: ./kube/config"
echo "   Cluster type: existing"
echo ""
echo "Note: Script 04 (prepare-mcp-client) will be skipped for existing clusters"