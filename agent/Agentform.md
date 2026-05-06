# Agentform - Declarative Agent Framework
# Source: https://github.com/Agentform-org/Agentform

## Philosophy
Agentform takes a declarative approach to agent definition. Instead of writing imperative code, describe your agents in Agentform's native schema and let the runtime engine handle the rest.

## Agent Definition Syntax

```agentform
agent "reviewer" {
  model        = model.gpt4o
  instructions = "Review code for security issues"
  allow        = [capability.read_file, capability.get_diff]
  policy       = policy.strict
}

agent "developer" {
  model        = model.gpt4
  instructions = "Write clean, well-documented code"
  allow        = [capability.write_file, capability.run_tests]
  policy       = policy.default
}

workflow "code_review" {
  steps = [
    { agent = "reviewer", task = "analyze code" },
    { agent = "developer", task = "fix issues" },
    { agent = "reviewer", task = "verify fixes" }
  ]
}
```

## Core Features
| Feature | Description |
|---------|-------------|
| Declarative Syntax | Define agents without writing code |
| Policy-Based Access | Granular permission control |
| Workflow Orchestration | Define multi-agent workflows |
| Model Abstraction | Works with any LLM |
| Auto-Retry | Automatic retry on failures |

## Benefits
- Reduces boilerplate code by 80%
- Easier to audit and review
- Consistent agent behavior
- Built-in best practices
- Rapid prototyping

---
Version: 2.0 | Agentform Framework