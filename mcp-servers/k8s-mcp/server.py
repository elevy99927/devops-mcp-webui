#!/usr/bin/env python3
"""
MCP Server for Kubernetes Operations
Executes kubectl, helm, and other Kubernetes commands via MCP protocol
"""

import asyncio
import json
import logging
import subprocess
import yaml
import os
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from mcp.server.models import Tool
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Kubernetes MCP Server")

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

async def execute_command(cmd: List[str], input_data: Optional[str] = None, timeout: int = 60) -> Dict[str, Any]:
    """Execute a command asynchronously"""
    try:
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE if input_data else None,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=input_data.encode() if input_data else None),
            timeout=timeout
        )
        
        if process.returncode == 0:
            # Try to parse as JSON if possible
            try:
                return json.loads(stdout.decode())
            except json.JSONDecodeError:
                return {"output": stdout.decode().strip()}
        else:
            return {"error": f"Command failed: {stderr.decode().strip()}"}
            
    except asyncio.TimeoutError:
        return {"error": f"Command timed out after {timeout} seconds"}
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {"error": str(e)}

@mcp.tool()
async def kubectl_get(
    resourceType: str,
    name: Optional[str] = None,
    namespace: str = "default",
    output: str = "json",
    allNamespaces: bool = False,
    labelSelector: Optional[str] = None,
    fieldSelector: Optional[str] = None
) -> List[TextContent]:
    """List or get Kubernetes resources (pods, services, deployments, etc.)"""
    
    args = ["kubectl", "get", resourceType]
    
    # Add name if specified
    if name:
        args.append(name)
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    # Add output format
    if output == "json":
        args.extend(["-o", "json"])
    elif output == "yaml":
        args.extend(["-o", "yaml"])
    elif output == "wide":
        args.extend(["-o", "wide"])
    
    # Add selectors
    if labelSelector:
        args.extend(["-l", labelSelector])
    if fieldSelector:
        args.extend(["--field-selector", fieldSelector])
    
    # Add all namespaces flag
    if allNamespaces:
        args.append("--all-namespaces")
    
    result = await execute_command(args)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def kubectl_describe(
    resourceType: str,
    name: str,
    namespace: str = "default"
) -> List[TextContent]:
    """Get detailed information about Kubernetes resources"""
    
    args = ["kubectl", "describe", resourceType, name]
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    result = await execute_command(args)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def kubectl_apply(
    manifest: str,
    namespace: str = "default",
    dryRun: bool = False
) -> List[TextContent]:
    """Apply YAML manifests to create or update resources"""
    
    args = ["kubectl", "apply", "-f", "-"]
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    # Add dry-run if specified
    if dryRun:
        args.append("--dry-run=client")
    
    result = await execute_command(args, input_data=manifest)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def kubectl_delete(
    resourceType: str,
    name: str,
    namespace: str = "default",
    force: bool = False
) -> List[TextContent]:
    """Delete Kubernetes resources"""
    
    args = ["kubectl", "delete", resourceType, name]
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    # Add force if specified
    if force:
        args.append("--force")
    
    result = await execute_command(args)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def kubectl_logs(
    name: str,
    namespace: str = "default",
    resourceType: str = "pod",
    container: Optional[str] = None,
    tail: Optional[int] = None,
    follow: bool = False
) -> List[TextContent]:
    """Retrieve logs from pods or deployments"""
    
    args = ["kubectl", "logs"]
    
    if resourceType == "deployment":
        args.append(f"deployment/{name}")
    else:
        args.append(name)
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    # Add container if specified
    if container:
        args.extend(["-c", container])
    
    # Add tail if specified
    if tail:
        args.extend(["--tail", str(tail)])
    
    # Add follow if specified (note: this might not work well in MCP context)
    if follow:
        args.append("-f")
    
    result = await execute_command(args, timeout=120)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def kubectl_scale(
    name: str,
    replicas: int,
    namespace: str = "default",
    resourceType: str = "deployment"
) -> List[TextContent]:
    """Scale deployments, statefulsets, or replicasets"""
    
    args = ["kubectl", "scale", f"{resourceType}/{name}", f"--replicas={replicas}"]
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    result = await execute_command(args)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def helm_install(
    name: str,
    chart: str,
    namespace: str = "default",
    repo: Optional[str] = None,
    values: Optional[Dict[str, Any]] = None
) -> List[TextContent]:
    """Install a Helm chart"""
    
    args = ["helm", "install", name]
    
    # Add chart
    if repo:
        args.extend(["--repo", repo])
    args.append(chart)
    
    # Add namespace
    if namespace != "default":
        args.extend(["--namespace", namespace, "--create-namespace"])
    
    # Add values if specified
    if values:
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
    
    result = await execute_command(args, timeout=300)  # Helm operations can take longer
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def helm_upgrade(
    name: str,
    chart: str,
    namespace: str = "default",
    repo: Optional[str] = None,
    values: Optional[Dict[str, Any]] = None
) -> List[TextContent]:
    """Upgrade an existing Helm release"""
    
    args = ["helm", "upgrade", name]
    
    # Add chart
    if repo:
        args.extend(["--repo", repo])
    args.append(chart)
    
    # Add namespace
    if namespace != "default":
        args.extend(["--namespace", namespace])
    
    # Add values if specified
    if values:
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
    
    result = await execute_command(args, timeout=300)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def helm_uninstall(
    name: str,
    namespace: str = "default"
) -> List[TextContent]:
    """Uninstall a Helm release"""
    
    args = ["helm", "uninstall", name]
    
    # Add namespace
    if namespace != "default":
        args.extend(["--namespace", namespace])
    
    result = await execute_command(args, timeout=120)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def exec_pod(
    name: str,
    command: str,
    namespace: str = "default",
    container: Optional[str] = None
) -> List[TextContent]:
    """Execute a command inside a pod container"""
    
    args = ["kubectl", "exec", "-it", name]
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    # Add container if specified
    if container:
        args.extend(["-c", container])
    
    # Add command
    args.extend(["--", "sh", "-c", command])
    
    result = await execute_command(args, timeout=120)
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

@mcp.tool()
async def port_forward(
    resourceType: str,
    resourceName: str,
    localPort: int,
    targetPort: int,
    namespace: str = "default"
) -> List[TextContent]:
    """Forward a local port to a pod or service"""
    
    args = ["kubectl", "port-forward", f"{resourceType}/{resourceName}", f"{localPort}:{targetPort}"]
    
    # Add namespace
    if namespace != "default":
        args.extend(["-n", namespace])
    
    # Note: Port forwarding is a long-running operation, this might not work well in MCP context
    result = await execute_command(args, timeout=10)  # Short timeout for testing
    return [TextContent(type="text", text=json.dumps(result, indent=2))]

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()