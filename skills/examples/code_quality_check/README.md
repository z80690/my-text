# Code Quality Check Skill

A skill that analyzes Python files and generates code quality reports.

## Overview

This skill performs static analysis on Python files to identify potential quality issues:

- File statistics (size, line count)
- Code complexity metrics
- Common code smells and issues
- Quality letter grade (A/B/C/D/F)

## Usage

```python
from skills.examples.code_quality_check.handler import handle

result = handle({"file_path": "/path/to/your/file.py"})

if result["success"]:
    report = result["data"]
    print(f"Grade: {report['grade']}")
    print(f"Issues: {report['issues']['count']}")
else:
    print(f"Error: {result['error']}")
```

### Command Line

```bash
cd skills/examples/code_quality_check
python handler.py /path/to/your/file.py
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute or relative path to Python file |

## Output Format

```json
{
  "success": true,
  "data": {
    "file_path": "example.py",
    "file_size_bytes": 1024,
    "total_lines": 100,
    "complexity": {
      "average_function_length": 15.5,
      "function_count": 5
    },
    "issues": {
      "count": 3,
      "details": [
        {
          "type": "long_line",
          "line": 42,
          "length": 150,
          "max_allowed": 120,
          "snippet": "..."
        }
      ]
    },
    "grade": "B"
  }
}
```

## Quality Metrics

### Grading Criteria

| Grade | Description |
|-------|-------------|
| **A** | Excellent - Few or no issues |
| **B** | Good - Minor issues only |
| **C** | Fair - Some issues, needs attention |
| **D** | Poor - Multiple issues, refactoring recommended |
| **F** | Failing - Critical issues, requires immediate attention |

### Issue Types

| Type | Description | Threshold |
|------|-------------|-----------|
| `long_line` | Lines exceeding max length | > 120 characters |
| `todo_comment` | TODO/FIXME/HACK comments | Any |
| `unused_import` | Potentially unused imports | Simple heuristic |

### Complexity Metrics

- **Average Function Length**: Lower is better
  - < 20 lines: Good
  - 20-30 lines: Acceptable
  - 30-50 lines: Needs attention
  - > 50 lines: Too long

## Examples

### Analyzing a Single File

```python
from skills.examples.code_quality_check.handler import handle

result = handle({"file_path": "src/utils.py"})
print(f"Quality Grade: {result['data']['grade']}")
```

### Batch Analysis

```python
import os
from skills.examples.code_quality_check.handler import handle

python_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            python_files.append(os.path.join(root, file))

for file_path in python_files:
    result = handle({"file_path": file_path})
    if result["success"] and result["data"]["grade"] in ["D", "F"]:
        print(f"{file_path}: {result['data']['grade']}")
```

## Integration with Logic Chain

```python
from skills.logic_chain import ChainExecutor, SkillNode

executor = ChainExecutor()
executor.register_node(SkillNode(
    node_id="check_quality",
    name="Check Code Quality",
    skill_name="code_quality_check",
    parameters={"file_path": "$target_file"},
    output_key="quality_report",
))

context = await executor.execute_chain(
    chain_name="code_review",
    start_node_id="check_quality",
    user_data={"target_file": "my_module.py"},
)

report = context.get("quality_report")
print(f"Grade: {report['grade']}")
```

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

## See Also

- [Skills Framework README](../../README.md)
- [OpenSpec AGENTS.md](../../../../AGENTS.md)
