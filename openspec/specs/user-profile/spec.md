# user-profile Specification

## Purpose
TBD - created by archiving change add-user-profile-management. Update Purpose after archive.
## Requirements
### Requirement: User Profile Creation
The system SHALL automatically create a user profile when a new user registers via Supabase Auth.

#### Scenario: Auto-create profile on registration
- **WHEN** a new user is created in `auth.users`
- **THEN** a corresponding profile record SHALL be created in `public.user_profiles` with default values

#### Scenario: Profile creation with defaults
- **WHEN** a new profile is created
- **THEN** display_name SHALL default to empty string
- **THEN** avatar_url SHALL default to NULL
- **THEN** bio SHALL default to NULL
- **THEN** preferences SHALL default to empty JSON object '{}'
- **THEN** stats SHALL default to empty JSON object '{}'
- **THEN** is_active SHALL default to true

### Requirement: Get User Profile
The system SHALL provide an endpoint to retrieve a user's profile information.

#### Scenario: Get own profile
- **WHEN** authenticated user requests their profile
- **THEN** return complete profile data including display_name, avatar_url, bio, phone, website, preferences, stats

#### Scenario: Profile not found
- **WHEN** authenticated user requests a profile that does not exist
- **THEN** return 404 error with appropriate message

### Requirement: Update User Profile
The system SHALL allow users to update their own profile information.

#### Scenario: Update display name
- **WHEN** user updates display_name
- **THEN** display_name SHALL be updated in database
- **THEN** updated_at SHALL be automatically set to current timestamp

#### Scenario: Update profile fields
- **WHEN** user updates profile with valid data
- **THEN** avatar_url SHALL be validated as valid URL format
- **THEN** website SHALL be validated as valid URL format
- **THEN** preferences SHALL be validated as valid JSON

#### Scenario: Update preferences
- **WHEN** user updates preferences JSON field
- **THEN** system SHALL accept any valid JSON object
- **THEN** system SHALL preserve all valid preference keys

### Requirement: Profile Security
The system SHALL enforce access control on profile data via Row Level Security.

#### Scenario: User reads own profile
- **WHEN** authenticated user queries profiles table
- **THEN** user SHALL only see their own profile record

#### Scenario: User updates own profile
- **WHEN** authenticated user updates profiles table
- **THEN** user SHALL only modify their own profile record

#### Scenario: Prevent profile deletion
- **WHEN** authenticated user attempts to delete profile
- **THEN** operation SHALL be denied by RLS policy

### Requirement: Profile Statistics
The system SHALL track user activity statistics in the profile.

#### Scenario: Increment login count
- **WHEN** user successfully logs in
- **THEN** login_count in stats SHALL be incremented by 1
- **THEN** last_login_at SHALL be updated to current timestamp

#### Scenario: Update profile view count
- **WHEN** user profile is viewed
- **THEN** views_count in stats SHALL be incremented by 1

