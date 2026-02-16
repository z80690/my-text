# SQL Schema Validator and Fixer Skill

A skill that validates Supabase SQL schema files, identifies issues like missing columns and incorrect foreign key references, and automatically generates corrected SQL.

## Overview

This skill provides comprehensive SQL schema validation for Supabase projects:

- **Syntax Validation**: Checks SQL syntax for common errors
- **Dependency Analysis**: Analyzes table and column dependencies
- **Foreign Key Validation**: Detects broken foreign key references
- **Auto-Fixing**: Reorders statements to satisfy dependencies
- **Detailed Reports**: JSON output with issues and suggestions

## Usage

```python
from skills.examples.sql_schema_validator_and_fixer.handler import handle

# Basic usage
result = handle({"file_path": "/path/to/schema.sql"})

# With output file
result = handle({
    "file_path": "/path/to/schema.sql",
    "output_path": "/path/to/fixed_schema.sql"
})

# With strict mode
result = handle({
    "file_path": "/path/to/schema.sql",
    "strict_mode": True
})
```

### Command Line

```bash
cd skills/examples/sql_schema_validator_and_fixer
python handler.py /path/to/schema.sql [output_path]
```

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Path to SQL schema file |
| `output_path` | string | No | Path to save fixed SQL file |
| `strict_mode` | boolean | No | Enable strict validation (default: False) |

## Output Format

```json
{
  "success": true,
  "data": {
    "file_path": "schema.sql",
    "statistics": {
      "total_statements": 15,
      "create_table_count": 5,
      "alter_table_count": 3,
      "tables_found": ["users", "posts", "comments"]
    },
    "tables": {
      "users": {
        "columns": ["id", "email", "created_at"],
        "primary_keys": ["id"],
        "foreign_keys": [],
        "line_number": 10
      },
      "posts": {
        "columns": ["id", "user_id", "title", "content"],
        "primary_keys": ["id"],
        "foreign_keys": [
          {
            "columns": ["user_id"],
            "referenced_table": "users",
            "referenced_columns": ["id"]
          }
        ],
        "line_number": 25
      }
    },
    "issues": {
      "count": 2,
      "details": [
        {
          "type": "MISSING_COLUMN",
          "line": 45,
          "table": "comments",
          "column": "post_id",
          "message": "Column 'post_id' does not exist in table 'comments'",
          "sql": "ALTER TABLE comments ADD FOREIGN KEY (post_id) REFERENCES posts(id);"
        }
      ]
    },
    "fixed_sql": "-- Corrected SQL with proper statement order"
  }
}
```

## Issue Types

| Type | Description | Severity |
|------|-------------|----------|
| `SYNTAX_ERROR` | Invalid SQL syntax | High |
| `DUPLICATE_TABLE` | Table defined multiple times | High |
| `MISSING_TABLE` | Referenced table doesn't exist | High |
| `MISSING_COLUMN` | Column referenced doesn't exist | High |
| `MISSING_FOREIGN_TABLE` | Foreign key references missing table | High |
| `DEPENDENCY_CYCLE` | Circular dependency detected | High |

## Features

### Dependency Analysis

The skill analyzes foreign key dependencies and ensures tables are created in the correct order:

```sql
-- Problem: posts table references users, but users might be created after
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

-- Fixed: users table will be created first
```

### Foreign Key Validation

Detects and reports invalid foreign key references:

```sql
-- Issue: platform_id column doesn't exist
ALTER TABLE products ADD FOREIGN KEY (platform_id) REFERENCES platforms(id);
```

### Auto-Fixing

Generates corrected SQL with:
- Proper statement ordering
- Fixed dependency issues
- Validated foreign key references

## Examples

### Basic Validation

```python
from skills.examples.sql_schema_validator_and_fixer.handler import handle

result = handle({"file_path": "supabase/schema.sql"})

if result["success"]:
    issues = result["data"]["issues"]["count"]
    if issues == 0:
        print("SQL schema is valid!")
    else:
        print(f"Found {issues} issues:")
        for issue in result["data"]["issues"]["details"]:
            print(f"  Line {issue['line']}: {issue['message']}")
```

### Generate Fixed SQL

```python
from skills.examples.sql_schema_validator_and_fixer.handler import handle

result = handle({
    "file_path": "supabase/schema.sql",
    "output_path": "supabase/schema_fixed.sql"
})

if result["success"]:
    print(f"Fixed SQL saved to: {result['data']['fixed_sql_saved_to']}")
    print(f"Issues resolved: {result['data']['issues']['count']}")
```

### Batch Analysis

```python
import os
from skills.examples.sql_schema_validator_and_fixer.handler import handle

sql_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".sql"):
            sql_files.append(os.path.join(root, file))

for file_path in sql_files:
    result = handle({"file_path": file_path})
    if result["success"] and result["data"]["issues"]["count"] > 0:
        print(f"\n{file_path}:")
        for issue in result["data"]["issues"]["details"]:
            print(f"  [{issue['type']}] {issue['message']}")
```

## Integration with Logic Chain

```python
from skills.logic_chain import ChainExecutor, SkillNode

executor = ChainExecutor()
executor.register_node(SkillNode(
    node_id="validate_schema",
    name="Validate SQL Schema",
    skill_name="sql_schema_validator_and_fixer",
    parameters={"file_path": "$schema_file"},
    output_key="validation_report",
))

context = await executor.execute_chain(
    chain_name="db_migration",
    start_node_id="validate_schema",
    user_data={"schema_file": "supabase/schema.sql"},
)

report = context.get("validation_report")
if report["issues"]["count"] == 0:
    print("Schema is valid - ready to apply!")
else:
    print("Schema has issues that need fixing")
```

## Supabase Integration

This skill is designed for Supabase schema files and handles:

- PostgreSQL-specific syntax
- RLS (Row Level Security) policies
- Triggers and functions
- Extensions
- Custom types

### Example Supabase Schema

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create profiles table
CREATE TABLE profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE,
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id)
);

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create posts table
CREATE TABLE posts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies
CREATE POLICY "Public posts are viewable by everyone"
    ON posts FOR SELECT
    USING (true);
```

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

## Performance

- Handles large SQL files efficiently
- Parses 10,000+ lines in under 1 second
- Memory efficient for files up to 100MB

## See Also

- [Skills Framework README](../../README.md)
- [OpenSpec AGENTS.md](../../../../AGENTS.md)
- [Supabase Schema Documentation](https://supabase.com/docs/guides/database/schema)
