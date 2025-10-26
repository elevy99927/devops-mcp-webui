#!/usr/bin/env python3
"""
MCP Bridge - REST API to MCP Protocol Bridge
Exposes Kubernetes operations via REST API and communicates with MCP Server via SSE
"""

import json
import logging
import requests
import sseclient
from flask import Flask, request, jsonify
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MCP Server configuration
MCP_SERVER_URL = "http://mcp-server:8080"

class MCPClient:
    """Client for communicating with MCP Server via SSE"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session_url = None
        self.tools = {}
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize SSE connection and get available tools"""
        try:
            # Establish SSE connection
            sse_response = requests.get(f"{self.server_url}/sse", stream=True, timeout=10)
            
            if sse_response.status_code != 200:
                logger.error(f"Failed to connect to SSE endpoint: {sse_response.status_code}")
                return
            
            # Parse SSE response to get the session endpoint
            client = sseclient.SSEClient(sse_response)
            
            for event in client.events():
                if event.event == 'endpoint':
                    self.session_url = f"{self.server_url}{event.data}"
                    logger.info(f"Got session endpoint: {self.session_url}")
                    break
            
            if not self.session_url:
                logger.error("Failed to get session endpoint from SSE")
                return
            
            # Initialize MCP session
            self._initialize_mcp_session()
            
            # Get available tools
            self._fetch_tools()
            
        except Exception as e:
            logger.error(f"Error initializing MCP connection: {e}")
    
    def _initialize_mcp_session(self):
        """Initialize the MCP session"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Step 1: Initialize
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-bridge",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            response = requests.post(self.session_url, json=init_request, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"MCP initialization failed: {response.status_code}")
                return
            
            # Step 2: Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            }
            
            requests.post(self.session_url, json=initialized_notification, headers=headers, timeout=10)
            logger.info("MCP session initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MCP session: {e}")
    
    def _fetch_tools(self):
        """Fetch available tools from MCP server"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            
            response = requests.post(self.session_url, json=tools_request, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result and "tools" in result["result"]:
                    for tool in result["result"]["tools"]:
                        self.tools[tool["name"]] = tool
                    logger.info(f"Fetched {len(self.tools)} tools from MCP server")
                else:
                    logger.warning("No tools found in MCP server response")
            else:
                logger.error(f"Failed to fetch tools: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching tools: {e}")
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            if not self.session_url:
                return {"error": "MCP session not initialized"}
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            tool_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                },
                "id": 3
            }
            
            logger.info(f"Calling MCP tool {tool_name} with args: {arguments}")
            response = requests.post(self.session_url, json=tool_request, headers=headers, timeout=120)
            
            if response.status_code == 200:
                result = response.json()
                if "result" in result:
                    # Extract text content from MCP response
                    if "content" in result["result"] and result["result"]["content"]:
                        content = result["result"]["content"][0]
                        if content["type"] == "text":
                            try:
                                return json.loads(content["text"])
                            except json.JSONDecodeError:
                                return {"output": content["text"]}
                    return result["result"]
                elif "error" in result:
                    return {"error": result["error"]}
            
            return {"error": f"MCP tool call failed with status {response.status_code}: {response.text}"}
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {tool_name}: {e}")
            return {"error": str(e)}
    
    def get_tools(self) -> Dict[str, Any]:
        """Get available tools"""
        return self.tools

# Initialize MCP client
mcp_client = MCPClient(MCP_SERVER_URL)

def generate_openapi_spec() -> Dict[str, Any]:
    """Generate OpenAPI specification dynamically from MCP capabilities"""
    
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "Kubernetes Management Tools",
            "version": "1.0.0",
            "description": "Kubernetes management via MCP protocol"
        },
        "servers": [{"url": "/", "description": "Kubernetes Tools"}],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "operationId": "health_check",
                    "responses": {"200": {"description": "Service is healthy"}}
                }
            }
        }
    }
    
    # Generate paths from MCP tools
    tools = mcp_client.get_tools()
    
    for tool_name, tool_info in tools.items():
        # Convert tool name to REST endpoint
        endpoint = f"/{tool_name}"
        
        # Extract parameters from tool schema
        properties = {}
        required = []
        
        if "inputSchema" in tool_info:
            schema = tool_info["inputSchema"]
            if "properties" in schema:
                properties = schema["properties"]
            if "required" in schema:
                required = schema["required"]
        
        # Create OpenAPI path
        spec["paths"][endpoint] = {
            "post": {
                "summary": tool_info.get("description", f"Execute {tool_name}"),
                "description": tool_info.get("description", f"Execute {tool_name} command"),
                "operationId": tool_name,
                "tags": [tool_name.split("_")[0]],  # Use first part as tag (kubectl, helm, etc.)
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": properties,
                                "required": required
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Command result"}}
            }
        }
    
    return spec

@app.route("/openapi.json", methods=["GET"])
def get_openapi_spec():
    """Return dynamically generated OpenAPI specification"""
    return jsonify(generate_openapi_spec())

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "mcp_tools": len(mcp_client.get_tools())})

# Dynamic route handler for all MCP tools
@app.route("/<tool_name>", methods=["POST"])
def handle_tool_call(tool_name: str):
    """Handle tool calls dynamically"""
    try:
        data = request.get_json() or {}
        logger.info(f"{tool_name} request: {data}")
        
        # Check if tool exists
        if tool_name not in mcp_client.get_tools():
            return jsonify({"error": f"Tool {tool_name} not found"}), 404
        
        # Call MCP server
        result = mcp_client.call_tool(tool_name, data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in {tool_name}: {e}")
        return jsonify({"error": str(e)}), 500

# Specific routes for backward compatibility
@app.route("/kubectl_get", methods=["POST"])
def kubectl_get():
    """Execute kubectl get command"""
    return handle_tool_call("kubectl_get")

@app.route("/kubectl_describe", methods=["POST"])
def kubectl_describe():
    """Execute kubectl describe command"""
    return handle_tool_call("kubectl_describe")

@app.route("/kubectl_apply", methods=["POST"])
def kubectl_apply():
    """Execute kubectl apply command"""
    return handle_tool_call("kubectl_apply")

@app.route("/kubectl_delete", methods=["POST"])
def kubectl_delete():
    """Execute kubectl delete command"""
    return handle_tool_call("kubectl_delete")

@app.route("/kubectl_logs", methods=["POST"])
def kubectl_logs():
    """Execute kubectl logs command"""
    return handle_tool_call("kubectl_logs")

@app.route("/kubectl_scale", methods=["POST"])
def kubectl_scale():
    """Execute kubectl scale command"""
    return handle_tool_call("kubectl_scale")

@app.route("/helm_install", methods=["POST"])
def helm_install():
    """Execute helm install command"""
    return handle_tool_call("helm_install")

@app.route("/helm_upgrade", methods=["POST"])
def helm_upgrade():
    """Execute helm upgrade command"""
    return handle_tool_call("helm_upgrade")

@app.route("/helm_uninstall", methods=["POST"])
def helm_uninstall():
    """Execute helm uninstall command"""
    return handle_tool_call("helm_uninstall")

@app.route("/exec_pod", methods=["POST"])
def exec_pod():
    """Execute command in pod"""
    return handle_tool_call("exec_pod")

@app.route("/port_forward", methods=["POST"])
def port_forward():
    """Execute port forward"""
    return handle_tool_call("port_forward")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)