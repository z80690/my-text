# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Development Commands

### Local Development

```bash
# Activate virtual environment (Windows)
my_clean_venv\Scripts\activate

# Activate virtual environment (Unix/macOS)
source my_clean_venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt

# Install development dependencies (includes code quality tools)
pip install -r src/requirements-dev.txt

# Run the main application
cd src && python main.py

# Run cloud function locally
cd src && python index.py
```

### Testing

```bash
# Run all connectivity tests
python src/test_connectivity.py --url <SUPABASE_URL> --key <SUPABASE_KEY>

# Run specific test functions
python -c "from src.test_connectivity import test_env_vars; print(test_env_vars())"
python -c "from src.test_connectivity import test_supabase_connection; print(test_supabase_connection())"
python -c "from src.test_connectivity import test_db_query; print(test_db_query())"

# Test authentication system
python src/test_auth_system.py

# Test database schema
python src/test_database_schema.py

# Test roles and permissions
python src/test_roles_and_permissions.py

# Test AI function calling
python src/test_function_calling.py
```

### Dependency Management

**View installed packages**:
```bash
pip list
```

**View dependency tree**:
```bash
pipdeptree
```

**Check for conflicts**:
```bash
pipdeptree | grep -i "possibly conflicting"
```

**Check for outdated packages**:
```bash
pip list --outdated
```

**Run security audit**:
```bash
pip-audit --desc
```

**Update dependencies**:
```bash
# Update all production dependencies
pip install --upgrade -r src/requirements.txt

# Update all development dependencies
pip install --upgrade -r src/requirements-dev.txt
```

> Detailed dependency management guide: [DEPENDENCIES.md](../DEPENDENCIES.md)

### CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline (`.github/workflows/ci-cd-pipeline.yml`):

**Jobs**:
1. **Security Scan** - Dependency audit, vulnerability checking, conflict detection
2. **Install** - Dependency installation with caching
3. **Test** - Connectivity, authentication, and database schema tests
4. **Code Quality** - Pylint, MyPy, Black, isort checks
5. **OpenSpec Validation** - Validate all specifications
6. **Build** - Docker image build and testing
7. **Deploy** - Deploy to Tencent Cloud SCF (main branch only)

**Triggers**:
- Push to main/develop branches
- Pull requests
- Daily security scans (UTC 2:00)
- Manual trigger (with option to skip tests)

For more details, see [CHANGELOG.md](../CHANGELOG.md).

### Code Quality

```bash
# From the backend directory (contains devDependencies)
cd backend

# Run ESLint
npm run lint

# Fix ESLint issues
npm run lint:fix

# Format code with Prettier
npm run format

# Check formatting
npm run format:check

# Run Python linting
npm run lint:python

# Run full quality check
npm run quality:check

# Fix all quality issues
npm run quality:fix
```

### Docker Deployment

```bash
# Build Docker image
docker build -t my-text .

# Run container with environment variables
docker run -p 9000:9000 \
  -e SUPABASE_URL=your_url \
  -e SUPABASE_KEY=your_key \
  -e SUPABASE_JWT_SECRET=your_jwt \
  -e ZHIPU_API_KEY=your_zhipu_key \
  my-text

# Run container in development mode
docker run -p 9000:9000 \
  --env-file .env \
  -e ENVIRONMENT=development \
  my-text
```

### OpenSpec Workflow Commands

```bash
# From openspec directory
cd openspec

# List all specifications
openspec list --specs

# List active changes
openspec list

# Show details of a spec or change
openspec show <spec-id> --type spec
openspec show <change-id>

# Validate a change proposal
openspec validate <change-id> --strict

# Archive a completed change
openspec archive <change-id> --yes

# Initialize OpenSpec in a new path
openspec init [path]

# Update instruction files
openspec update [path]

# Full-text search for requirements and scenarios
rg -n "Requirement:|Scenario:" openspec/specs

# Show all specs in JSON format
openspec spec list --long --json
```

## High-Level Architecture

### Project Overview

This is a full-stack application built with spec-driven development using OpenSpec. The project provides an AI-powered backend service with authentication, knowledge base queries, and AI capabilities through ZhipuAI integration.

### Core Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    API Layer (src/)                       │
│  ├─ main.py              # Main API router               │
│  ├─ index.py             # SCF entry point               │
│  ├─ auth_api.py          # Auth endpoint handler         │
│  ├─ ai_api.py           # AI endpoint handler           │
│  └─ skill_handler.py     # Skill execution system        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Business Logic Layer (src/auth/)             │
│  ├─ Authentication        # JWT token management          │
│  ├─ User Management     # User profile operations       │
│  ├─ Authorization       # Role-based access control      │
│  └─ Security           # Encryption and validation      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│               Data Layer (Supabase)                       │
│  ├─ auth.users            # Supabase Auth users        │
│  ├─ public.user_profiles   # Extended user data         │
│  ├─ public.user_roles     # Role definitions           │
│  └─ public.user_role_assignments  # Role mappings     │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Patterns

#### 1. Spec-Driven Development (OpenSpec)

The project uses OpenSpec for managing specifications and changes:

- **specs/**: Current truth - what IS built (production-ready features)
  - `authentication/spec.md`: Auth and JWT token management
  - `user-auth/spec.md`: User registration, login, profile management
  - `user-profile/spec.md`: Profile CRUD operations with RLS

- **changes/**: Proposals - what SHOULD change (in-progress features)
  - Each change has: `proposal.md`, `tasks.md`, optional `design.md`, and spec deltas

- **changes/archive/**: Completed changes organized by date (YYYY-MM-DD-change-name)

**Workflow**: Always create a change proposal before implementing features. Use `openspec validate --strict` before requesting approval.

#### 2. Serverless Cloud Functions (Tencent Cloud SCF)

- **Entry Point**: `src/index.py::main_handler(event, context)`
- **Port**: 9000 (Tencent Cloud requirement)
- **Runtime**: Python 3.10
- **Response Format**: Standardized HTTP response with statusCode, headers, and JSON body

#### 3. Supabase Integration

**Authentication**: Uses Supabase Auth for user management
- User registration and login
- JWT token generation and validation
- Email verification
- Password reset flow

**Database**: PostgreSQL with Row-Level Security (RLS)
- `auth.users`: Built-in Supabase users table
- `public.user_profiles`: Extended user profile data
- `public.user_roles`: Role definitions and permissions
- `public.user_role_assignments`: Many-to-many user-role relationships

**RLS Policies**: All tables enforce access control
- Users can only access their own profile data
- Role-based permissions for admin/moderator access
- Automatic triggers for profile creation on user registration

#### 4. AI Integration (ZhipuAI)

**Service Layer**: `src/zhipu_service.py` (minimal, extends as needed)
**Handler**: `src/ai_api.py` processes AI requests
**Capabilities**: Function calling, chat completions (configurable via ZHIPU_MODEL)

**Security**:
- API keys stored in environment variables
- Request validation and rate limiting
- Error handling with user-friendly messages

#### 5. Skill System

**Handler**: `src/skill_handler.py` manages skill execution
**Structure**: Modular skill system in `skills/` directory
**Capabilities**: Extensible skill framework for AI-powered operations

### Directory Structure

```
my-text/
├── src/                        # Main Python application
│   ├── main.py                 # FastAPI-like router
│   ├── index.py                # SCF entry point (event handler)
│   ├── ai_api.py              # AI API endpoints
│   ├── auth_api.py            # Auth API endpoints
│   ├── functions.py           # Business logic functions
│   ├── skill_handler.py       # Skill execution engine
│   ├── security.py           # Security utilities
│   ├── auth/                # Authentication module
│   ├── test_*.py           # Test files
│   ├── requirements.txt      # Python dependencies
│   ├── .pylintrc          # Pylint configuration
│   └── mypy.ini           # MyPy configuration
│
├── backend/                   # Node.js tooling
│   └── package.json        # ESLint, Prettier, OpenSpec scripts
│
├── frontend/                  # Frontend (placeholder, minimal setup)
│
├── openspec/                 # OpenSpec specification system
│   ├── project.md           # Project conventions and schema
│   ├── AGENTS.md           # AI agent instructions
│   ├── GETTING_STARTED.md   # OpenAPI getting started guide
│   ├── specs/              # Current specifications
│   │   ├── authentication/
│   │   ├── user-auth/
│   │   └── user-profile/
│   ├── changes/            # Active change proposals
│   │   └── archive/      # Completed changes
│   └── workflows/         # Workflow configurations
│
├── skills/                   # Skill modules
├── utils/                    # Utility functions
├── templates/                # Template files
├── knowledge_graph_project/   # Knowledge graph subproject
├── openapi/                  # OpenAPI specifications
├── my_clean_venv/           # Python virtual environment
├── Dockerfile               # Docker configuration
├── .env.example            # Environment variables template
├── .env                   # Actual environment (not in git)
├── AGENTS.md              # AI agent instructions (legacy, use openspec/AGENTS.md)
└── README.md              # Project overview
```

### Data Flow

#### Authentication Flow

1. User registers via `/auth/register`
2. Supabase creates user in `auth.users`
3. Trigger creates profile in `public.user_profiles`
4. User logs in via `/auth/login`
5. Supabase validates credentials and issues JWT tokens
6. Client includes `Authorization: Bearer <token>` header
7. Middleware validates token and extracts user context
8. Protected endpoints check RLS policies

#### AI Request Flow

1. Client sends request to `/api/ai/*` with authentication
2. `ai_api.py` validates request and token
3. `skill_handler.py` routes to appropriate skill
4. ZhipuAI API is called with function definitions
5. Response is processed and returned as JSON

#### Knowledge Base Query Flow

1. Client queries `/` with optional parameters
2. `functions.py` builds Supabase query
3. RLS policies enforce data access
4. Results are returned in standardized JSON format

### Environment Configuration

**Required Variables**:
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_KEY`: Supabase API key (anon or service role)
- `SUPABASE_JWT_SECRET`: JWT secret for token verification

**Optional Variables**:
- `ZHIPU_API_KEY`: ZhipuAI API key
- `ZHIPU_MODEL`: AI model name (default: glm-4)
- `ACCESS_TOKEN_EXPIRY`: Access token expiration in seconds (default: 3600)
- `REFRESH_TOKEN_EXPIRY`: Refresh token expiration in seconds (default: 604800)
- `MIN_PASSWORD_LENGTH`: Minimum password length (default: 8)
- `CORS_ORIGINS`: Comma-separated allowed origins
- `RATE_LIMIT_PER_MINUTE`: Request rate limit (default: 60)

### Code Conventions

**Python Style**:
- UTF-8 encoding
- 4-space indentation
- Type hints required for all functions
- snake_case for functions/variables
- PascalCase for classes
- UPPER_SNAKE_CASE for constants
- Chinese language comments for code documentation

**Error Handling**:
- Try-except blocks with descriptive messages
- Standardized error response format:
  ```python
  return {
      "statusCode": error_code,
      "headers": {"Content-Type": "application/json"},
      "body": json.dumps({
          "success": False,
          "error": {"code": error_code, "message": description}
      })
  }
  ```

**Logging**:
- Prefix with level: `[INFO]`, `[WARNING]`, `[ERROR]`
- Sensitive data masking in logs
- Structured logging for debugging

**Security**:
- Never commit credentials
- Use environment variables for secrets
- Validate all input parameters
- Implement rate limiting
- Use HTTPS for external communications

### Key Files Reference

- `src/main.py:1` - Main API router and request handling
- `src/index.py:1` - Tencent Cloud SCF entry point
- `src/auth_api.py:1` - Authentication endpoint handlers
- `src/ai_api.py:1` - AI API endpoint handlers
- `src/functions.py:1` - Business logic functions
- `src/skill_handler.py:1` - Skill execution system
- `src/security.py:1` - Security utilities and encryption
- `openspec/project.md:1` - Project schema and conventions
- `openspec/AGENTS.md:1` - Detailed OpenSpec workflow instructions

### Testing Strategy

**Unit Tests**: Individual function testing with isolated dependencies
**Integration Tests**: Database connectivity and API endpoint testing
**Auth Tests**: Token generation, validation, and RLS policy testing
**Schema Tests**: Database structure and constraint validation

**Test Execution**: Run `python src/test_connectivity.py` for full suite

### Deployment Notes

**Docker**: Multi-stage build using Python 3.10-slim, Alibaba Cloud mirror for packages
**Tencent Cloud SCF**: Python 3.10 runtime, port 9000, entry point `index.main_handler`
**Environment**: Set all required variables in deployment platform or `.env` file

### When to Use OpenSpec

**Create a change proposal when**:
- Adding new features or functionality
- Making breaking changes (API, schema)
- Changing architecture or patterns
- Optimizing performance (changes behavior)
- Updating security patterns

**Skip proposal for**:
- Bug fixes (restore intended behavior)
- Typos, formatting, comments
- Dependency updates (non-breaking)
- Configuration changes
- Tests for existing behavior

### Quick Reference

**OpenSpec Commands**:
- `openspec list` - View active changes
- `openspec validate <id> --strict` - Validate proposal
- `openspec archive <id> --yes` - Mark complete
- `openspec spec list --long` - View all specs

**Common Tasks**:
- Create change: Scaffold `proposal.md`, `tasks.md`, spec deltas
- Implement: Read proposal → tasks.md → implement sequentially
- Archive: Move changes to `archive/YYYY-MM-DD-[name]/`

**Spec Format**:
- Requirements with `### Requirement:` header
- Scenarios with `#### Scenario:` header (4 hashtags required)
- Delta operations: `## ADDED|MODIFIED|REMOVED Requirements`

Remember: Specs are truth. Changes are proposals. Keep them in sync.
