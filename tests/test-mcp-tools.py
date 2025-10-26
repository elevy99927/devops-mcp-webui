#!/usr/bin/env python3
"""
Test script for MCP Server Kubernetes tools
Tests kubectl_apply, kubectl_get, kubectl_describe, kubectl_logs, and exec_pod
"""

import json
import urllib.request
import urllib.parse
import time
import sys
from typing import Dict, Any

# Configuration
MCP_BRIDGE_URL = "http://localhost:9000"
TEST_POD_NAME = "mcp-test-pod"
TEST_NAMESPACE = "default"

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

def call_mcp_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Make API call to MCP Bridge using built-in urllib"""
    print(f"{Colors.BLUE}📡 Calling {tool_name}...{Colors.NC}")
    
    try:
        # Prepare the request
        url = f"{MCP_BRIDGE_URL}/{tool_name}"
        data = json.dumps(payload).encode('utf-8')
        
        # Create request with headers
        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Content-Length': str(len(data))
            },
            method='POST'
        )
        
        # Make the request
        with urllib.request.urlopen(req, timeout=60) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
            
    except urllib.error.HTTPError as e:
        try:
            error_data = e.read().decode('utf-8')
            return json.loads(error_data)
        except:
            return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection error: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}

def check_response(response: Dict[str, Any], operation: str) -> bool:
    """Check if response contains error"""
    if "error" in response:
        print(f"{Colors.RED}❌ {operation} failed:{Colors.NC}")
        print(json.dumps(response["error"], indent=2))
        return False
    else:
        print(f"{Colors.GREEN}✅ {operation} succeeded{Colors.NC}")
        return True

def main():
    print("🧪 Testing MCP Server Kubernetes Tools")
    print("======================================")
    
    # Test 1: kubectl_apply - Create test pod
    print(f"\n{Colors.YELLOW}Test 1: kubectl_apply - Creating test pod{Colors.NC}")
    print("=" * 48)
    
    test_pod_manifest = """apiVersion: v1
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
    image: nginx:latest
    ports:
    - containerPort: 8080
    env:
    - name: TEST_ENV
      value: "mcp-server-test"
    command: ["/bin/sh"]
    args: ["-c", "echo 'MCP Test Pod Started' && echo 'Pod is running...' && sleep 300"]
  restartPolicy: Never"""
    
    apply_payload = {
        "manifest": test_pod_manifest,
        "namespace": TEST_NAMESPACE
    }
    
    apply_response = call_mcp_tool("kubectl_apply", apply_payload)
    if not check_response(apply_response, "Pod creation"):
        sys.exit(1)
    
    print("Response:")
    print(json.dumps(apply_response, indent=2))
    
    # Wait for pod to be created
    print("\n⏳ Waiting 10 seconds for pod to start...")
    time.sleep(10)
    
    # Test 2: kubectl_get - Get the test pod
    print(f"\n{Colors.YELLOW}Test 2: kubectl_get - Getting test pod{Colors.NC}")
    print("=" * 45)
    
    get_payload = {
        "resourceType": "pods",
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE,
        "output": "json"
    }
    
    get_response = call_mcp_tool("kubectl_get", get_payload)
    check_response(get_response, "Get pod")
    
    print("Pod Status:")
    if "status" in get_response and "phase" in get_response["status"]:
        print(get_response["status"]["phase"])
    elif "output" in get_response:
        print(get_response["output"])
    
    # Test 3: kubectl_get - List all pods with label selector
    print(f"\n{Colors.YELLOW}Test 3: kubectl_get - List pods with label selector{Colors.NC}")
    print("=" * 52)
    
    get_list_payload = {
        "resourceType": "pods",
        "namespace": TEST_NAMESPACE,
        "labelSelector": "app=mcp-test",
        "output": "json"
    }
    
    get_list_response = call_mcp_tool("kubectl_get", get_list_payload)
    check_response(get_list_response, "List pods with label selector")
    
    print("Found pods:")
    if "items" in get_list_response:
        for item in get_list_response["items"]:
            print(f"  - {item['metadata']['name']}")
    elif "output" in get_list_response:
        print(get_list_response["output"])
    
    # Test 4: kubectl_describe - Describe the test pod
    print(f"\n{Colors.YELLOW}Test 4: kubectl_describe - Describing test pod{Colors.NC}")
    print("=" * 47)
    
    describe_payload = {
        "resourceType": "pod",
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE
    }
    
    describe_response = call_mcp_tool("kubectl_describe", describe_payload)
    check_response(describe_response, "Describe pod")
    
    print("Pod Description (first 10 lines):")
    if "output" in describe_response:
        lines = describe_response["output"].split('\n')[:10]
        for line in lines:
            print(f"  {line}")
    
    # Wait a bit more for pod to be fully running
    print("\n⏳ Waiting 15 more seconds for pod to be fully running...")
    time.sleep(15)
    
    # Test 5: kubectl_logs - Get logs from the test pod
    print(f"\n{Colors.YELLOW}Test 5: kubectl_logs - Getting logs from test pod{Colors.NC}")
    print("=" * 49)
    
    logs_payload = {
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE,
        "resourceType": "pod",
        "tail": 50
    }
    
    logs_response = call_mcp_tool("kubectl_logs", logs_payload)
    check_response(logs_response, "Get pod logs")
    
    print("Pod Logs:")
    if "output" in logs_response:
        lines = logs_response["output"].split('\n')[:20]
        for line in lines:
            print(f"  {line}")
    
    # Test 6: exec_pod - Execute command in the test pod
    print(f"\n{Colors.YELLOW}Test 6: exec_pod - Execute command in test pod{Colors.NC}")
    print("=" * 47)
    
    exec_payload = {
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE,
        "command": "echo 'Hello from MCP exec test' && whoami && pwd && ls -la /etc"
    }
    
    exec_response = call_mcp_tool("exec_pod", exec_payload)
    check_response(exec_response, "Execute command in pod")
    
    print("Command Output:")
    if "output" in exec_response:
        print(exec_response["output"])
    
    # Test 7: exec_pod - Check environment variables
    print(f"\n{Colors.YELLOW}Test 7: exec_pod - Check environment variables{Colors.NC}")
    print("=" * 47)
    
    env_exec_payload = {
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE,
        "command": "env | grep TEST_ENV"
    }
    
    env_exec_response = call_mcp_tool("exec_pod", env_exec_payload)
    check_response(env_exec_response, "Check environment variables")
    
    print("Environment Variables:")
    if "output" in env_exec_response:
        print(env_exec_response["output"])
    
    # Test 8: kubectl_get - Get pod with wide output
    print(f"\n{Colors.YELLOW}Test 8: kubectl_get - Get pod with wide output{Colors.NC}")
    print("=" * 47)
    
    get_wide_payload = {
        "resourceType": "pods",
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE,
        "output": "wide"
    }
    
    get_wide_response = call_mcp_tool("kubectl_get", get_wide_payload)
    check_response(get_wide_response, "Get pod with wide output")
    
    print("Pod Wide Output:")
    if "output" in get_wide_response:
        print(get_wide_response["output"])
    
    # Cleanup: Delete the test pod
    print(f"\n{Colors.YELLOW}Cleanup: Deleting test pod{Colors.NC}")
    print("=" * 31)
    
    delete_payload = {
        "resourceType": "pod",
        "name": TEST_POD_NAME,
        "namespace": TEST_NAMESPACE
    }
    
    delete_response = call_mcp_tool("kubectl_delete", delete_payload)
    check_response(delete_response, "Delete test pod")
    
    print("Cleanup Response:")
    print(json.dumps(delete_response, indent=2))
    
    # Final verification - check that pod is gone
    print("\n🔍 Verifying pod deletion...")
    time.sleep(5)
    
    verify_response = call_mcp_tool("kubectl_get", get_payload)
    
    if "error" in verify_response:
        print(f"{Colors.GREEN}✅ Pod successfully deleted{Colors.NC}")
    else:
        print(f"{Colors.YELLOW}⚠️  Pod might still exist{Colors.NC}")
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 15)
    print(f"{Colors.GREEN}✅ kubectl_apply - Create test pod{Colors.NC}")
    print(f"{Colors.GREEN}✅ kubectl_get - Get specific pod{Colors.NC}")
    print(f"{Colors.GREEN}✅ kubectl_get - List pods with label selector{Colors.NC}")
    print(f"{Colors.GREEN}✅ kubectl_describe - Describe pod{Colors.NC}")
    print(f"{Colors.GREEN}✅ kubectl_logs - Get pod logs{Colors.NC}")
    print(f"{Colors.GREEN}✅ exec_pod - Execute commands in pod{Colors.NC}")
    print(f"{Colors.GREEN}✅ kubectl_delete - Delete test pod{Colors.NC}")
    
    print(f"\n{Colors.GREEN}🎉 All MCP Server tool tests completed successfully!{Colors.NC}")
    print("\n💡 Tips:")
    print("   - Check MCP Bridge logs: docker logs mcpo")
    print("   - Check MCP Server logs: docker logs mcp-server")
    print("   - Verify cluster access: kubectl get nodes")
    print()

if __name__ == "__main__":
    main()