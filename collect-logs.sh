#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p ./logs

# Function to collect logs for a container
collect_logs() {
    local container_name=$1
    local log_file="./logs/${container_name}.log"
    
    echo "Collecting logs for $container_name..."
    docker logs $container_name > $log_file 2>&1
}

# Collect logs from all containers
collect_logs "ollama"
collect_logs "open-webui"
collect_logs "k8s-mcp-server-backend"
collect_logs "mcpo"

echo "Logs collected in ./logs/ directory"