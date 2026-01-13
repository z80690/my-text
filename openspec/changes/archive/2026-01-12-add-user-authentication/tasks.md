## 1. Database Schema Setup
- [x] 1.1 Create Supabase Auth configuration in project
- [x] 1.2 Design user profile table schema (extends Supabase Auth users)
- [x] 1.3 Create database migration for user profiles
- [x] 1.4 Set up Row Level Security (RLS) policies for user data
- [x] 1.5 Test database schema and RLS policies

## 2. Environment Configuration
- [x] 2.1 Add SUPABASE_JWT_SECRET to environment variables
- [x] 2.2 Update Dockerfile with new environment variables
- [x] 2.3 Update AGENTS.md with authentication configuration
- [x] 2.4 Document environment variable requirements in openspec/project.md

## 3. Backend Authentication Implementation
- [x] 3.1 Create `src/auth/` directory for auth-related code
- [x] 3.2 Implement user registration endpoint (`POST /auth/register`)
- [x] 3.3 Implement user login endpoint (`POST /auth/login`)
- [x] 3.4 Implement token refresh endpoint (`POST /auth/refresh`)
- [x] 3.5 Implement user logout endpoint (`POST /auth/logout`)
- [x] 3.6 Implement password reset initiation endpoint (`POST /auth/password/reset`)
- [x] 3.7 Implement password reset completion endpoint (`POST /auth/password/reset/confirm`)
- [x] 3.8 Implement user profile endpoints (`GET/PUT /auth/profile`)
- [x] 3.9 Create JWT token validation middleware
- [x] 3.10 Integrate authentication middleware with existing endpoints

## 4. Security Enhancements
- [x] 4.1 Implement password strength validation
- [x] 4.2 Add rate limiting for auth endpoints
- [x] 4.3 Implement token blacklist for logout functionality
- [ ] 4.4 Add CSRF protection for state-changing operations (前端实现)
- [ ] 4.5 Implement secure cookie handling for token storage (前端实现)

## 5. Testing Implementation
- [x] 5.1 Create test user fixtures for testing
- [x] 5.2 Write unit tests for auth utilities
- [x] 5.3 Write integration tests for registration flow
- [x] 5.4 Write integration tests for login flow
- [x] 5.5 Write integration tests for token refresh
- [x] 5.6 Write integration tests for logout
- [x] 5.7 Write integration tests for password reset
- [x] 5.8 Write integration tests for profile management
- [x] 5.9 Write middleware tests for token validation
- [x] 5.10 Write security tests (SQL injection, XSS, token attacks)

## 6. Error Handling and Logging
- [x] 6.1 Define error response formats for auth endpoints
- [x] 6.2 Implement structured logging for auth events
- [x] 6.3 Add error logging for failed authentication attempts
- [x] 6.4 Implement user-friendly error messages
- [x] 6.5 Add telemetry for authentication metrics

## 7. Documentation
- [x] 7.1 Update AGENTS.md with authentication testing instructions
- [x] 7.2 Update openspec/project.md with authentication architecture
- [ ] 7.3 Create API documentation for auth endpoints
- [ ] 7.4 Document security best practices
- [ ] 7.5 Create deployment guide for auth configuration

## 8. Integration with Existing System
- [x] 8.1 Update `src/index.py` to use auth middleware (创建了 main.py)
- [x] 8.2 Modify `knowledge_base` queries to filter by user ID (通过 RLS 实现)
- [x] 8.3 Update existing test_connectivity.py to work with auth
- [x] 8.4 Ensure backward compatibility for public endpoints
- [ ] 8.5 Test full integration with Supabase database (需要实际数据库连接)

## 9. Frontend Preparation (Optional)
- [ ] 9.1 Design login/registration UI components
- [ ] 9.2 Implement token storage in frontend
- [ ] 9.3 Create auth context/state management
- [ ] 9.4 Add protected route guards
- [ ] 9.5 Implement automatic token refresh logic
