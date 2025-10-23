#!/bin/bash
# Script 05: Start Docker Compose and Setup Ollama Models

set -e

echo "Starting Docker Compose Services..."
echo "====================================="

# Pull latest images
echo "Pulling latest Docker images..."
docker compose pull






# Build custom services
echo "Building custom services..."
docker compose build mcpo

# Start services
echo "Starting all services..."
docker compose up -d

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
        echo "✅ Ollama is ready!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        echo "❌ Ollama failed to start after $max_attempts attempts"
        echo "Check logs: docker logs ollama"
        exit 1
    fi
    
    echo "   Attempt $attempt/$max_attempts - waiting..."
    sleep 2
    ((attempt++))
done

# Check if llama3.2 model already exists
echo "Checking for existing llama3.2 model..."
model_exists=false

# Try to check if model exists (with error handling)
if docker exec ollama ollama list 2>/dev/null | grep -q "llama3.2"; then
    echo "✅ llama3.2 model already exists!"
    model_exists=true
else
    echo "llama3.2 model not found, need to download..."
fi

# Download model if it doesn't exist
if [ "$model_exists" = false ]; then
    echo "Pulling llama3.2 model..."
    echo "   This may take 5-15 minutes depending on your internet connection"
    echo "   Model size: ~2GB"
    echo ""
    
    # Pull the model with timeout (macOS compatible)
    echo "Starting model download (30 minute timeout)..."
    
    # Start the download in background and get its PID
    docker exec ollama ollama pull llama3.2 &
    download_pid=$!
    
    # Wait for the process with timeout
    timeout_seconds=1800  # 30 minutes
    elapsed=0
    
    while kill -0 $download_pid 2>/dev/null; do
        if [ $elapsed -ge $timeout_seconds ]; then
            echo ""
            echo "⏰ Download timeout reached (30 minutes)"
            kill $download_pid 2>/dev/null
            wait $download_pid 2>/dev/null
            download_success=false
            break
        fi
        
        sleep 10
        elapsed=$((elapsed + 10))
        
        # Show progress every 2 minutes
        if [ $((elapsed % 120)) -eq 0 ]; then
            echo "   Still downloading... ($((elapsed / 60)) minutes elapsed)"
        fi
    done
    
    # Check if download completed successfully
    if kill -0 $download_pid 2>/dev/null; then
        # Process still running, we timed out
        download_success=false
    else
        # Process finished, check exit code
        wait $download_pid
        if [ $? -eq 0 ]; then
            download_success=true
        else
            download_success=false
        fi
    fi
    
    if [ "$download_success" = true ]; then
        echo ""
        echo "✅ llama3.2 model downloaded successfully!"
    else
        echo ""
        echo "❌ Failed to download llama3.2 model (timeout or error)"
        echo ""
        echo "Choose an option:"
        echo "  [1] Quit setup (you can restart later)"
        echo "  [2] Continue without model (download manually later)"
        echo ""
        read -p "What would you like to do? [1/2]: " -n 1 -r
        echo ""
        
        case $REPLY in
            1)
                echo "Setup stopped. You can restart with: ./scripts/05-start-docker-compose.sh"
                echo "Or download manually: docker exec ollama ollama pull llama3.2"
                exit 1
                ;;
            2)
                echo "⚠️  Continuing without llama3.2 model"
                echo "To download later, run: docker exec ollama ollama pull llama3.2"
                ;;
            *)
                echo "⚠️  Invalid choice, continuing without model"
                echo "To download later, run: docker exec ollama ollama pull llama3.2"
                ;;
        esac
    fi
fi

# Show available models
echo ""
echo "Available Ollama models:"
docker exec ollama ollama list

# Show service status
echo ""
echo "Service Status:"
echo "=================="
docker compose ps

echo ""
echo "✅ Docker Compose startup complete!"
echo ""
echo "Services available at:"
echo "   - Open WebUI: http://localhost:3000"
echo "   - MCP Bridge: http://localhost:9000"
echo "   - Ollama API: http://localhost:11434"
echo ""
echo "Next: Configure Open WebUI to use the MCP tools"
