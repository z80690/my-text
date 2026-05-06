# AGENT.md - Universal Agent Configuration File
# Source: https://github.com/agentmd/agent.md

## Purpose
This file defines a standard format for AI agent configuration files. The goal is to create a human-readable, machine-parsable format that enables agentic coding tools to understand and interact with software projects.

## Format Specification

### 1. Project Metadata
```yaml
name: "Project Name"
version: "1.0.0"
description: "Brief description of the project"
author: "Author Name"
license: "MIT"
```

### 2. Agent Capabilities
| Capability | Description | Status |
|------------|-------------|--------|
| code_generation | Generate code based on prompts | ✅ |
| code_analysis | Analyze code structure and patterns | ✅ |
| debugging | Assist with debugging tasks | ✅ |
| testing | Generate and run tests | ✅ |

### 3. Tool Access
```yaml
tools:
  - name: file_read
    description: Read file contents
    permissions: read
  
  - name: file_write
    description: Write to files
    permissions: write
  
  - name: command_exec
    description: Execute shell commands
    permissions: restricted
```

### 4. Safety Guidelines
- Never execute destructive commands without confirmation
- Validate all user inputs before processing
- Limit file system access to project directory
- Use sandboxed execution environment

### 5. Output Standards
- Format code according to project conventions
- Provide clear explanations for all actions
- Include error handling and recovery strategies
- Maintain consistent code style throughout

---
Version: 1.0 | Last Updated: 2026-05-05