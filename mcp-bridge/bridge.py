#!/usr/bin/env python3
"""
MCP to OpenAPI Bridge
Translates OpenAPI calls from Open WebUI to MCP protocol calls to k8s-mcp-server
"""

import json
import logging
import requests
import sseclient
import yaml
import os
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MCP Server configuration
MCP_SERVER_URL = "http://k8s-mcp-server-backend:8080"

def fix_kubeconfig():
    """Fix kubeconfig to use the correct API server endpoint"""
    try:
        kubeconfig_path = "/root/.kube/config"
        if os.path.exists(kubeconfig_path):
            with open(kubeconfig_path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Update the server URL to use the kind container directly
            for cluster in config.get('clusters', []):
                if 'kind-mcp-lab-control-plane' in cluster['cluster']['server']:
                    # Change to use the kind container directly on port 6443
                    cluster['cluster']['server'] = 'https://kind-mcp-lab-control-plane:6443'
                    logger.info(f"Updated cluster server to: {cluster['cluster']['server']}")
            
            # Write back the modified config
            with open(kubeconfig_path, 'w') as f:
                yaml.dump(config, f)
                
            logger.info("Kubeconfig updated successfully")
    except Exception as e:
        logger.error(f"Failed to fix kubeconfig: {e}")

# Fix kubeconfig on startup
fix_kubeconfig()

def execute_kubectl_command(args, input_data=None):
    """Execute kubectl command directly"""
    import subprocess
    import json
    
    try:
        # Build the full kubectl command
        cmd = ["kubectl"] + args
        logger.info(f"Executing kubectl command: {' '.join(cmd)}")
        
        # Execute the command
        result = subprocess.run(
            cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Try to parse as JSON if possible
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout.strip()}
        else:
            return {"error": f"kubectl command failed: {result.stderr.strip()}"}
            
    except subprocess.TimeoutExpired:
        return {"error": "kubectl command timed out"}
    except Exception as e:
        logger.error(f"Error executing kubectl command: {e}")
        return {"error": str(e)}

def execute_helm_command(args, input_data=None):
    """Execute helm command directly"""
    import subprocess
    import json
    
    try:
        # Build the full helm command
        cmd = args  # args already includes 'helm' as first element
        logger.info(f"Executing helm command: {' '.join(cmd)}")
        logger.info(f"Full command args: {args}")
        
        # Execute the command
        result = subprocess.run(
            cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=120  # Helm operations can take longer
        )
        
        logger.info(f"Helm command stdout: {result.stdout}")
        logger.info(f"Helm command stderr: {result.stderr}")
        logger.info(f"Helm command return code: {result.returncode}")
        
        if result.returncode == 0:
            # Try to parse as JSON if possible
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout.strip()}
        else:
            return {"error": f"helm command failed: {result.stderr.strip()}"}
            
    except subprocess.TimeoutExpired:
        return {"error": "helm command timed out"}
    except Exception as e:
        logger.error(f"Error executing helm command: {e}")
        return {"error": str(e)}

def call_mcp_tool_via_sse(tool_name, arguments):
    """Call kubectl directly instead of via MCP for now"""
    try:
        logger.info(f"Calling tool {tool_name} with args: {arguments}")
        
        if tool_name == "kubectl_get":
            # Build kubectl get command
            args = ["get", arguments.get("resourceType", "pods")]
            
            # Add name if specified
            if arguments.get("name"):
                args.append(arguments["name"])
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            # Add output format
            output_format = arguments.get("output", "json")
            if output_format == "json":
                args.extend(["-o", "json"])
            elif output_format == "yaml":
                args.extend(["-o", "yaml"])
            elif output_format == "wide":
                args.extend(["-o", "wide"])
            
            # Add selectors
            if arguments.get("labelSelector"):
                args.extend(["-l", arguments["labelSelector"]])
            if arguments.get("fieldSelector"):
                args.extend(["--field-selector", arguments["fieldSelector"]])
            
            # Add all namespaces flag
            if arguments.get("allNamespaces"):
                args.append("--all-namespaces")
            
            return execute_kubectl_command(args)
            
        elif tool_name == "kubectl_describe":
            # Build kubectl describe command
            args = ["describe", arguments.get("resourceType", "pod"), arguments.get("name", "")]
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            return execute_kubectl_command(args)
            
        elif tool_name == "kubectl_logs":
            # Build kubectl logs command
            args = ["logs"]
            
            if arguments.get("resourceType") == "deployment":
                args.append(f"deployment/{arguments.get('name', '')}")
            else:
                args.append(arguments.get("name", ""))
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            # Add container if specified
            if arguments.get("container"):
                args.extend(["-c", arguments["container"]])
            
            # Add tail if specified
            if arguments.get("tail"):
                args.extend(["--tail", str(arguments["tail"])])
            
            # Add follow if specified
            if arguments.get("follow"):
                args.append("-f")
            
            return execute_kubectl_command(args)
            
        elif tool_name == "kubectl_apply":
            # Build kubectl apply command
            args = ["apply", "-f", "-"]  # Read from stdin
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            # Add dry-run if specified
            if arguments.get("dryRun"):
                args.append("--dry-run=client")
            
            # Handle manifest content
            manifest = arguments.get("manifest")
            if manifest:
                return execute_kubectl_command(args, input_data=manifest)
            else:
                return {"error": "No manifest provided"}
                
        elif tool_name == "kubectl_delete":
            # Build kubectl delete command
            args = ["delete", arguments.get("resourceType", "pod"), arguments.get("name", "")]
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            # Add force if specified
            if arguments.get("force"):
                args.append("--force")
            
            return execute_kubectl_command(args)
            
        elif tool_name == "kubectl_scale":
            # Build kubectl scale command
            resource_type = arguments.get("resourceType", "deployment")
            name = arguments.get("name", "")
            replicas = arguments.get("replicas", 1)
            
            args = ["scale", f"{resource_type}/{name}", f"--replicas={replicas}"]
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            return execute_kubectl_command(args)
            
        elif tool_name == "install_helm_chart":
            # Build helm install command
            args = ["helm", "install", arguments.get("name", "")]
            
            # Add chart
            chart = arguments.get("chart", "")
            if arguments.get("repo"):
                # Add repo if specified
                args.extend(["--repo", arguments["repo"]])
            args.append(chart)
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["--namespace", namespace, "--create-namespace"])
            
            # Add values if specified
            values = arguments.get("values")
            if values:
                # Convert nested dict to --set format
                def dict_to_set_args(d, prefix=""):
                    set_args = []
                    for key, value in d.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, dict):
                            set_args.extend(dict_to_set_args(value, full_key))
                        else:
                            set_args.extend(["--set", f"{full_key}={value}"])
                    return set_args
                
                args.extend(dict_to_set_args(values))
            
            return execute_helm_command(args)
            
        elif tool_name == "upgrade_helm_chart":
            # Build helm upgrade command
            args = ["helm", "upgrade", arguments.get("name", "")]
            
            # Add chart
            chart = arguments.get("chart", "")
            if arguments.get("repo"):
                # Add repo if specified
                args.extend(["--repo", arguments["repo"]])
            args.append(chart)
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["--namespace", namespace])
            
            # Add values if specified
            values = arguments.get("values")
            if values:
                # Convert nested dict to --set format
                def dict_to_set_args(d, prefix=""):
                    set_args = []
                    for key, value in d.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if isinstance(value, dict):
                            set_args.extend(dict_to_set_args(value, full_key))
                        else:
                            set_args.extend(["--set", f"{full_key}={value}"])
                    return set_args
                
                args.extend(dict_to_set_args(values))
            
            return execute_helm_command(args)
            
        elif tool_name == "uninstall_helm_chart":
            # Build helm uninstall command
            args = ["helm", "uninstall", arguments.get("name", "")]
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["--namespace", namespace])
            
            return execute_helm_command(args)
            
        elif tool_name == "exec_in_pod":
            # Build kubectl exec command
            args = ["exec", "-it", arguments.get("name", "")]
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            # Add container if specified
            if arguments.get("container"):
                args.extend(["-c", arguments["container"]])
            
            # Add command
            command = arguments.get("command", "")
            if command:
                args.extend(["--", "sh", "-c", command])
            
            return execute_kubectl_command(args)
            
        elif tool_name == "port_forward":
            # Build kubectl port-forward command
            resource_type = arguments.get("resourceType", "pod")
            resource_name = arguments.get("resourceName", "")
            local_port = arguments.get("localPort", 8080)
            target_port = arguments.get("targetPort", 80)
            
            args = ["port-forward", f"{resource_type}/{resource_name}", f"{local_port}:{target_port}"]
            
            # Add namespace
            namespace = arguments.get("namespace", "default")
            if namespace != "default":
                args.extend(["-n", namespace])
            
            return execute_kubectl_command(args)
        
        else:
            return {"error": f"Tool {tool_name} not implemented yet"}
        
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return {"error": str(e)}

# OpenAPI specification for Open WebUI - Complete k8s-mcp-server capabilities
OPENAPI_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Kubernetes Management Tools",
        "version": "1.0.0",
        "description": "Complete Kubernetes management via kubectl, helm, istioctl, and argocd"
    },
    "servers": [{"url": "/", "description": "Kubernetes Tools"}],
    "paths": {
        "/health": {
            "get": {
                "summary": "Health check",
                "operationId": "health_check",
                "responses": {"200": {"description": "Service is healthy"}}
            }
        },
        # kubectl operations
        "/kubectl_get": {
            "post": {
                "summary": "Get Kubernetes Resources",
                "description": "List or get Kubernetes resources (pods, services, deployments, etc.)",
                "operationId": "kubectl_get",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceType": {"type": "string", "description": "Resource type (pods, services, deployments, etc.)"},
                                    "name": {"type": "string", "description": "Resource name (optional)"},
                                    "namespace": {"type": "string", "default": "default", "description": "Namespace"},
                                    "output": {"type": "string", "enum": ["json", "yaml", "wide", "name"], "default": "json"},
                                    "allNamespaces": {"type": "boolean", "default": False},
                                    "labelSelector": {"type": "string", "description": "Label selector"},
                                    "fieldSelector": {"type": "string", "description": "Field selector"}
                                },
                                "required": ["resourceType"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Resource information"}}
            }
        },
        "/kubectl_describe": {
            "post": {
                "summary": "Describe Kubernetes Resources",
                "description": "Get detailed information about Kubernetes resources",
                "operationId": "kubectl_describe",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceType": {"type": "string", "description": "Resource type"},
                                    "name": {"type": "string", "description": "Resource name"},
                                    "namespace": {"type": "string", "default": "default"}
                                },
                                "required": ["resourceType", "name"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Detailed resource information"}}
            }
        },
        "/kubectl_apply": {
            "post": {
                "summary": "Apply Kubernetes Manifests",
                "description": "Apply YAML manifests to create or update resources",
                "operationId": "kubectl_apply",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "manifest": {"type": "string", "description": "YAML manifest content"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "dryRun": {"type": "boolean", "default": False}
                                }
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Apply result"}}
            }
        },
        "/kubectl_delete": {
            "post": {
                "summary": "Delete Kubernetes Resources",
                "description": "Delete Kubernetes resources",
                "operationId": "kubectl_delete",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceType": {"type": "string", "description": "Resource type"},
                                    "name": {"type": "string", "description": "Resource name"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "force": {"type": "boolean", "default": False}
                                },
                                "required": ["resourceType", "name"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Delete result"}}
            }
        },
        "/kubectl_logs": {
            "post": {
                "summary": "Get Pod Logs",
                "description": "Retrieve logs from pods or deployments",
                "operationId": "kubectl_logs",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceType": {"type": "string", "enum": ["pod", "deployment"], "default": "pod"},
                                    "name": {"type": "string", "description": "Resource name"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "container": {"type": "string", "description": "Container name (optional)"},
                                    "tail": {"type": "number", "description": "Number of lines to show"},
                                    "follow": {"type": "boolean", "default": False}
                                },
                                "required": ["name", "namespace"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Log output"}}
            }
        },
        "/kubectl_scale": {
            "post": {
                "summary": "Scale Kubernetes Resources",
                "description": "Scale deployments, statefulsets, or replicasets",
                "operationId": "kubectl_scale",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Resource name"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "replicas": {"type": "number", "description": "Number of replicas"},
                                    "resourceType": {"type": "string", "default": "deployment"}
                                },
                                "required": ["name", "replicas"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Scale result"}}
            }
        },
        # Helm operations
        "/helm_install": {
            "post": {
                "summary": "Install Helm Chart",
                "description": "Install a Helm chart",
                "operationId": "helm_install",
                "tags": ["helm"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Release name"},
                                    "chart": {"type": "string", "description": "Chart name"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "repo": {"type": "string", "description": "Helm repository URL"},
                                    "values": {"type": "object", "description": "Chart values"}
                                },
                                "required": ["name", "chart", "namespace"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Installation result"}}
            }
        },
        "/helm_upgrade": {
            "post": {
                "summary": "Upgrade Helm Release",
                "description": "Upgrade an existing Helm release",
                "operationId": "helm_upgrade",
                "tags": ["helm"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Release name"},
                                    "chart": {"type": "string", "description": "Chart name"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "values": {"type": "object", "description": "Chart values"}
                                },
                                "required": ["name", "chart", "namespace"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Upgrade result"}}
            }
        },
        "/helm_uninstall": {
            "post": {
                "summary": "Uninstall Helm Release",
                "description": "Uninstall a Helm release",
                "operationId": "helm_uninstall",
                "tags": ["helm"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Release name"},
                                    "namespace": {"type": "string", "default": "default"}
                                },
                                "required": ["name", "namespace"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Uninstall result"}}
            }
        },
        # Additional operations
        "/exec_pod": {
            "post": {
                "summary": "Execute Command in Pod",
                "description": "Execute a command inside a pod container",
                "operationId": "exec_pod",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string", "description": "Pod name"},
                                    "namespace": {"type": "string", "default": "default"},
                                    "command": {"type": "string", "description": "Command to execute"},
                                    "container": {"type": "string", "description": "Container name (optional)"}
                                },
                                "required": ["name", "command"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Command output"}}
            }
        },
        "/port_forward": {
            "post": {
                "summary": "Port Forward",
                "description": "Forward a local port to a pod or service",
                "operationId": "port_forward",
                "tags": ["kubectl"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "resourceType": {"type": "string", "description": "Resource type (pod/service)"},
                                    "resourceName": {"type": "string", "description": "Resource name"},
                                    "localPort": {"type": "number", "description": "Local port"},
                                    "targetPort": {"type": "number", "description": "Target port"},
                                    "namespace": {"type": "string", "default": "default"}
                                },
                                "required": ["resourceType", "resourceName", "localPort", "targetPort"]
                            }
                        }
                    }
                },
                "responses": {"200": {"description": "Port forward result"}}
            }
        }
    }
}

@app.route("/openapi.json", methods=["GET"])
def get_openapi_spec():
    """Return OpenAPI specification for Open WebUI"""
    return jsonify(OPENAPI_SPEC)

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

# kubectl operations
@app.route("/kubectl_get", methods=["POST"])
def kubectl_get():
    """Execute kubectl get command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"kubectl_get request: {data}")
        
        # Call MCP server
        result = call_mcp_tool_via_sse("kubectl_get", data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in kubectl_get: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/kubectl_describe", methods=["POST"])
def kubectl_describe():
    """Execute kubectl describe command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"kubectl_describe request: {data}")
        
        result = call_mcp_tool_via_sse("kubectl_describe", data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in kubectl_describe: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/kubectl_apply", methods=["POST"])
def kubectl_apply():
    """Execute kubectl apply command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"kubectl_apply request: {data}")
        
        result = call_mcp_tool_via_sse("kubectl_apply", data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in kubectl_apply: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/kubectl_delete", methods=["POST"])
def kubectl_delete():
    """Execute kubectl delete command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"kubectl_delete request: {data}")
        
        result = call_mcp_tool_via_sse("kubectl_delete", data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in kubectl_delete: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/kubectl_logs", methods=["POST"])
def kubectl_logs():
    """Execute kubectl logs command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"kubectl_logs request: {data}")
        
        result = call_mcp_tool_via_sse("kubectl_logs", data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in kubectl_logs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/kubectl_scale", methods=["POST"])
def kubectl_scale():
    """Execute kubectl scale command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"kubectl_scale request: {data}")
        
        result = call_mcp_tool_via_sse("kubectl_scale", data)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in kubectl_scale: {e}")
        return jsonify({"error": str(e)}), 500

# Helm operations
@app.route("/helm_install", methods=["POST"])
def helm_install():
    """Execute helm install command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"helm_install request: {data}")
        result = call_mcp_tool_via_sse("install_helm_chart", data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in helm_install: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/helm_upgrade", methods=["POST"])
def helm_upgrade():
    """Execute helm upgrade command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"helm_upgrade request: {data}")
        result = call_mcp_tool_via_sse("upgrade_helm_chart", data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in helm_upgrade: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/helm_uninstall", methods=["POST"])
def helm_uninstall():
    """Execute helm uninstall command via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"helm_uninstall request: {data}")
        result = call_mcp_tool_via_sse("uninstall_helm_chart", data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in helm_uninstall: {e}")
        return jsonify({"error": str(e)}), 500

# Additional operations
@app.route("/exec_pod", methods=["POST"])
def exec_pod():
    """Execute command in pod via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"exec_pod request: {data}")
        result = call_mcp_tool_via_sse("exec_in_pod", data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in exec_pod: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/port_forward", methods=["POST"])
def port_forward():
    """Execute port forward via MCP server"""
    try:
        data = request.get_json()
        logger.info(f"port_forward request: {data}")
        result = call_mcp_tool_via_sse("port_forward", data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in port_forward: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)