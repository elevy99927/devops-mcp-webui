#!/bin/bash
# Script to check if Kind cluster and Docker network are up

KIND_CLUSTER_NAME="kind-mcp-lab"
DOCKER_NETWORK_NAME="lab-mcp-network"

# Check Kind cluster
kind get clusters | grep -q "$KIND_CLUSTER_NAME"
if [ $? -eq 0 ]; then
  echo "Kind cluster '$KIND_CLUSTER_NAME' is running."
else
  echo "Kind cluster '$KIND_CLUSTER_NAME' is NOT running."
fi

# Check Docker network
if docker network inspect "$DOCKER_NETWORK_NAME" >/dev/null 2>&1; then
  echo "Docker network '$DOCKER_NETWORK_NAME' exists."
else
  echo "Docker network '$DOCKER_NETWORK_NAME' does NOT exist."
fi
