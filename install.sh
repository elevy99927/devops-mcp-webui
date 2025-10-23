#!/bin/bash
# Open WebUI Kubernetes Integration - Startup Script
# This script runs all setup scripts in sequence (01-07)

set -e

echo "Starting Open WebUI Kubernetes Integration Setup..."
echo "=================================================="

# Define the scripts directory
SCRIPTS_DIR="./scripts"

# List of scripts to run in order (04 may be skipped for existing clusters)
SCRIPTS=(
  "01-create-docker-network.sh"
  "02-create-kind-cluster.sh"
  "05-start-docker-compose.sh"
  "06-attach-network.sh"
  "07-rebuild-mcpo.sh"
)

# Function to run a script with error handling
run_script() {
  local script_name="$1"
  local script_path="$SCRIPTS_DIR/$script_name"
  
  if [ -f "$script_path" ]; then
    echo ""
    echo "Running: $script_name"
    echo "----------------------------------------"
    
    # Make script executable
    chmod +x "$script_path"
    
    # Run the script
    if bash "$script_path"; then
      echo "✅ Completed: $script_name"
    else
      echo "❌ Failed: $script_name"
      echo "🛑 Setup stopped due to error in $script_name"
      exit 1
    fi
  else
    echo "⚠️  Script not found: $script_path"
    echo "Setup stopped due to missing script"
    exit 1
  fi
}

# Run scripts in sequence with conditional logic
for script in "${SCRIPTS[@]}"; do
  # Special handling for script 02 (cluster setup)
  if [ "$script" = "02-create-kind-cluster.sh" ]; then
    run_script "$script"
    
    # Check if we should run script 04 based on cluster type
    if [ -f "./kube/.cluster-type" ]; then
      CLUSTER_TYPE=$(cat ./kube/.cluster-type)
      if [ "$CLUSTER_TYPE" = "kind" ]; then
        echo ""
        echo "Running: 04-prepare-mcp-client.sh (Kind cluster detected)"
        echo "----------------------------------------"
        run_script "04-prepare-mcp-client.sh"
      else
        echo ""
        echo "Skipping: 04-prepare-mcp-client.sh (existing cluster detected)"
      fi
    fi
  else
    run_script "$script"
  fi
done

echo ""
echo "Setup Complete!"
echo "=================="
echo ""
echo "Services Status:"
echo "   - Open WebUI: http://localhost:3000"
echo "   - MCP Bridge: http://localhost:9000"
echo "   - Ollama: http://localhost:11434"
echo ""
echo "Next Steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Create an admin account"
echo "   3. Go to Settings → Admin Panel → Tools"
echo "   4. Add tool server: http://mcpo:9000"
echo "   5. Start asking Kubernetes questions!"
echo ""
echo "Example queries:"
echo "   - 'What pods are running in kube-system?'"
echo "   - 'Show me all services in default namespace'"
echo "   - 'List all deployments'"
echo ""
echo "To clean up everything: ./scripts/99-delete-all.sh"

