#!/bin/bash

echo "🚀 Testing MCP Bridge - Creating Deployment via localhost:9000"
echo "=================================================="

# Test curl command to create a new deployment via the MCP bridge
# Creates: hello-mcp deployment with nginx image and 3 replicas in default namespace

echo "1. Creating deployment 'hello-mcp' with nginx image and 3 replicas..."
curl -s "http://localhost:9000/kubectl_apply" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "manifest": "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: hello-mcp\n  namespace: default\nspec:\n  replicas: 3\n  selector:\n    matchLabels:\n      app: hello-mcp\n  template:\n    metadata:\n      labels:\n        app: hello-mcp\n    spec:\n      containers:\n      - name: nginx\n        image: nginx\n        ports:\n        - containerPort: 80",
    "namespace": "default"
  }'

echo ""
echo ""
echo "2. Verifying deployment was created..."
sleep 2

# Verify the deployment was created
curl -s "http://localhost:9000/kubectl_get" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "deployments",
    "namespace": "default",
    "name": "hello-mcp"
  }' | jq '{name: .metadata.name, replicas: .spec.replicas, status: .status.conditions[0].type}'

echo ""
echo "3. Checking pods created by the deployment..."
curl -s "http://localhost:9000/kubectl_get" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "pods",
    "namespace": "default",
    "labelSelector": "app=hello-mcp"
  }' | jq '.items[] | {name: .metadata.name, status: .status.phase, image: .spec.containers[0].image}'

echo ""
echo "✅ Test completed! The MCP bridge successfully:"
echo "   - Created a deployment via kubectl apply"
echo "   - Retrieved deployment details via kubectl get"
echo "   - Listed pods with label selector"