#!/bin/bash

# Simple curl command to install Jenkins via Helm through MCP bridge
echo "Installing Jenkins via Helm..."

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
          }
        }
      },
      "persistence": {
        "enabled": false
      }
    }
  }'