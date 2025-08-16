-- Enable Row Level Security
-- Run this after initial schema

-- Enable RLS on all tables
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE content ENABLE ROW LEVEL SECURITY;
ALTER TABLE keywords ENABLE ROW LEVEL SECURITY;
ALTER TABLE detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE identifiers ENABLE ROW LEVEL SECURITY;
ALTER TABLE osint_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_case_link ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_users ENABLE ROW LEVEL SECURITY;

-- Helper functions
CREATE OR REPLACE FUNCTION get_user_role()
RETURNS user_role AS $$
BEGIN
    RETURN (
        SELECT role 
        FROM system_users 
        WHERE auth_user_id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_user_role() = 'Admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Basic RLS policies (add more specific policies as needed)
CREATE POLICY "authenticated_users_read" ON sources FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON users FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON content FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON keywords FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON detections FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON identifiers FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON osint_results FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON cases FOR SELECT USING (auth.role() = 'authenticated');
CREATE POLICY "authenticated_users_read" ON user_case_link FOR SELECT USING (auth.role() = 'authenticated');

-- Admin policies
CREATE POLICY "admin_full_access" ON sources FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON users FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON content FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON keywords FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON detections FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON identifiers FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON osint_results FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON cases FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON user_case_link FOR ALL USING (is_admin());
CREATE POLICY "admin_full_access" ON system_users FOR ALL USING (is_admin());