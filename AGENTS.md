<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md

Instructions for AI agents working in this codebase.

## Quick Start

```bash
# Install dependencies
pip install -r src/requirements.txt

# Set environment variables
set SUPABASE_URL=your_url_here
set SUPABASE_KEY=your_key_here

# Run connectivity tests
python src/test_connectivity.py

# Docker build and run
docker build -t my-text .
docker run -p 9000:9000 -e SUPABASE_URL=your_url -e SUPABASE_KEY=your_key my-text
```

## Testing Commands

```bash
# Run full test suite
python src/test_connectivity.py
python src/test_database_schema.py

# Run single test function (in Python REPL)
python -c "from src.test_connectivity import test_env_vars; print(test_env_vars())"
python -c "from src.test_connectivity import test_supabase_connection; print(test_supabase_connection())"
python -c "from src.test_connectivity import test_db_query; print(test_db_query())"

# Run with custom URL/Key
python src/test_connectivity.py --url https://your-project.supabase.co --key your_key

# Run specific database schema test
python -c "from src.test_database_schema import test_table_exists; print(test_table_exists())"
```

## Code Style Guidelines

### Python File Format
- **Encoding**: Always include `# -*- coding: utf-8 -*-` or `# -*- coding: utf8 -*-` at line 1
- **Imports**: Organize in order: stdlib → third-party → local (separated by blank lines)
- **Line Length**: Maximum 88 characters (follow PEP 8)
- **Indentation**: 4 spaces, no tabs

### Type Hints
- Required for all function parameters and return values
- Use `typing` module: `Dict[str, Any]`, `Optional[str]`, etc.
- Example:
  ```python
  def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
      pass
  ```

### Naming Conventions
- Functions/Variables: `snake_case` (e.g., `test_env_vars`, `supabase_url`)
- Classes: `PascalCase` (e.g., `Client`, `User`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `SUPABASE_URL`)
- Private functions: `_leading_underscore`

### Error Handling
- Wrap all database operations in try-except blocks
- Log errors with `[ERROR]` prefix
- Return HTTP responses with appropriate status codes (400, 500)
- Example:
  ```python
  try:
      response = supabase.table("table").select("*").execute()
  except Exception as e:
      error_msg = f"Error: {str(e)}"
      print(f"[ERROR] {error_msg}")
      return {"statusCode": 500, "body": json.dumps({"error": error_msg})}
  ```

### Logging
- Use prefixes: `[INFO]`, `[WARNING]`, `[ERROR]`
- Example:
  ```python
  print("[INFO] Starting database query")
  print("[WARNING] Cache miss, fetching from database")
  print("[ERROR] Failed to connect to Supabase")
  ```

### Cloud Function Response Format
- Must return dict with: `statusCode`, `headers`, `body`
- Headers should include CORS headers
- Body must be JSON string
- Example:
  ```python
  return {
      "statusCode": 200,
      "headers": {"Content-Type": "application/json"},
      "body": json.dumps({"success": True, "data": result})
  }
  ```

### Comments
- Use Chinese comments for code documentation
- Docstrings for all public functions
- Keep comments concise and relevant

### Database Operations
- Use Supabase client: `from supabase import create_client, Client`
- Query pattern: `supabase.table("table_name").select("*").limit(n).execute()`
- Always check if response has data before processing

### Test Functions
- Return dict with keys: `test`, `status`, `message`
- Status values: `"PASSED"` or `"FAILED"`
- Accept optional parameters for URL and key
- Example:
  ```python
  def test_connection(supabase_url: Optional[str] = None) -> Dict[str, Any]:
      try:
          return {"test": "connection", "status": "PASSED", "message": "Success"}
      except Exception as e:
          return {"test": "connection", "status": "FAILED", "message": str(e)}
  ```

## Common Tasks

### Adding a New Test
1. Create test function in `src/test_connectivity.py` or `src/test_database_schema.py`
2. Follow naming pattern: `test_<feature>()`
3. Return dict with `test`, `status`, `message` keys
4. Add to test list in `run_connectivity_tests()` or `run_all_tests()`

### Adding a New Cloud Function
1. Create function in `src/` directory
2. Use `main_handler(event, context)` signature
3. Return proper HTTP response dict
4. Add tests in test files if database operations involved

### Updating Dependencies
1. Edit `src/requirements.txt`
2. Test locally: `python src/test_connectivity.py`
3. Rebuild Docker: `docker build -t my-text .`

## Linting & Code Quality

No linting commands currently configured. When adding tools:
```bash
# Example future commands:
python -m flake8 src/
python -m mypy src/
```

## Deployment

### Tencent Cloud SCF
- Entry point: `index.main_handler`
- Runtime: Python 3.10
- Port: 9000
- Environment variables: SUPABASE_URL, SUPABASE_KEY

### Docker
- Base image: `python:3.10-slim` (DaoCloud mirror)
- Exposed port: 9000
- Health check: Run `test_connectivity.py` on startup

## Important Reminders

1. Never commit secrets - use environment variables
2. Test before deploying - always run test scripts
3. UTF-8 encoding required for all Python files
4. Type hints required for all functions
5. Error handling required in cloud functions
6. Chinese comments for documentation
7. Return proper HTTP response format

## Architecture

```
Client Request → Tencent Cloud SCF (Port 9000) → Python: src/index.py
→ Supabase Client → Supabase Database → Response JSON
```
