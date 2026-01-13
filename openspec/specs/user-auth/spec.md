# user-auth Specification

## Purpose
TBD - created by archiving change add-user-authentication. Update Purpose after archive.
## Requirements
### Requirement: User Registration
The system SHALL allow new users to register with an email address and password.

#### Scenario: Successful registration
- **WHEN** a user provides a valid email address and password (minimum 8 characters)
- **THEN** a new user account is created
- **AND** a verification email is sent to the provided email address
- **AND** the system returns a success response with user ID
- **AND** the password is securely hashed before storage

#### Scenario: Registration with duplicate email
- **WHEN** a user attempts to register with an email that already exists
- **THEN** the registration fails
- **AND** the system returns a 400 Bad Request error
- **AND** the error message indicates the email is already registered

#### Scenario: Registration with invalid email
- **WHEN** a user provides an invalid email format
- **THEN** the registration fails
- **AND** the system returns a 400 Bad Request error
- **AND** the error message indicates invalid email format

#### Scenario: Registration with weak password
- **WHEN** a user provides a password with less than 8 characters
- **THEN** the registration fails
- **AND** the system returns a 400 Bad Request error
- **AND** the error message indicates password requirements

### Requirement: User Login
The system SHALL authenticate users and issue JWT tokens upon successful login.

#### Scenario: Successful login
- **WHEN** a user provides valid email and password credentials
- **THEN** the credentials are verified against stored hash
- **AND** a JWT access token is generated
- **AND** a refresh token is generated
- **AND** the system returns both tokens with user profile data
- **AND** the access token expires after 1 hour
- **AND** the refresh token expires after 7 days

#### Scenario: Login with invalid credentials
- **WHEN** a user provides incorrect email or password
- **THEN** authentication fails
- **AND** the system returns a 401 Unauthorized error
- **AND** no token is issued
- **AND** the error message does not reveal whether email or password was incorrect

#### Scenario: Login for unverified email
- **WHEN** a user tries to login with an email that has not been verified
- **THEN** authentication fails
- **AND** the system returns a 403 Forbidden error
- **AND** the error message indicates email verification is required

### Requirement: Token Validation
The system SHALL validate JWT tokens for protected endpoints.

#### Scenario: Valid token access
- **WHEN** a request includes a valid, non-expired JWT token
- **THEN** the token is decoded and verified
- **AND** the user ID is extracted from the token
- **AND** the request proceeds to the protected endpoint
- **AND** the user context is available to the endpoint handler

#### Scenario: Expired token access
- **WHEN** a request includes an expired JWT token
- **THEN** the token validation fails
- **AND** the system returns a 401 Unauthorized error
- **AND** the error message indicates token expiration

#### Scenario: Invalid token access
- **WHEN** a request includes a malformed or tampered JWT token
- **THEN** the token validation fails
- **AND** the system returns a 401 Unauthorized error
- **AND** the error message indicates invalid token

#### Scenario: Missing token access
- **WHEN** a request to a protected endpoint lacks an Authorization header
- **THEN** the request is rejected
- **AND** the system returns a 401 Unauthorized error
- **AND** the error message indicates authentication is required

### Requirement: Token Refresh
The system SHALL allow users to refresh their access tokens using a valid refresh token.

#### Scenario: Successful token refresh
- **WHEN** a user provides a valid, non-expired refresh token
- **THEN** a new access token is generated
- **AND** a new refresh token is generated
- **AND** the old refresh token is invalidated
- **AND** the system returns both new tokens
- **AND** the new tokens have fresh expiration times

#### Scenario: Refresh with expired token
- **WHEN** a user provides an expired refresh token
- **THEN** the refresh fails
- **AND** the system returns a 401 Unauthorized error
- **AND** no new tokens are issued

#### Scenario: Refresh with invalid token
- **WHEN** a user provides an invalid or revoked refresh token
- **THEN** the refresh fails
- **AND** the system returns a 401 Unauthorized error
- **AND** no new tokens are issued

### Requirement: User Logout
The system SHALL invalidate user sessions upon logout.

#### Scenario: Successful logout
- **WHEN** an authenticated user requests logout
- **THEN** the user's refresh token is invalidated
- **AND** the access token cannot be renewed after expiration
- **AND** the system returns a success response
- **AND** the access token remains valid until its natural expiration

### Requirement: Password Reset
The system SHALL allow users to reset their password via email verification.

#### Scenario: Initiate password reset
- **WHEN** a user requests a password reset with their registered email
- **THEN** a password reset token is generated
- **AND** an email with reset link is sent to the user
- **AND** the reset token expires after 1 hour
- **AND** the system returns a success response without revealing email existence

#### Scenario: Complete password reset
- **WHEN** a user provides a valid reset token and new password
- **THEN** the reset token is validated
- **AND** the user's password is updated with the new value
- **AND** the reset token is invalidated
- **AND** all existing sessions for the user are terminated
- **AND** the system returns a success response

#### Scenario: Password reset with expired token
- **WHEN** a user provides an expired reset token
- **THEN** the reset fails
- **AND** the system returns a 400 Bad Request error
- **AND** the password is not changed

### Requirement: User Profile Management
The system SHALL allow authenticated users to view and update their profile.

#### Scenario: View user profile
- **WHEN** an authenticated user requests their profile
- **THEN** the system returns the user's profile data
- **AND** sensitive fields like password hash are excluded
- **AND** the response includes user ID, email, and metadata

#### Scenario: Update user profile
- **WHEN** an authenticated user submits profile updates
- **THEN** only allowed fields are updated
- **AND** the email address cannot be changed
- **AND** the password cannot be updated through this endpoint
- **AND** the system returns the updated profile

### Requirement: Supabase Integration
The system SHALL use Supabase Auth for authentication and user management.

#### Scenario: Initialize Supabase Auth client
- **WHEN** the application starts
- **THEN** Supabase Auth client is initialized with environment variables
- **AND** the client configuration includes the Supabase URL and key
- **AND** the client is ready for authentication operations

#### Scenario: Supabase Auth registration
- **WHEN** a user registration request is processed
- **THEN** Supabase Auth API is called with email and password
- **AND** the response includes the Supabase user ID
- **AND** any Supabase errors are properly mapped to HTTP error responses

#### Scenario: Supabase Auth login
- **WHEN** a user login request is processed
- **THEN** Supabase Auth API is called with credentials
- **AND** the response includes access token, refresh token, and user data
- **AND** tokens are stored for session management

