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

This file provides instructions for AI agents working on this codebase.

## Quick Start

### Running the Application
```bash
# Install Python dependencies
pip install -r src/requirements.txt

# Set environment variables
set SUPABASE_URL=your_url_here
set SUPABASE_KEY=your_key_here

# Run connectivity tests
python src/test_connectivity.py --url %SUPABASE_URL% --key %SUPABASE_KEY%

# Or test with environment variables directly
python src/test_connectivity.py
```

### Docker Commands
```bash
# Build Docker image
docker build -t my-text .

# Run container with environment variables
docker run -p 9000:9000 -e SUPABASE_URL=your_url -e SUPABASE_KEY=your_key my-text
```

## Development Commands

### Testing
```bash
# Run full connectivity test suite
python src/test_connectivity.py

# Run with command line arguments
python src/test_connectivity.py --url https://your-project.supabase.co --key your_anon_key

# Test specific functions (in Python REPL)
python -c "from test_connectivity import run_connectivity_tests; print(run_connectivity_tests())"
```

### Dependencies
```bash
# Update requirements.txt
pip freeze > src/requirements.txt

# Install specific packages
pip install supabase==2.27.0 httpx==0.28.1
```

## Key Files

### Core Application Files
- `src/index.py` - Main cloud function handler (SCF entry point)
- `src/test_connectivity.py` - Comprehensive testing suite with multiple test functions
- `src/requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration for deployment

### Configuration Files
- `.vscode/launch.json` - VSCode debug configuration
- `backend/package.json` - Backend Node.js setup (minimal)
- `frontend/package.json` - Frontend Node.js setup (minimal)

## Code Conventions

### Python
- **Encoding**: UTF-8 (always include `# -*- coding: utf-8 -*-` or `# -*- coding: utf8 -*-`)
- **Type Hints**: Use `typing` module for function signatures
  ```python
  def main_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
  ```
- **Error Handling**: Always wrap database operations in try-except blocks
- **Response Format**: Cloud functions must return dict with statusCode, headers, body
- **Environment Variables**: Never hardcode credentials; always use `os.getenv()`
- **Comments**: Use Chinese comments for code documentation

### Database Operations
- Use Supabase client: `from supabase import create_client, Client`
- Query pattern: `supabase.table("table_name").select("*").limit(n).execute()`
- Always check if response has data before processing

### Testing
- Write tests in `test_connectivity.py` following existing patterns
- Test functions should return dict with: `test`, `status`, `message`
- Status values: "PASSED" or "FAILED"
- Provide optional parameters for URL and key to support flexible testing

## Common Tasks

### Adding a New Cloud Function
1. Create new function in `src/` directory
2. Use `main_handler(event, context)` signature
3. Return dict with `statusCode`, `headers`, `body`
4. Add tests to `test_connectivity.py` if database operations are involved

### Updating Dependencies
1. Update `src/requirements.txt`
2. Test locally: `python src/test_connectivity.py`
3. Rebuild Docker image to verify container compatibility
4. Update this file if new commands are needed

### Adding Database Tables
1. Create table in Supabase dashboard
2. Update queries in `src/index.py`
3. Add test cases in `src/test_connectivity.py`
4. Update database schema section in `openspec/project.md`

### Debugging
- Use VSCode launch configuration in `.vscode/launch.json`
- Add print statements with `[INFO]`, `[WARNING]`, or `[ERROR]` prefixes
- Run `test_connectivity.py` for isolated testing
- Check environment variables are set: `echo %SUPABASE_URL%`

## Linting & Code Quality

**Note**: No linting or typecheck commands are currently configured in this project. 

When adding Python linting/testing tools in the future, document the commands here:
```bash
# Example (when configured):
# python -m flake8 src/
# python -m mypy src/
# pytest tests/
```

## Deployment Notes

### Tencent Cloud SCF
- Entry point: `index.main_handler`
- Runtime: Python 3.10
- Port: 9000 (SCF requirement)
- Environment variables: Set SUPABASE_URL and SUPABASE_KEY in SCF console

### Docker
- Base image: `python:3.10-slim` (via DaoCloud mirror)
- Exposed port: 9000
- Health check: Run `test_connectivity.py` on container startup

## Important Reminders

1. **Never commit secrets**: Use environment variables for SUPABASE_URL and SUPABASE_KEY
2. **Test before deploying**: Always run `test_connectivity.py` before pushing changes
3. **Update documentation**: Keep `openspec/project.md` in sync with code changes
4. **Encoding matters**: Ensure all Python files use UTF-8 encoding
5. **Type hints required**: Use type hints for all function parameters and return values
6. **Error handling**: Always handle exceptions in cloud function handlers
7. **Response format**: Cloud functions must return proper HTTP response dict

## Architecture Overview

```
Client Request
    ↓
Tencent Cloud SCF (Port 9000)
    ↓
Python: src/index.py::main_handler
    ↓
Supabase Client
    ↓
Supabase Database (knowledge_base table)
    ↓
Response JSON
```

## Database Access

### Current Table
- **knowledge_base**: Stores knowledge base entries
- **Operations**: SELECT queries with limit
- **Example**: 
  ```python
  supabase.table("knowledge_base").select("*").limit(5).execute()
  ```

### Adding New Tables
1. Create in Supabase dashboard
2. Update queries in `src/index.py`
3. Add tests to `src/test_connectivity.py`
4. Document in `openspec/project.md`
