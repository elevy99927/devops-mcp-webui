# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Log collection system for all Docker containers
- `collect-logs.sh` script to gather container logs into `./logs/` directory
- Log rotation configuration (10MB max size, 3 files per container)
- Comprehensive badges to README.md (Kind, Helm, kubectl, Docker Compose, Kubernetes, Open WebUI, Ollama, MCP Protocol, MIT License)
- "How It Works" section with step-by-step workflow explanation
- Data flow diagram showing user interaction process

### Changed
- Updated `docker-compose.yml` to include logging configuration for all services
- Removed obsolete `version` field from docker-compose.yml
- Simplified architecture from 5 to 4 components in README.md
- Updated mermaid diagrams to show direct MCP-Bridge → Kubernetes flow
- Removed k8s-mcp-server-backend references from documentation
- Cleaned up component descriptions and network architecture

### Removed
- `BRIDGE_VS_MCP_COMPARISON.md` file (170 lines of comparison documentation)
- k8s-mcp-server references from architecture diagrams
- Redundant MCP server layer from documentation

### Fixed
- Resolved Docker logging configuration error with unsupported `path` option


## How It Works — Step by Step

1. **The user types:**
```

Show me all pods running in the cluster.

````

2. **Open-WebUI** sends this query to the **LLM (Language Model)** —  
the model interprets the intent and decides which **tool** to use,  
based on the definitions provided in the `openapi.json` file.

3. **The LLM** then asks the **MCP Bridge** to execute the corresponding action —  
for example, it might send a structured request like:
```json
{
  "tool": "k8s_get_pods",
  "parameters": {}
}
````

4. **The MCP Bridge** translates this into a real command, such as:

   ```bash
   kubectl get pods -A -o json
   ```

   It runs the command against the cluster and returns the output to the LLM.

5. **The LLM** summarizes the result in natural language,
   and **Open-WebUI** displays the response to the user.

---

### 🧠 Data Flow

```
User → Open-WebUI → LLM → MCP-Bridge → MCP Server (kubectl) → LLM → Open-WebUI → User
```

The **LLM** decides *when* to trigger the Bridge,
and the **Bridge** simply executes the actual commands.

```

