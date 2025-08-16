-- Check auth users
SELECT 
  id,
  email,
  created_at,
  email_confirmed_at,
  last_sign_in_at
FROM auth.users 
WHERE email IN ('admin@cyber.com', 'analyst@cyber.com');

-- Check system users
SELECT 
  system_user_id,
  auth_user_id,
  username,
  email,
  role,
  created_at
FROM system_users 
WHERE email IN ('admin@cyber.com', 'analyst@cyber.com');

-- Check linking
SELECT 
  su.username,
  su.email,
  su.role,
  au.email as auth_email,
  au.created_at as auth_created,
  au.email_confirmed_at
FROM system_users su
JOIN auth.users au ON su.auth_user_id = au.id
WHERE su.email IN ('admin@cyber.com', 'analyst@cyber.com');