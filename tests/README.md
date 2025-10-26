# 🧪 **MCP Server Tool Tests**

Comprehensive test suite for validating MCP Server Kubernetes tools functionality.

## 📋 **Test Coverage**

### **Tools Tested:**
1. **`kubectl_apply`** - Create test pod in default namespace
2. **`kubectl_get`** - Get specific pod and list with label selector
3. **`kubectl_describe`** - Describe the test pod
4. **`kubectl_logs`** - Retrieve logs from test pod
5. **`exec_pod`** - Execute commands inside test pod
6. **`kubectl_delete`** - Clean up test pod

### **Test Scenarios:**
- ✅ **Pod Creation** - Apply YAML manifest
- ✅ **Resource Retrieval** - Get pod by name and label selector
- ✅ **Detailed Information** - Describe pod with full details
- ✅ **Log Access** - Retrieve container logs
- ✅ **Command Execution** - Run commands inside containers
- ✅ **Resource Cleanup** - Delete test resources

---

## 🚀 **Quick Start**

### **Prerequisites:**
```bash
# Ensure services are running
docker-compose up -d

# Verify cluster access
kubectl get nodes

# For Python tests (optional - uses built-in modules)
# pip install -r tests/requirements.txt  # Only if you want requests library
```

### **Run Tests:**
```bash
# Interactive test runner
./tests/run-tests.sh

# Or run specific version
./tests/run-tests.sh bash     # Bash version
./tests/run-tests.sh python   # Python version
./tests/run-tests.sh both     # Both versions

# Or run directly
./tests/test-mcp-tools.sh           # Bash version
python3 ./tests/test-mcp-tools.py   # Python version
```

---

## 📁 **Test Files**

| File | Description | Language |
|------|-------------|----------|
| `test-mcp-tools.sh` | Main test script with full validation | Bash |
| `test-mcp-tools.py` | Python version with JSON handling | Python |
| `run-tests.sh` | Test runner with service checks | Bash |
| `README.md` | This documentation | Markdown |

---

## 🔧 **Test Details**

### **Test Pod Specification:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mcp-test-pod
  namespace: default
  labels:
    app: mcp-test
    test: "true"
spec:
  containers:
  - name: nginx
    image: nginx:alpine
    ports:
    - containerPort: 80
    env:
    - name: TEST_ENV
      value: "mcp-server-test"
    command: ["/bin/sh"]
    args: ["-c", "echo 'MCP Test Pod Started' && nginx -g 'daemon off;'"]
  restartPolicy: Never
```

### **Test Flow:**
1. **Create** test pod using `kubectl_apply`
2. **Wait** for pod to start (10 seconds)
3. **Get** pod details using `kubectl_get`
4. **List** pods with label selector
5. **Describe** pod for detailed information
6. **Wait** for pod to be fully running (15 seconds)
7. **Retrieve** logs using `kubectl_logs`
8. **Execute** commands using `exec_pod`
9. **Check** environment variables
10. **Get** pod with wide output format
11. **Delete** test pod using `kubectl_delete`
12. **Verify** cleanup completed

---

## 📊 **Expected Output**

### **Successful Test Run:**
```
🧪 Testing MCP Server Kubernetes Tools
======================================

Test 1: kubectl_apply - Creating test pod
================================================
📡 Calling kubectl_apply...
✅ Pod creation succeeded

⏳ Waiting 10 seconds for pod to start...

Test 2: kubectl_get - Getting test pod
=============================================
📡 Calling kubectl_get...
✅ Get pod succeeded
Pod Status: Running

...

📊 Test Summary
===============
✅ kubectl_apply - Create test pod
✅ kubectl_get - Get specific pod
✅ kubectl_get - List pods with label selector
✅ kubectl_describe - Describe pod
✅ kubectl_logs - Get pod logs
✅ exec_pod - Execute commands in pod
✅ kubectl_delete - Delete test pod

🎉 All MCP Server tool tests completed successfully!
```

---

## 🔍 **Troubleshooting**

### **Common Issues:**

#### **Python Module Missing:**
```bash
ModuleNotFoundError: No module named 'requests'
```
**Solution:** The script has been updated to use built-in modules. If you still see this error, run:
```bash
pip install requests
# OR use the bash version instead:
./tests/test-mcp-tools.sh
```

#### **Service Not Running:**
```bash
❌ MCP Bridge is not running (port 9000)
   Start with: docker-compose up -d mcpo
```
**Solution:** Start the services with `docker-compose up -d`

#### **Cluster Not Accessible:**
```bash
❌ Kubernetes cluster is not accessible
   Check your kubeconfig and cluster status
```
**Solution:** Verify cluster with `kubectl get nodes`

#### **Pod Creation Fails:**
```bash
❌ Pod creation failed:
"error": "kubectl command failed: ..."
```
**Solution:** Check cluster resources and permissions

#### **Tool Call Timeout:**
```bash
❌ Get pod failed:
"error": "Request timeout"
```
**Solution:** Check MCP Server logs: `docker logs mcp-server`

### **Debug Commands:**
```bash
# Check service status
docker-compose ps

# Check MCP Bridge logs
docker logs mcpo --tail 50

# Check MCP Server logs
docker logs mcp-server --tail 50

# Test MCP Bridge health
curl http://localhost:9000/health

# Verify cluster access
kubectl get nodes
kubectl get pods -A
```

---

## 🎯 **Test Customization**

### **Environment Variables:**
```bash
# Customize test configuration
export MCP_BRIDGE_URL="http://localhost:9000"
export TEST_POD_NAME="my-test-pod"
export TEST_NAMESPACE="testing"
```

### **Custom Test Pod:**
Edit the `test_pod_manifest` variable in the test scripts to use different:
- Container images
- Environment variables
- Resource requirements
- Labels and annotations

### **Additional Tests:**
Add new test cases by following the pattern:
```bash
# New test case
echo "Test N: tool_name - Description"
payload=$(jq -n '{"param": "value"}')
response=$(call_mcp_tool "tool_name" "$payload")
check_response "$response" "Operation description"
```

---

## 📈 **Performance Metrics**

### **Typical Test Duration:**
- **Total runtime:** ~45-60 seconds
- **Pod startup:** ~25 seconds (includes waits)
- **Tool calls:** ~15-20 seconds
- **Cleanup:** ~5 seconds

### **Resource Usage:**
- **Test pod:** nginx:alpine (~5MB)
- **Network calls:** ~10-15 HTTP requests
- **Cluster resources:** 1 temporary pod

---

## 🤝 **Contributing**

### **Adding New Tests:**
1. **Identify** the tool to test
2. **Create** test payload
3. **Add** test case to both scripts
4. **Update** documentation
5. **Test** thoroughly

### **Test Guidelines:**
- **Descriptive names** for test cases
- **Proper cleanup** of test resources
- **Error handling** for all scenarios
- **Clear output** with colors and formatting
- **Documentation** for new test cases

---

**The test suite provides comprehensive validation of MCP Server functionality and serves as both quality assurance and usage examples.**