#!/bin/bash

# Standalone KIND cluster setup script
# This runs KIND on your host machine instead of in Docker Compose

CLUSTER_NAME="dev-cluster"
KUBECONFIG_PATH="./kubeconfig/config"

echo "Setting up KIND cluster: $CLUSTER_NAME"

# Check if KIND is installed
if ! command -v kind &> /dev/null; then
    echo "KIND not found. Installing..."
    # For macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install kind
        else
            curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-darwin-amd64
            chmod +x ./kind
            sudo mv ./kind /usr/local/bin/kind
        fi
    # For Linux
    else
        curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
        chmod +x ./kind
        sudo mv ./kind /usr/local/bin/kind
    fi
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "kubectl not found. Installing..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install kubectl
        else
            curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/darwin/amd64/kubectl"
            chmod +x ./kubectl
            sudo mv ./kubectl /usr/local/bin/kubectl
        fi
    else
        curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
        chmod +x ./kubectl
        sudo mv ./kubectl /usr/local/bin/kubectl
    fi
fi

# Create kubeconfig directory
mkdir -p ./kubeconfig

# Delete existing cluster if it exists
if kind get clusters | grep -q "^$CLUSTER_NAME$"; then
    echo "Deleting existing cluster: $CLUSTER_NAME"
    kind delete cluster --name $CLUSTER_NAME
fi

# Create the cluster
echo "Creating KIND cluster..."
kind create cluster --name $CLUSTER_NAME --config ./kind-config/kind-config.yaml --kubeconfig $KUBECONFIG_PATH

if [ $? -eq 0 ]; then
    echo "✅ KIND cluster created successfully!"
    echo ""
    echo "To use this cluster:"
    echo "export KUBECONFIG=$(pwd)/$KUBECONFIG_PATH"
    echo ""
    echo "Or copy to your default kubeconfig:"
    echo "cp $KUBECONFIG_PATH ~/.kube/config"
    echo ""
    echo "Test the connection:"
    echo "kubectl --kubeconfig $KUBECONFIG_PATH get nodes"
    echo ""
    echo "The cluster is accessible at: https://localhost:6443"
else
    echo "❌ Failed to create KIND cluster"
    exit 1
fi