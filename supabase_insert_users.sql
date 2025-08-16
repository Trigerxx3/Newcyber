-- Step 1: Create auth users using Supabase Auth API
-- You MUST do this first via Supabase Dashboard or API calls

-- Method A: Via Supabase Dashboard
-- 1. Go to Authentication > Users in Supabase Dashboard
-- 2. Click "Add user" 
-- 3. Create user with:
--    Email: admin@cyber.com
--    Password: admin123456
--    Confirm password: admin123456
-- 4. Note the generated UUID (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')
-- 5. Repeat for analyst@cyber.com with password: analyst123456

-- Method B: Via SQL function (if you have service role access)
SELECT auth.create_user(
  email := 'admin@cyber.com',
  password := 'admin123456',
  user_metadata := '{"username": "admin", "role": "Admin"}'::jsonb
);

SELECT auth.create_user(
  email := 'analyst@cyber.com', 
  password := 'analyst123456',
  user_metadata := '{"username": "analyst", "role": "Analyst"}'::jsonb
);

-- Step 2: Insert system users with ACTUAL auth user IDs
-- Replace the UUIDs below with the actual IDs from Step 1
INSERT INTO system_users (auth_user_id, username, email, role) VALUES
  ('502a8de8-c069-45ac-a087-98af8b4c4b34', 'admin', 'admin@cyber.com', 'Admin'),
  ('932c90ac-2e96-4e94-9eb1-dfaa8ffeb80f', 'analyst', 'analyst@cyber.com', 'Analyst');

-- Step 3: Verify the setup
SELECT 
  su.username,
  su.email,
  su.role,
  au.email as auth_email,
  au.created_at
FROM system_users su
JOIN auth.users au ON su.auth_user_id = au.id;


