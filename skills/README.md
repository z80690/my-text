# AI Agent Skills Directory

This directory contains AI Agent Skills for the project, following a standardized structure for skill development and registration.

## Directory Structure

```
skills/
├── skills.json              # Central skill registry
├── README.md                # This file
├── schemas/
│   ├── skill-schema.json        # Individual skill schema
│   └── skill-registry-schema.json # Registry schema
├── examples/
│   └── hello_world/         # Example skill implementation
├── templates/
│   └── basic/               # Template for creating new skills
└── utils/
    └── __init__.py          # Shared utility functions
```

## Quick Start

### Creating a New Skill

1. **Copy the template**:
   ```bash
   cp -r templates/basic examples/my_new_skill
   ```

2. **Update skill.json**:
   ```json
   {
     "name": "my_new_skill",
     "version": "1.0.0",
     "description": "Description of my skill",
     "entrypoint": "handler.py",
     "permissions": []
   }
   ```

3. **Implement the handler** in `handler.py`:
   ```python
   def handle(input_data: dict) -> dict:
       # Your skill logic here
       return {"success": True, "data": {}}
   ```

4. **Register the skill** in `skills.json`:
   ```json
   {
     "name": "my_new_skill",
     "version": "1.0.0",
     "description": "Description of my skill",
     "category": "tools",
     "entrypoint": "examples/my_new_skill/handler.py",
     "permissions": [],
     "tags": ["utility"]
   }
   ```

### Using Utilities

```python
from skills.utils import validate_input, format_response, sanitize_input

def handle(input_data: dict) -> dict:
    # Validate input
    is_valid, error = validate_input(input_data, ["required_field"])
    if not is_valid:
        return format_response(False, error=error)

    # Sanitize input
    clean_data = sanitize_input(input_data, ["allowed_field"])

    # Process and return
    return format_response(True, data={"result": "success"})
```

## Skill Schema

Each skill must include a `skill.json` file with the following structure:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique skill identifier |
| `version` | string | Yes | Semantic version (x.y.z) |
| `description` | string | Yes | Human-readable description |
| `entrypoint` | string | Yes | Path to handler file |
| `permissions` | array | No | Required permissions |

## Categories

- **examples**: Reference implementations and tutorials
- **tools**: External tool integration skills
- **processors**: Data processing and transformation skills

## Best Practices

1. Keep skills focused and single-purpose
2. Use type hints for all function parameters
3. Return standardized responses using `format_response()`
4. Validate all inputs before processing
5. Document your skill in README.md

## See Also

- [OpenSpec AGENTS.md](../../AGENTS.md) for project guidelines
