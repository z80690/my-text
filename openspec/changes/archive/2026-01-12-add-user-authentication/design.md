## Context

The my-text application currently provides public access to a knowledge base via Supabase database queries. The system lacks user authentication, which is essential for:
- Multi-user data isolation and personalization
- User-specific content access control
- Audit logging and accountability
- Feature expansions requiring user context

This change introduces a complete authentication system using Supabase Auth, which provides:
- Built-in user management and session handling
- JWT token generation and validation
- Email verification and password reset flows
- Row-Level Security (RLS) for data isolation

### Constraints
- Must maintain compatibility with existing Tencent Cloud SCF deployment
- Must integrate with existing Supabase PostgreSQL database
- Must follow existing Python 3.10 environment
- Must maintain UTF-8 encoding and type hint conventions

### Stakeholders
- End users requiring personalized data access
- Developers needing to implement authenticated features
- System administrators managing user access

## Goals / Non-Goals

### Goals
- Implement secure user registration and login with email/password
- Provide JWT-based session management with access and refresh tokens
- Integrate Supabase Auth for user management and authentication
- Add token validation middleware for protected endpoints
- Implement password reset via email
- Enable user-specific data filtering in knowledge base queries
- Maintain security best practices (rate limiting, token expiration, etc.)

### Non-Goals
- Social login (OAuth, Google, GitHub, etc.) - out of scope for initial implementation
- Multi-factor authentication (MFA/2FA) - can be added in future iteration
- User roles and permissions (admin, moderator, etc.) - all users have equal permissions initially
- Email template customization - using Supabase default templates
- Session persistence across devices - device-specific sessions acceptable

## Decisions

### Decision 1: Use Supabase Auth for Authentication

**What**: Leverage Supabase's built-in authentication service instead of building custom auth.

**Why**:
- Supabase Auth provides production-ready authentication out of the box
- Seamless integration with existing Supabase database and RLS policies
- Reduces development time and maintenance burden
- Handles complex security concerns (JWT, session management, token rotation)
- Provides built-in email verification and password reset flows
- Well-documented and battle-tested

**Alternatives considered**:
1. **Custom auth with JWT and custom user table**
   - Pros: Full control, no external auth service dependency
   - Cons: High development cost, security risks, reinventing the wheel
   - **Rejected**: Security complexity too high for current team size

2. **Firebase Authentication**
   - Pros: Mature, well-maintained, good documentation
   - Cons: Requires additional service, complicates architecture, not already using Firebase
   - **Rejected**: Supabase already integrated, no need for another service

3. **Auth0 or other SaaS auth provider**
   - Pros: Feature-rich, enterprise-grade
   - Cons: Additional cost, service dependency, overkill for current scale
   - **Rejected**: Supabase Auth provides sufficient features

### Decision 2: JWT with Access and Refresh Tokens

**What**: Implement JWT-based authentication with short-lived access tokens (1 hour) and long-lived refresh tokens (7 days).

**Why**:
- Industry-standard approach for REST APIs
- Stateless - no server-side session storage required
- Access tokens can be used immediately without network calls
- Refresh tokens provide security by limiting token lifetime
- Compatible with Supabase Auth's default token strategy
- Enables easy integration with frontend clients

**Alternatives considered**:
1. **Single long-lived JWT token**
   - Pros: Simpler implementation, no refresh endpoint needed
   - Cons: Security risk if token compromised, no revocation capability
   - **Rejected**: Security risk too high

2. **Session-based authentication with server-side storage**
   - Pros: Easy revocation, granular control
   - Cons: Requires server-side session storage, violates stateless design, more complex for SCF
   - **Rejected**: Serverless architecture benefits from stateless approach

### Decision 3: Token Validation Middleware

**What**: Create a Python decorator/middleware function to validate JWT tokens before accessing protected endpoints.

**Why**:
- Centralized authentication logic
- Easy to apply to multiple endpoints
- Clean separation of concerns
- Follows Python decorator pattern
- Allows for future enhancement (role-based access, rate limiting)

**Alternatives considered**:
1. **Manual token validation in each endpoint**
   - Pros: Simple, no abstraction
   - Cons: Code duplication, error-prone, harder to maintain
   - **Rejected**: Violates DRY principle

2. **Third-party authentication framework (e.g., Flask-Login, FastAPI OAuth2)**
   - Pros: Feature-rich, well-tested
   - Cons: Additional dependency, may not fit existing SCF handler pattern
   - **Rejected**: Overkill for current needs, custom solution sufficient

### Decision 4: Email-Only Password Reset

**What**: Implement password reset using email verification links only.

**Why**:
- Industry standard for security
- No SMS costs or phone number collection required
- Compatible with Supabase Auth's default reset flow
- Sufficient security for most applications
- Users already have email (required for registration)

**Alternatives considered**:
1. **SMS-based OTP for password reset**
   - Pros: More secure than email alone
   - Cons: SMS costs, requires phone numbers, overkill for current needs
   - **Rejected**: Email-only is sufficient and cost-effective

2. **Security questions for password reset**
   - Pros: No email or SMS required
   - Cons: Weaker security, poor user experience, outdated approach
   - **Rejected**: Security risk and poor UX

### Decision 5: Database Schema Design

**What**: Extend Supabase Auth users with a custom `user_profiles` table for additional user data.

**Why**:
- Supabase Auth provides base user table with auth-specific fields
- Custom profile table allows application-specific data
- Separation of concerns (auth data vs. app data)
- Flexibility to add fields without modifying Supabase Auth tables
- Can leverage RLS for user data isolation

**Schema**:
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    avatar_url TEXT,
    preferences JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON user_profiles FOR UPDATE
    USING (auth.uid() = id);
```

**Alternatives considered**:
1. **Use Supabase Auth `user_metadata` field**
   - Pros: Simpler, no additional table
   - Cons: Limited to JSON, no type safety, harder to query
   - **Rejected**: Need structured, queryable data

2. **Single monolithic user table**
   - Pros: Simpler queries
   - Cons: Couples auth and app data, violates separation of concerns
   - **Rejected**: Better separation with dedicated profile table

## Risks / Trade-offs

### Risk 1: Breaking Existing Public Endpoints
**Risk**: Adding authentication to existing `knowledge_base` endpoints will break current clients.

**Mitigation**:
- Gradual migration: Create new authenticated endpoints first
- Maintain public endpoints with deprecation warnings
- Document migration path for clients
- Consider optional authentication (authenticated users get more data)
- **Status**: Accepted trade-off - necessary for security and multi-user support

### Risk 2: Email Delivery Issues
**Risk**: Email verification and password reset emails may be marked as spam or not delivered.

**Mitigation**:
- Use Supabase's managed email service with proper SPF/DKIM configuration
- Monitor email deliverability metrics
- Provide manual verification fallback for development/testing
- Document email service requirements
- **Status**: Low risk - Supabase handles deliverability

### Risk 3: Token Storage on Frontend
**Risk**: Storing JWT tokens in browser exposes them to XSS attacks.

**Mitigation**:
- Use httpOnly, secure cookies for refresh tokens (if possible)
- Short access token expiration (1 hour)
- Implement token rotation on refresh
- Recommend using secure cookie storage over localStorage
- Document security best practices for frontend implementation
- **Status**: Accepted risk - industry-standard approach with mitigations

### Risk 4: Performance Impact
**Risk**: Token validation on every request may add latency.

**Mitigation**:
- Efficient JWT parsing (minimal crypto operations)
- Cache user profiles after initial lookup
- Consider edge caching for frequently accessed endpoints
- Monitor performance and optimize as needed
- **Status**: Low risk - JWT validation is fast (<5ms typical)

### Risk 5: Complexity Increase
**Risk**: Authentication adds significant code and testing complexity.

**Mitigation**:
- Comprehensive test suite before deployment
- Clear documentation and code comments
- Follow existing conventions (UTF-8, type hints, error handling)
- Incremental implementation with thorough testing at each step
- Use proven patterns from Supabase Auth documentation
- **Status**: Accepted trade-off - necessary feature

## Migration Plan

### Phase 1: Database and Environment Setup
1. Configure Supabase Auth in the Supabase dashboard
2. Create `user_profiles` table with RLS policies
3. Add environment variables (`SUPABASE_JWT_SECRET`, etc.)
4. Test database schema and policies

### Phase 2: Backend Implementation
1. Create auth utilities (token validation, password hashing)
2. Implement authentication endpoints (register, login, logout, refresh)
3. Implement password reset endpoints
4. Implement user profile endpoints
5. Add authentication middleware to existing endpoints
6. Add comprehensive tests for all auth functionality

### Phase 3: Integration Testing
1. Test full authentication flow end-to-end
2. Test token expiration and refresh
3. Test password reset flow
4. Test authenticated access to protected endpoints
5. Test error handling and edge cases

### Phase 4: Frontend Integration (Optional)
1. Implement login/registration UI
2. Add token storage and automatic refresh
3. Implement protected route guards
4. Test full user journey

### Phase 5: Deployment
1. Deploy to staging environment
2. Conduct smoke tests and security audits
3. Monitor logs and metrics
4. Deploy to production
5. Monitor for issues and user feedback

### Rollback Plan
If critical issues are discovered post-deployment:
1. Disable authentication by removing token validation middleware
2. Restore public access to knowledge base endpoints
3. Monitor system stability
4. Investigate and fix issues
5. Re-deploy with fixes
6. Re-enable authentication

**Rollback triggers**:
- Authentication blocking all user access
- Security vulnerability discovered
- Critical performance degradation
- Data corruption or loss

## Open Questions

- [ ] Should we implement email verification as required or optional?
  - **Current stance**: Required for security
  - **Decision needed**: Confirm with stakeholders

- [ ] What password strength requirements should we enforce?
  - **Current stance**: Minimum 8 characters
  - **Decision needed**: Consider adding complexity requirements (uppercase, numbers, special chars)

- [ ] Should we rate limit authentication endpoints?
  - **Current stance**: Yes, to prevent brute force attacks
  - **Decision needed**: Determine rate limits (e.g., 5 requests per minute per IP)

- [ ] How should we handle "forgot password" without knowing email?
  - **Current stance**: Generic success message to prevent email enumeration
  - **Decision needed**: Confirm with security team

- [ ] Should we implement account lockout after failed login attempts?
  - **Current stance**: No, rely on rate limiting instead
  - **Decision needed**: Review security requirements

- [ ] How do we handle user data migration when authentication is added?
  - **Current stance**: Existing data becomes public until claimed by a user
  - **Decision needed**: Define data ownership policy
