# Project Overview

A full-stack application that provides data access to a knowledge base through Supabase integration. The project is designed to run as a serverless cloud function on Tencent Cloud, with a Python backend handling database queries and a frontend interface.

## Tech Stack

### Backend
- **Language**: Python 3.10
- **Framework**: Serverless Cloud Functions (Tencent Cloud SCF)
- **Database**: Supabase (PostgreSQL)
- **Key Libraries**:
  - `supabase==2.27.0` - Supabase Python client
  - `httpx==0.28.1` - Async HTTP client
  - `postgrest==2.27.0` - PostgREST client
  - `realtime==2.27.0` - Realtime subscriptions
  - `storage3==2.27.0` - Storage client
  - `supabase-auth==2.27.0` - Authentication
  - `supabase-functions==2.27.0` - Edge functions
  - `yarl==1.22.0` - URL parsing and handling
  - `httpcore==1.0.9` - HTTP core functionality
  - `h11==0.16.0` - HTTP/1.1 protocol implementation

### Frontend
- **Runtime**: Node.js
- **Current State**: Initial setup, awaiting implementation

### DevOps
- **Containerization**: Docker (Python 3.10-slim base image)
- **Deployment**: Tencent Cloud Serverless Cloud Functions
- **Port**: 9000 (Tencent Cloud SCF requirement)
- **Package Source**: Alibaba Cloud mirror for faster dependency installation in China

### Development Tools
- **LSP Server**: pylsp (Python Language Server Protocol)
- **Virtual Environment**: `my_clean_venv` (located at project root)
- **OpenCode Configuration**: `opencode.json` for AI-assisted development
- **IDE Support**: VSCode with debug configuration in `.vscode/launch.json`

## Project Structure

```
my-text/
├── backend/              # Backend Node.js setup (currently minimal)
│   ├── package.json
│   └── package-lock.json
├── frontend/             # Frontend setup
│   ├── package.json
│   └── package-lock.json
├── src/                  # Main Python application code
│   ├── index.py          # Main SCF handler for data queries
│   ├── requirements.txt  # Python dependencies
│   └── test_connectivity.py  # Connectivity testing suite
├── openspec/             # Project specification
│   └── project.md        # This file
├── Dockerfile            # Docker configuration
└── .vscode/              # IDE configuration
    └── launch.json
```

## Conventions

### Code Style
- **Encoding**: UTF-8 for all Python files
- **Type Hints**: Uses Python `typing` module for function signatures
- **Error Handling**: Try-except blocks with descriptive error messages
- **Comments**: Chinese language comments for code documentation
- **Indentation**: Standard 4-space indentation (PEP 8)

### Configuration Management
- **Environment Variables**: All sensitive data stored in environment variables
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_KEY`: Supabase API key (anon or service role)
  - `SUPABASE_JWT_SECRET`: JWT secret for token verification (auth specific)
  - `ACCESS_TOKEN_EXPIRY`: Access token expiration time in seconds (default: 3600)
  - `REFRESH_TOKEN_EXPIRY`: Refresh token expiration time in seconds (default: 604800)
  - `MIN_PASSWORD_LENGTH`: Minimum password length (default: 8)
- **No Hardcoded Secrets**: Never commit credentials to repository
- **Environment Template**: See `.env.example` for all required variables

### API Design
- **Handler Pattern**: Cloud function uses `main_handler(event, context)` entry point
- **Response Format**: HTTP response with statusCode, headers, and body
  ```python
  {
    'statusCode': 200,
    'headers': {'Content-Type': 'application/json'},
    'body': json.dumps(response_data, ensure_ascii=False)
  }
  ```
- **Database Operations**: Uses Supabase client for type-safe queries
  - Table: `knowledge_base`
  - Operations: `select()`, `limit()`, `execute()`

### Testing
- **Integration Tests**: Comprehensive test suite in `test_connectivity.py`
- **Test Categories**:
  1. Environment variable validation (`test_env_vars`)
  2. Supabase client connection (`test_supabase_connection`)
  3. Database query execution (`test_db_query`)
- **Test Functions**: Return dict with `test`, `status`, `message` keys
- **Flexible Execution**: Supports command-line arguments and environment variables
- **Exit Codes**: Returns 0 for success, 1 for failure
- **Test Result Format**:
  ```python
  {
    "test": "test_name",
    "status": "PASSED" | "FAILED",
    "message": "description"
  }
  ```

### Deployment
- **Docker Build**: Multi-stage build process using slim Python image
- **Package Mirrors**: Uses Alibaba Cloud PyPI mirror for China region
- **Port Exposure**: Container exposes port 9000 for SCF compatibility

### LSP and AI Integration
- **LSP Server**: pylsp with comprehensive plugins enabled
  - pycodestyle: Code style checking (max 120 characters)
  - pyflakes: Linting and error detection
  - mccabe: Complexity analysis (threshold: 15)
  - pydocstyle: Docstring convention (PEP 257)
  - jedi: Code completion, definition lookup, hover help, symbols
- **OpenCode AI Features**:
  - Context awareness with symbol resolution
  - Codebase navigation with import following
  - Intelligent query handling with definitions and examples
  - Real-time error checking and diagnostics

## Database Schema

### knowledge_base Table
- **Purpose**: Stores knowledge base entries for the application
- **Query Pattern**: Retrieves records with configurable limit
- **Example Query**:
  ```python
  supabase.table("knowledge_base").select("*").limit(5).execute()
  ```

## Development Workflow

### Local Development
1. **Virtual Environment Setup**:
   ```bash
   # Create virtual environment (if not exists)
   python -m venv my_clean_venv
   
   # Activate virtual environment
   # On Windows:
   my_clean_venv\Scripts\activate
   # On Unix/macOS:
   source my_clean_venv/bin/activate
   ```
2. Install dependencies: `pip install -r src/requirements.txt`
3. Set environment variables: `SUPABASE_URL` and `SUPABASE_KEY`
4. Run connectivity tests: `python src/test_connectivity.py --url <URL> --key <KEY>`
5. LSP Setup: The `opencode.json` configuration automatically detects the `my_clean_venv` virtual environment

### Docker Deployment
1. Build image: `docker build -t my-text .`
2. Run container with environment variables
3. Access service on port 9000

### Cloud Function Deployment
- Target platform: Tencent Cloud Serverless Cloud Functions (SCF)
- Entry point: `src/index.py::main_handler`
- Runtime: Python 3.10

## Security Considerations

- API keys should be stored securely (environment variables or secrets manager)
- Use read-only or appropriately scoped keys when possible
- Implement rate limiting in production
- Validate all input parameters
- Use HTTPS for all external communications

## Documentation

### Key Documentation Files
- **`AGENTS.md`**: Instructions for AI agents working in this codebase
  - Quick start commands for local development and Docker
  - Code conventions and style guidelines
  - Common tasks and debugging procedures
  - Deployment notes and architecture overview

- **`opencode.json`**: OpenCode AI integration configuration
  - LSP server configuration (pylsp)
  - Feature settings (completion, hover, diagnostics)
  - Workspace folder mappings (root, backend, frontend, src)
  - Virtual environment detection
  - AI agent context awareness settings

### Documentation Conventions
- Project specs: `openspec/` directory
- Agent instructions: `AGENTS.md` in root
- Chinese comments for Python code documentation
- README files should use English for broader accessibility
