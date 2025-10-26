#!/bin/bash

# Test runner for MCP Server tools
# Provides options to run bash or python version of tests

echo "🧪 MCP Server Tool Test Runner"
echo "=============================="
echo ""
echo "Available test options:"
echo "  1. Bash version (test-mcp-tools.sh)"
echo "  2. Python version (test-mcp-tools.py)"
echo "  3. Both versions"
echo ""

# Check if services are running
echo "🔍 Checking if services are running..."

# Check MCP Bridge
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "✅ MCP Bridge is running (port 9000)"
else
    echo "❌ MCP Bridge is not running (port 9000)"
    echo "   Start with: docker-compose up -d mcpo"
    exit 1
fi

# Check if kubectl works
if kubectl get nodes > /dev/null 2>&1; then
    echo "✅ Kubernetes cluster is accessible"
else
    echo "❌ Kubernetes cluster is not accessible"
    echo "   Check your kubeconfig and cluster status"
    exit 1
fi

echo ""

# Get user choice
if [ "$1" = "bash" ] || [ "$1" = "1" ]; then
    echo "🚀 Running Bash version of tests..."
    ./tests/test-mcp-tools.sh
elif [ "$1" = "python" ] || [ "$1" = "2" ]; then
    echo "🚀 Running Python version of tests..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed"
        echo "   Install Python 3 or use the bash version: ./tests/run-tests.sh bash"
        exit 1
    fi
    
    python3 ./tests/test-mcp-tools.py
elif [ "$1" = "both" ] || [ "$1" = "3" ]; then
    echo "🚀 Running both versions of tests..."
    echo ""
    echo "📋 Running Bash version first..."
    ./tests/test-mcp-tools.sh
    echo ""
    echo "📋 Running Python version..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed, skipping Python tests"
    else
        python3 ./tests/test-mcp-tools.py
    fi
else
    echo "Please specify test version:"
    echo "  ./tests/run-tests.sh bash     # Run bash version"
    echo "  ./tests/run-tests.sh python   # Run python version"
    echo "  ./tests/run-tests.sh both     # Run both versions"
    echo ""
    echo "Or run directly:"
    echo "  ./tests/test-mcp-tools.sh     # Bash version"
    echo "  python3 ./tests/test-mcp-tools.py  # Python version"
fi