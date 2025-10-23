#!/bin/bash
# Script 02: Create Kind Cluster or Use Existing Kubernetes Cluster

set -e

echo "Kubernetes Cluster Setup"
echo "============================"
echo ""
echo "Choose your Kubernetes setup:"
echo "  [Y] Use temporary Kind cluster (default)"
echo "  [N] Use existing Kubernetes cluster"
echo ""
read -p "Do you want to use a temporary Kind cluster? [Y/n]: " -n 1 -r
echo ""

# Default to Yes if user just presses Enter
if [[ -z "$REPLY" ]] || [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "✅ Creating temporary Kind cluster..."
    
    # Check if Kind is installed
    if ! command -v kind >/dev/null 2>&1; then
        echo "❌ Kind is not installed. Please install Kind first:"
        echo "   https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
        exit 1
    fi
    
    # Delete existing cluster if it exists
    if kind get clusters | grep -q "kind-mcp-lab"; then
        echo "Removing existing Kind cluster..."
        kind delete cluster --name kind-mcp-lab
    fi
    
    # Create new Kind cluster
    echo "Creating Kind cluster 'kind-mcp-lab'..."
    kind create cluster --name kind-mcp-lab
    
    # Connect to Docker networks
    echo "Connecting Kind cluster to Docker networks..."
    docker network connect mcp-lab-network kind-mcp-lab-control-plane 2>/dev/null || echo "⚠️  Network mcp-lab-network connection failed (may already exist)"
    docker network connect openwebui_mcp-lab-network kind-mcp-lab-control-plane 2>/dev/null || echo "⚠️  Network openwebui_mcp-lab-network connection failed (may not exist)"
    
    # Export kubeconfig for Kind cluster
    echo "Setting up kubeconfig..."
    mkdir -p ./kube
    kind export kubeconfig --name kind-mcp-lab --kubeconfig ./kube/config
    
    echo "✅ Kind cluster created successfully!"
    echo "   Cluster name: kind-mcp-lab"
    echo "   Kubeconfig: ./kube/config"
    
    # Create a flag file to indicate we're using Kind
    echo "kind" > ./kube/.cluster-type
    
else
    echo "✅ Using existing Kubernetes cluster..."
    
    # Run script 03 to handle existing cluster setup
    if [ -f "./scripts/03-use-existing-k8s.sh" ]; then
        echo "Running existing cluster setup..."
        chmod +x "./scripts/03-use-existing-k8s.sh"
        bash "./scripts/03-use-existing-k8s.sh"
    else
        echo "❌ Script 03-use-existing-k8s.sh not found!"
        exit 1
    fi
fi

echo ""
echo "Next: Script 04 will prepare the MCP client..."
