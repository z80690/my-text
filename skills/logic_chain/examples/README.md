# Logic Chain Examples

This directory contains example chains demonstrating the Logic Chain Framework.

## Example 1: User Registration Flow

**File**: `example_chain.py` and `example_chain.json`

Demonstrates IF/ELSE branching logic:

```
START
  ↓
Validate Email (Condition)
  ↓
IF Email Valid → Check User Exists → IF User Not Exists → Create User → END_SUCCESS
  ↓ (false)        ↓ (found)        ↓ (false)
Reject Email    IF User Found     Reject User Exists
                → END_ERROR
```

### Condition Syntax

| Pattern | Example | Description |
|---------|---------|-------------|
| `$var == value` | `$age == 18` | Equality check |
| `$var != value` | `$status != 'banned'` | Inequality check |
| `$var > N` | `$score > 100` | Greater than |
| `$var matches pattern` | `$email matches .*@.*` | Regex match |
| `$var exists` | `$optional_field exists` | Variable exists |

### Running the Example

```python
import asyncio
from skills.logic_chain.examples.example_chain import run_example

asyncio.run(run_example())
```

## Chain Structure

### Node Types

1. **Skill Node** - Executes a skill handler
2. **Condition Node** - Evaluates a condition, stores boolean result
3. **IfElse Node** - Routes to true/false branches based on condition
4. **Parallel Node** - Executes multiple nodes concurrently

### Metadata

Each node can have `metadata.next` for flow control:

```json
{
  "metadata": {
    "next": {
      "default": "next_node_id",
      "true": "branch_true_node",
      "false": "branch_false_node"
    }
  }
}
```
