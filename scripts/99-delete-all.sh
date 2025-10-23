#!/bin/bash
# Script to clean up all Open WebUI Kubernetes Integration lab resources

set -e

echo "Starting cleanup of Open WebUI Kubernetes Integration..."

# Ask about Kind cluster deletion (optional)
echo ""
echo "Kind cluster cleanup:"
if command -v kind >/dev/null 2>&1; then
  # Check if any Kind clusters exist
  existing_clusters=""
  if kind get clusters | grep -q "kind-mcp-lab"; then
    existing_clusters="$existing_clusters kind-mcp-lab"
  fi
  if kind get clusters | grep -q "dev-cluster"; then
    existing_clusters="$existing_clusters dev-cluster"
  fi
  
  if [ -n "$existing_clusters" ]; then
    echo "   Found Kind clusters:$existing_clusters"
    echo "   ⚠️  Warning: This will permanently delete your Kubernetes cluster(s)"
    echo ""
    read -p "Do you want to delete Kind cluster(s)? [y/N]: " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo "Deleting Kind clusters..."
      
      if kind get clusters | grep -q "kind-mcp-lab"; then
        kind delete cluster --name kind-mcp-lab
        echo "✅ Deleted Kind cluster: kind-mcp-lab"
      fi
      
      if kind get clusters | grep -q "dev-cluster"; then
        kind delete cluster --name dev-cluster
        echo "✅ Deleted Kind cluster: dev-cluster"
      fi
    else
      echo "Kind clusters preserved"
    fi
  else
    echo "No Kind clusters found"
  fi
else
  echo "Kind not installed, skipping cluster check"
fi

# Stop and remove all Docker Compose services
echo "Stopping Docker Compose services..."
if [ -f docker-compose.yml ]; then
  docker compose down --volumes --remove-orphans
  echo "✅ Docker Compose services stopped"
else
  echo "⚠️  docker-compose.yml not found, skipping compose down"
fi

# Remove specific containers if they exist
echo "Removing containers..."
containers=("open-webui" "mcpo" "k8s-mcp-server-backend" "ollama")
for container in "${containers[@]}"; do
  if docker ps -a --format "table {{.Names}}" | grep -q "^${container}$"; then
    docker rm -f "$container"
    echo "✅ Removed container: $container"
  fi
done

# Remove custom Docker images
echo "Removing custom Docker images..."
if docker images --format "table {{.Repository}}:{{.Tag}}" | grep -q "openwebui-mcpo"; then
  docker rmi openwebui-mcpo 2>/dev/null || echo "⚠️  Could not remove openwebui-mcpo image"
fi

# Remove Docker volumes
echo "Removing Docker volumes..."
volumes=("openwebui_kind-data" "kind-data")
for volume in "${volumes[@]}"; do
  if docker volume ls --format "table {{.Name}}" | grep -q "^${volume}$"; then
    docker volume rm "$volume" 2>/dev/null && echo "✅ Removed volume: $volume" || echo "⚠️  Could not remove volume: $volume"
  fi
done

# Remove Docker network
echo "Removing Docker network..."
if docker network inspect mcp-lab-network >/dev/null 2>&1; then
  docker network rm mcp-lab-network
  echo "✅ Removed network: mcp-lab-network"
fi

# Kind cluster already deleted at the beginning (priority cleanup)

# Clean up configuration files (optional)
echo ""
echo "Configuration files cleanup:"
echo "   This will remove:"
echo "   - ./kube/config"
echo "   - ./open-webui/data (chat history, settings)"
echo "   - ./ollama/models (downloaded AI models)"
echo ""
read -p "Do you want to delete configuration files and data? [y/N]: " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "Cleaning up configuration files..."
  files_to_remove=(
    "./kube/config"
    "./open-webui/data"
    "./ollama/models"
  )

  for file in "${files_to_remove[@]}"; do
    if [ -e "$file" ]; then
      rm -rf "$file"
      echo "✅ Removed: $file"
    fi
  done
  echo "✅ Configuration files cleaned up"
else
  echo "Configuration files preserved"
fi

# Clean up any dangling Docker resources
echo "Cleaning up dangling Docker resources..."
docker system prune -f --volumes >/dev/null 2>&1 && echo "✅ Docker system pruned" || echo "⚠️  Docker system prune failed"

# Final status check
echo ""
echo "Cleanup complete!"
echo ""
echo "Final status:"
echo "   - Docker containers: $(docker ps -a --format "table {{.Names}}" | wc -l | xargs) remaining"
echo "   - Docker volumes: $(docker volume ls --format "table {{.Name}}" | wc -l | xargs) remaining"
echo "   - Docker networks: $(docker network ls --format "table {{.Name}}" | wc -l | xargs) remaining"
echo ""
echo "To start fresh, run: sh start.sh"
