#!/bin/bash

echo "🚀 Testing MCP Bridge - Installing Jenkins via Helm"
echo "=================================================="

# Test helm install command to install Jenkins via the MCP bridge
# Creates: Jenkins installation using official Jenkins Helm chart

echo "1. Installing Jenkins using Helm chart..."
curl -s "http://localhost:9000/helm_install" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "name": "jenkins",
    "chart": "jenkins",
    "namespace": "jenkins",
    "repo": "https://charts.jenkins.io",
    "values": {
      "controller": {
        "serviceType": "NodePort",
        "nodePort": 32000,
        "adminPassword": "admin123",
        "resources": {
          "requests": {
            "cpu": "50m",
            "memory": "256Mi"
          },
          "limits": {
            "cpu": "2000m",
            "memory": "4096Mi"
          }
        }
      },
      "agent": {
        "enabled": false
      },
      "persistence": {
        "enabled": false
      }
    }
  }'

echo ""
echo ""
echo "2. Waiting for Jenkins to be deployed..."
sleep 10

echo "3. Checking Jenkins deployment status..."
curl -s "http://localhost:9000/kubectl_get" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "deployments",
    "namespace": "jenkins",
    "name": "jenkins"
  }' | jq '{name: .metadata.name, replicas: .spec.replicas, ready: .status.readyReplicas}'

echo ""
echo "4. Checking Jenkins pods..."
curl -s "http://localhost:9000/kubectl_get" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "pods",
    "namespace": "jenkins",
    "labelSelector": "app.kubernetes.io/name=jenkins"
  }' | jq '.items[] | {name: .metadata.name, status: .status.phase, ready: .status.conditions[]? | select(.type=="Ready") | .status}'

echo ""
echo "5. Checking Jenkins service..."
curl -s "http://localhost:9000/kubectl_get" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "services",
    "namespace": "jenkins",
    "name": "jenkins"
  }' | jq '{name: .metadata.name, type: .spec.type, ports: .spec.ports[]? | {port: .port, nodePort: .nodePort}}'

echo ""
echo "6. Getting Jenkins admin password..."
curl -s "http://localhost:9000/kubectl_get" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "secrets",
    "namespace": "jenkins",
    "name": "jenkins"
  }' | jq -r '.data."jenkins-admin-password"' | base64 -d

echo ""
echo ""
echo "✅ Jenkins Helm installation test completed!"
echo "📋 Summary:"
echo "   - Jenkins installed via Helm chart from https://charts.jenkins.io"
echo "   - Namespace: jenkins"
echo "   - Service Type: NodePort (port 32000)"
echo "   - Admin Password: admin123 (or check secret above)"
echo "   - Access: http://localhost:32000 (if using kind port-forward)"