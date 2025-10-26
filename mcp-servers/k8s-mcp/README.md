# 🚀 **MCP Server for Kubernetes Operations**

A FastMCP-based server that provides Kubernetes management capabilities through the Model Context Protocol (MCP). This server executes kubectl, helm, and other Kubernetes commands in a secure, containerized environment.

## 🛠️ **All Supported Methods Listed:**

### **kubectl Operations (8 tools):**
- `kubectl_get` - List/get resources with all parameters
- `kubectl_describe` - Detailed resource information
- `kubectl_apply` - Apply YAML manifests
- `kubectl_delete` - Delete resources
- `kubectl_logs` - Retrieve pod/deployment logs
- `kubectl_scale` - Scale deployments/statefulsets
- `exec_pod` - Execute commands in pods
- `port_forward` - Forward ports to pods/services

### **Helm Operations (3 tools):**
- `helm_install` - Install Helm charts
- `helm_upgrade` - Upgrade Helm releases
- `helm_uninstall` - Uninstall Helm releases

## 📋 **Table of Contents**

- [Overview](#overview)
- [Supported Tools](#supported-tools)
  - [kubectl Operations](#kubectl-operations)
  - [Helm Operations](#helm-operations)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Development](#development)

---

## 🎯 **Overview**

The MCP Server implements the Model Context Protocol specification and provides the following capabilities:

- **Async Command Execution** - Non-blocking Kubernetes operations
- **Proper MCP Compliance** - Full JSON-RPC 2.0 and MCP protocol support
- **Tool Schema Definitions** - Self-describing tools with parameter validation
- **Secure Execution** - Containerized environment with proper permissions
- **Kubeconfig Management** - Automatic configuration for Kind clusters

---

## 🛠️ **Supported Tools**

### **kubectl Operations**

#### **1. `kubectl_get`**
List or get Kubernetes resources (pods, services, deployments, etc.)

**Parameters:**
- `resourceType` (required): Resource type (pods, services, deployments, etc.)
- `name` (optional): Specific resource name
- `namespace` (default: "default"): Target namespace
- `output` (default: "json"): Output format (json, yaml, wide)
- `allNamespaces` (default: false): List across all namespaces
- `labelSelector` (optional): Filter by labels
- `fieldSelector` (optional): Filter by fields

**Example:**
```json
{
  "resourceType": "pods",
  "namespace": "kube-system",
  "labelSelector": "app=nginx"
}
```

#### **2. `kubectl_describe`**
Get detailed information about Kubernetes resources

**Parameters:**
- `resourceType` (required): Resource type
- `name` (required): Resource name
- `namespace` (default: "default"): Target namespace

**Example:**
```json
{
  "resourceType": "deployment",
  "name": "nginx-deployment",
  "namespace": "production"
}
```

#### **3. `kubectl_apply`**
Apply YAML manifests to create or update resources

**Parameters:**
- `manifest` (required): YAML manifest content
- `namespace` (default: "default"): Target namespace
- `dryRun` (default: false): Perform dry run

**Example:**
```json
{
  "manifest": "apiVersion: v1\nkind: Pod\nmetadata:\n  name: test-pod\nspec:\n  containers:\n  - name: nginx\n    image: nginx",
  "namespace": "default"
}
```

#### **4. `kubectl_delete`**
Delete Kubernetes resources

**Parameters:**
- `resourceType` (required): Resource type
- `name` (required): Resource name
- `namespace` (default: "default"): Target namespace
- `force` (default: false): Force deletion

**Example:**
```json
{
  "resourceType": "pod",
  "name": "test-pod",
  "namespace": "default",
  "force": true
}
```

#### **5. `kubectl_logs`**
Retrieve logs from pods or deployments

**Parameters:**
- `name` (required): Resource name
- `namespace` (default: "default"): Target namespace
- `resourceType` (default: "pod"): Resource type (pod, deployment)
- `container` (optional): Container name
- `tail` (optional): Number of lines to show
- `follow` (default: false): Follow log output

**Example:**
```json
{
  "name": "nginx-pod",
  "namespace": "default",
  "container": "nginx",
  "tail": 100
}
```

#### **6. `kubectl_scale`**
Scale deployments, statefulsets, or replicasets

**Parameters:**
- `name` (required): Resource name
- `replicas` (required): Number of replicas
- `namespace` (default: "default"): Target namespace
- `resourceType` (default: "deployment"): Resource type

**Example:**
```json
{
  "name": "nginx-deployment",
  "replicas": 5,
  "namespace": "production",
  "resourceType": "deployment"
}
```

#### **7. `exec_pod`**
Execute a command inside a pod container

**Parameters:**
- `name` (required): Pod name
- `command` (required): Command to execute
- `namespace` (default: "default"): Target namespace
- `container` (optional): Container name

**Example:**
```json
{
  "name": "nginx-pod",
  "command": "ls -la /var/log",
  "namespace": "default",
  "container": "nginx"
}
```

#### **8. `port_forward`**
Forward a local port to a pod or service

**Parameters:**
- `resourceType` (required): Resource type (pod/service)
- `resourceName` (required): Resource name
- `localPort` (required): Local port
- `targetPort` (required): Target port
- `namespace` (default: "default"): Target namespace

**Example:**
```json
{
  "resourceType": "service",
  "resourceName": "nginx-service",
  "localPort": 8080,
  "targetPort": 80,
  "namespace": "default"
}
```

---

### **Helm Operations**

#### **9. `helm_install`**
Install a Helm chart

**Parameters:**
- `name` (required): Release name
- `chart` (required): Chart name
- `namespace` (default: "default"): Target namespace
- `repo` (optional): Helm repository URL
- `values` (optional): Chart values as object

**Example:**
```json
{
  "name": "my-nginx",
  "chart": "nginx",
  "namespace": "web",
  "repo": "https://charts.bitnami.com/bitnami",
  "values": {
    "replicaCount": 3,
    "service": {
      "type": "LoadBalancer"
    }
  }
}
```

#### **10. `helm_upgrade`**
Upgrade an existing Helm release

**Parameters:**
- `name` (required): Release name
- `chart` (required): Chart name
- `namespace` (default: "default"): Target namespace
- `repo` (optional): Helm repository URL
- `values` (optional): Chart values as object

**Example:**
```json
{
  "name": "my-nginx",
  "chart": "nginx",
  "namespace": "web",
  "values": {
    "replicaCount": 5
  }
}
```

#### **11. `helm_uninstall`**
Uninstall a Helm release

**Parameters:**
- `name` (required): Release name
- `namespace` (default: "default"): Target namespace

**Example:**
```json
{
  "name": "my-nginx",
  "namespace": "web"
}
```

---

## 🚀 **Installation**

### **Docker Compose (Recommended)**

```yaml
services:
  mcp-server:
    build: ./mcp-server
    ports:
      - "8080:8080"
    volumes:
      - ./kube:/root/.kube:ro
    environment:
      - KUBECONFIG=/root/.kube/config
```

### **Manual Build**

```bash
# Build the container
docker build -t mcp-server .

# Run the container
docker run -p 8080:8080 \
  -v $(pwd)/kube:/root/.kube:ro \
  -e KUBECONFIG=/root/.kube/config \
  mcp-server
```

---

## ⚙️ **Configuration**

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `KUBECONFIG` | `/root/.kube/config` | Path to kubeconfig file |
| `MCP_PORT` | `8080` | MCP server port |
| `LOG_LEVEL` | `INFO` | Logging level |

### **Volume Mounts**

- **Kubeconfig**: Mount your kubeconfig at `/root/.kube/config`
- **Certificates**: Additional certificates if needed

### **Network Requirements**

- **Port 8080**: MCP server endpoint
- **Kubernetes API**: Access to your cluster's API server
- **Helm repositories**: Internet access for chart downloads

---

## 📚 **Usage Examples**

### **MCP Client Connection**

```python
import requests

# Connect to MCP server
response = requests.get("http://localhost:8080/sse")
# Handle SSE connection and MCP protocol
```

### **Tool Call Example**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "kubectl_get",
    "arguments": {
      "resourceType": "pods",
      "namespace": "kube-system"
    }
  },
  "id": 1
}
```

### **Common Operations**

```bash
# List all pods in kube-system
kubectl_get(resourceType="pods", namespace="kube-system")

# Scale a deployment
kubectl_scale(name="nginx", replicas=5, namespace="production")

# Install Jenkins with Helm
helm_install(
  name="jenkins",
  chart="jenkins",
  namespace="ci-cd",
  repo="https://charts.jenkins.io"
)
```

---

## 📖 **API Reference**

### **MCP Protocol Endpoints**

- **`GET /sse`** - Server-Sent Events endpoint for MCP connection
- **`POST /session/{id}`** - MCP session endpoint for tool calls

### **Tool Discovery**

```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 1
}
```

### **Tool Schemas**

Each tool provides a complete JSON schema for parameter validation:

```json
{
  "name": "kubectl_get",
  "description": "List or get Kubernetes resources",
  "inputSchema": {
    "type": "object",
    "properties": {
      "resourceType": {
        "type": "string",
        "description": "Resource type (pods, services, etc.)"
      }
    },
    "required": ["resourceType"]
  }
}
```

---

## 🔧 **Development**

### **Adding New Tools**

1. **Define the tool function**:
```python
@mcp.tool()
async def my_new_tool(param1: str, param2: int = 10) -> List[TextContent]:
    """Tool description"""
    # Implementation
    result = await execute_command(["kubectl", "my-command"])
    return [TextContent(type="text", text=json.dumps(result))]
```

2. **Tool auto-discovery** - The MCP framework automatically registers the tool

3. **Parameter validation** - Type hints provide automatic schema generation

### **Testing**

```bash
# Run tests
python -m pytest tests/

# Test specific tool
python -c "
import asyncio
from server import kubectl_get
result = asyncio.run(kubectl_get('pods', namespace='default'))
print(result)
"
```

### **Debugging**

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run server
python server.py
```

---

## 🏗️ **Architecture**

```
MCP Client → SSE Connection → FastMCP Server → Tool Functions → kubectl/helm → Kubernetes
```

### **Components**

- **FastMCP Framework** - MCP protocol implementation
- **Tool Functions** - Async command wrappers
- **Command Executor** - Secure subprocess execution
- **Kubeconfig Manager** - Configuration handling

---

## 🔒 **Security**

- **Containerized execution** - Isolated environment
- **Read-only kubeconfig** - Mounted as read-only volume
- **Command validation** - Parameter validation and sanitization
- **Timeout protection** - Commands have execution timeouts
- **Non-root user** - Container runs as non-root when possible

---

## 📊 **Monitoring**

### **Health Checks**

```bash
# Check server health
curl http://localhost:8080/health

# List available tools
curl -X POST http://localhost:8080/session/tools/list
```

### **Logging**

- **Structured logging** - JSON format for easy parsing
- **Command tracing** - All executed commands are logged
- **Error tracking** - Detailed error information

---

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create a feature branch**
3. **Add your tool function**
4. **Write tests**
5. **Submit a pull request**

---

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 **Support**

- **Issues**: Report bugs and feature requests
- **Documentation**: Comprehensive guides and examples
- **Community**: Join our discussions

**The MCP Server provides a robust, standards-compliant foundation for Kubernetes management through the Model Context Protocol.**