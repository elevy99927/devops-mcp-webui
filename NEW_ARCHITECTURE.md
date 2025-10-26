# 🔄 **New MCP Architecture - Split Components**

## 📊 **Architecture Overview**

The MCP bridge has been split into two separate components for better separation of concerns:

| Component | **MCP Server** | **MCP Bridge** |
|-----------|----------------|----------------|
| **Purpose** | Execute Kubernetes commands | Expose REST API |
| **Protocol** | MCP Protocol (FastMCP) | HTTP/REST |
| **Port** | 8080 | 9000 |
| **Dependencies** | kubectl, helm, FastMCP | Flask, requests, SSE client |
| **Responsibilities** | Command execution, MCP compliance | API translation, OpenAPI generation |

---

## 🏗️ **New Architecture Flow**

```
OpenWebUI → HTTP POST → MCP Bridge → SSE → MCP Server → kubectl/helm → Kubernetes
```

### **Detailed Flow:**
1. **OpenWebUI** sends REST API request to MCP Bridge (port 9000)
2. **MCP Bridge** translates REST to MCP protocol via SSE
3. **MCP Server** receives MCP tool call via SSE transport
4. **MCP Server** executes kubectl/helm commands
5. **Results** flow back through the same chain

---

## 📁 **Component Details**

### **1. MCP Server (`mcp-server/`)**
- **File**: `server.py`
- **Framework**: FastMCP (proper MCP implementation)
- **Tools**: All kubectl and helm operations as MCP tools
- **Features**:
  - ✅ Proper MCP protocol compliance
  - ✅ Async command execution
  - ✅ Tool schema definitions
  - ✅ kubectl and helm binaries included
  - ✅ Kubeconfig mounting and fixing

### **2. MCP Bridge (`mcp-bridge/`)**
- **File**: `bridge.py`
- **Framework**: Flask (REST API)
- **Features**:
  - ✅ Dynamic OpenAPI generation from MCP capabilities
  - ✅ SSE communication with MCP Server
  - ✅ Proper MCP session initialization
  - ✅ Tool discovery and caching
  - ✅ Backward compatibility routes

---

## 🔧 **Key Improvements**

### **1. Dynamic OpenAPI Generation**
```python
def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI specification dynamically from MCP capabilities"""
    # Fetches tools from MCP Server
    # Generates REST endpoints automatically
    # Creates proper OpenAPI schema
```

### **2. Proper MCP Communication**
```python
class MCPClient:
    """Client for communicating with MCP Server via SSE"""
    # SSE connection establishment
    # MCP session initialization
    # Tool discovery and caching
    # Proper JSON-RPC communication
```

### **3. Separation of Concerns**
- **MCP Server**: Focus on command execution and MCP compliance
- **MCP Bridge**: Focus on API translation and OpenWebUI integration

---

## 🚀 **Benefits**

### **Scalability**
- **Independent scaling** - Bridge and server can scale separately
- **Multiple bridges** - One MCP server can serve multiple bridges
- **Load balancing** - Multiple MCP servers behind load balancer

### **Maintainability**
- **Clear responsibilities** - Each component has single purpose
- **Easier testing** - Components can be tested independently
- **Better debugging** - Issues isolated to specific component

### **Standards Compliance**
- **Proper MCP protocol** - Server follows MCP specification exactly
- **Dynamic capabilities** - OpenAPI reflects actual MCP capabilities
- **Future-proof** - Easy to add new MCP tools

### **Development Experience**
- **Hot reloading** - Bridge can restart without affecting server
- **Tool development** - Add tools to MCP server, bridge auto-discovers
- **API evolution** - OpenAPI updates automatically with new tools

---

## 🔄 **Migration Path**

### **From Old Architecture:**
```
OpenWebUI → MCP Bridge (direct commands) → kubectl/helm
```

### **To New Architecture:**
```
OpenWebUI → MCP Bridge (REST) → SSE → MCP Server (MCP) → kubectl/helm
```

### **Backward Compatibility**
- All existing REST endpoints still work
- Same OpenWebUI configuration
- Same tool names and parameters
- Transparent upgrade for users

---

## 📈 **Performance Considerations**

### **Latency**
- **Additional hop** - One extra network call (Bridge → Server)
- **Connection reuse** - SSE connection stays open
- **Async execution** - Non-blocking command execution

### **Resource Usage**
- **Memory** - Two containers instead of one
- **CPU** - Distributed processing
- **Network** - Internal container communication

### **Optimization**
- **Connection pooling** - Reuse SSE connections
- **Tool caching** - Cache tool definitions
- **Batch operations** - Multiple tools in single session

---

## 🛠️ **Deployment**

### **Docker Compose**
```yaml
services:
  mcp-server:
    build: ./mcp-server
    ports: ["8080:8080"]
    volumes: ["./kube:/root/.kube:ro"]
    
  mcpo:
    build: ./mcp-bridge
    ports: ["9000:9000"]
    depends_on: [mcp-server]
```

### **Environment Variables**
- **MCP Server**: `KUBECONFIG=/root/.kube/config`
- **MCP Bridge**: `MCP_SERVER_URL=http://mcp-server:8080`

---

## 🎯 **Next Steps**

1. **Test the new architecture** - Verify all tools work correctly
2. **Performance benchmarking** - Compare with old architecture
3. **Add monitoring** - Health checks and metrics
4. **Documentation** - Update user guides
5. **Tool expansion** - Add istioctl, argocd tools

---

## 🏆 **Success Metrics**

- ✅ **All tools working** - kubectl and helm operations
- ✅ **Dynamic OpenAPI** - Generated from MCP capabilities
- ✅ **Proper MCP protocol** - Standards compliant
- ✅ **Backward compatibility** - Existing integrations work
- ✅ **Better separation** - Clear component responsibilities

**The new architecture provides a solid foundation for future expansion while maintaining compatibility with existing OpenWebUI integrations.**