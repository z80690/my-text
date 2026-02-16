# Code Quality Check Runner Skill

A skill that runs comprehensive code quality checks for the project including ESLint, Prettier, and Pylint analysis.

## Overview

This skill executes the project's quality check workflow:

- **ESLint**: JavaScript/TypeScript linting for code quality and style
- **Prettier**: Code formatting verification
- **Pylint**: Python code analysis and quality rating

## Usage

```python
from skills.examples.code_quality_check_runner.handler import handle

result = handle({})

if result["success"]:
    report = result["data"]
    print(f"Status: {report['status']}")
    print(f"Total Issues: {report['total_issues']}")
    for rec in report['recommendations']:
        print(f"  - {rec}")
else:
    print(f"Error: {result['error']}")
```

### Command Line

```bash
cd skills/examples/code_quality_check_runner
python handler.py
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `check_type` | string | No | Specific check to run: 'eslint', 'prettier', 'pylint', or None for all |

## Output Format

```json
{
  "success": true,
  "data": {
    "status": "passed" | "failed",
    "summary": {
      "eslint": {
        "errors": 0,
        "warnings": 0
      },
      "prettier": {
        "passed": true,
        "issues": 0
      },
      "pylint": {
        "rating": "10.00/10",
        "issues": 0,
        "errors": 0,
        "warnings": 0,
        "conventions": 0,
        "refactors": 0
      }
    },
    "total_issues": 0,
    "recommendations": [
      "Run 'npm run lint:fix' to auto-fix ESLint issues",
      "Run 'npm run format' to fix formatting issues"
    ]
  },
  "error": null
}
```

## Quality Tools

### ESLint

Checks JavaScript/TypeScript code for:
- Code quality issues
- Best practices violations
- Potential bugs
- Style inconsistencies

**Commands:**
- Check: `npm run lint`
- Auto-fix: `npm run lint:fix`

### Prettier

Verifies code formatting against project standards:
- Consistent indentation
- Proper line length
- Quote styles
- Spacing and alignment

**Commands:**
- Check: `npm run format:check`
- Auto-fix: `npm run format`

### Pylint

Analyzes Python code for:
- Code quality rating (0-10)
- Errors, warnings, and conventions
- Code complexity metrics
- Refactoring suggestions

**Commands:**
- Check: `npm run lint:python`
- Auto-fix: `npm run lint:python:fix`

## Status Indicators

| Status | Description |
|--------|-------------|
| **passed** | All quality checks passed with no issues |
| **failed** | One or more quality checks found issues |

## Examples

### Full Quality Check

```python
from skills.examples.code_quality_check_runner.handler import handle

result = handle({})

if result["success"]:
    data = result["data"]
    print(f"Overall Status: {data['status']}")
    print(f"ESLint: {data['summary']['eslint']['errors']} errors, {data['summary']['eslint']['warnings']} warnings")
    print(f"Prettier: {'PASSED' if data['summary']['prettier']['passed'] else 'FAILED'}")
    print(f"Pylint: {data['summary']['pylint']['rating']}")
    print(f"\nRecommendations:")
    for rec in data['recommendations']:
        print(f"  - {rec}")
```

### Quick Status Check

```python
from skills.examples.code_quality_check_runner.handler import handle

result = handle({})

if result["success"]:
    status = result["data"]["status"]
    issues = result["data"]["total_issues"]
    if status == "passed":
        print("✓ All quality checks passed!")
    else:
        print(f"✗ {issues} issue(s) found - see recommendations for fixes")
```

### CI/CD Integration

```python
from skills.examples.code_quality_check_runner.handler import handle
import json

result = handle({})

if result["success"]:
    data = result["data"]
    if data["status"] == "passed":
        print("Quality gates passed")
        exit(0)
    else:
        print("Quality gates failed:")
        for rec in data["recommendations"]:
            print(f"  - {rec}")
        exit(1)
```

## Integration with Logic Chain

```python
from skills.logic_chain import ChainExecutor, SkillNode

executor = ChainExecutor()
executor.register_node(SkillNode(
    node_id="check_quality",
    name="Check Code Quality",
    skill_name="code_quality_check_runner",
    parameters={},
    output_key="quality_report",
))

context = await executor.execute_chain(
    chain_name="pre_commit",
    start_node_id="check_quality",
    user_data={},
)

report = context.get("quality_report")
if report["status"] == "failed":
    print("Quality checks failed!")
    for rec in report["recommendations"]:
        print(f"  - {rec}")
```

## Requirements

- Node.js and npm (for ESLint and Prettier)
- Python 3.8+ (for Pylint)
- Project dependencies installed

## See Also

- [Skills Framework README](../../README.md)
- [OpenSpec AGENTS.md](../../../../AGENTS.md)
- [Backend Quality Commands](../../../../backend/package.json)
