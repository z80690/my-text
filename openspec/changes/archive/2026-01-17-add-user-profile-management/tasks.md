## 1. Database Schema Implementation
- [x] 1.1 Create `public.user_profiles` table with all required fields (已完成: src/auth/migrations/002_user_profiles_schema.sql)
- [x] 1.2 Add indexes for display_name, is_active, created_at, updated_at (已完成)
- [x] 1.3 Create database trigger for automatic profile creation on new user (已完成)
- [x] 1.4 Implement `get_user_profile(user_id UUID)` helper function (已完成)
- [x] 1.5 Implement `update_last_login(user_id UUID)` helper function (已完成)
- [x] 1.6 Set up RLS policies for profile access control (已完成)

## 2. API Endpoint Implementation
- [x] 2.1 Create `get_user_profile` endpoint handler (已完成: src/index.py)
- [x] 2.2 Create `update_user_profile` endpoint handler (已完成: src/index.py)
- [x] 2.3 Add input validation for profile fields (已完成: validate_profile_data 函数)
- [x] 2.4 Implement profile picture URL validation (已完成: validate_url 函数)
- [x] 2.5 Add JSON schema validation for preferences field (已完成: validate_profile_data 函数)

## 3. Testing
- [x] 3.1 Add test for user profile table existence (已完成: test_user_profile_table_exists)
- [x] 3.2 Add test for profile creation trigger (已完成: test_database_schema.py 中已有)
- [x] 3.3 Add test for get profile API endpoint (已完成: test_get_user_profile)
- [x] 3.4 Add test for update profile API endpoint (已完成: test_update_user_profile)
- [x] 3.5 Add test for RLS policies (已完成: test_database_schema.py 中已有)

## 4. Documentation
- [x] 4.1 Update API documentation with profile endpoints (已完成: openspec/project.md)
- [x] 4.2 Add example requests and responses (已完成: src/auth/API_PROFILE.md)
