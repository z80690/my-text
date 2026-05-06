# Portable Agent Manifest (PAM)
# Source: https://github.com/JSON-Agents

## Overview
The Portable Agent Manifest is a universal, JSON-native format for describing AI agents, their capabilities, tools, runtimes, and governance in a single, interoperable manifest.

## Manifest Structure

```json
{
  "$schema": "https://json-agents.org/schema/v1",
  "id": "agent://my-agent",
  "version": "1.0.0",
  "name": "My Agent",
  "description": "A versatile AI agent",
  
  "capabilities": {
    "reasoning": true,
    "tool_use": true,
    "memory": "short-term",
    "learning": false
  },
  
  "tools": [
    {
      "id": "web_search",
      "name": "Web Search",
      "description": "Search the web for information",
      "parameters": {
        "query": "string"
      }
    }
  ],
  
  "runtime": {
    "type": "python",
    "version": "3.11+",
    "memory_limit_mb": 512
  },
  
  "governance": {
    "rate_limit": 100,
    "timeout_seconds": 30,
    "allowed_domains": ["*"]
  }
}
```

## Framework Compatibility
- ✅ LangChain
- ✅ OpenAI Agents
- ✅ AutoGen
- ✅ MCP (Model Context Protocol)
- ✅ Custom Frameworks

## Key Features
1. **Framework Agnostic**: Works across all major agent frameworks
2. **Self-Describing**: Contains all metadata needed for integration
3. **Secure**: Built-in governance and rate limiting
4. **Versioned**: Supports semantic versioning

---
Format Version: 1.0 | Specification: PAM-v1