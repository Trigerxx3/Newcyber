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

-- Helper function to get current user's role
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

-- Helper function to check if user is admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_user_role() = 'Admin';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- System Users table policies
CREATE POLICY "Admins can view all system users" ON system_users
    FOR SELECT USING (is_admin());

CREATE POLICY "Users can view their own profile" ON system_users
    FOR SELECT USING (auth_user_id = auth.uid());

CREATE POLICY "Admins can manage system users" ON system_users
    FOR ALL USING (is_admin());

-- Sources table policies
CREATE POLICY "All authenticated users can view sources" ON sources
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage sources" ON sources
    FOR ALL USING (is_admin());

-- Users table policies (platform users)
CREATE POLICY "All authenticated users can view platform users" ON users
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Analysts can flag users" ON users
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage platform users" ON users
    FOR ALL USING (is_admin());

-- Content table policies
CREATE POLICY "All authenticated users can view content" ON content
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Analysts can update content scores" ON content
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage content" ON content
    FOR ALL USING (is_admin());

-- Keywords table policies
CREATE POLICY "All authenticated users can view keywords" ON keywords
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage keywords" ON keywords
    FOR ALL USING (is_admin());

-- Detections table policies
CREATE POLICY "All authenticated users can view detections" ON detections
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "System can create detections" ON detections
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Admins can manage detections" ON detections
    FOR ALL USING (is_admin());

-- Identifiers table policies
CREATE POLICY "All authenticated users can view identifiers" ON identifiers
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Analysts can add identifiers" ON identifiers
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage identifiers" ON identifiers
    FOR ALL USING (is_admin());

-- OSINT Results table policies
CREATE POLICY "All authenticated users can view osint results" ON osint_results
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Analysts can add osint results" ON osint_results
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage osint results" ON osint_results
    FOR ALL USING (is_admin());

-- Cases table policies
CREATE POLICY "All authenticated users can view cases" ON cases
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Analysts can create and update cases" ON cases
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

CREATE POLICY "Analysts can update cases" ON cases
    FOR UPDATE USING (auth.role() = 'authenticated');

CREATE POLICY "Admins can manage cases" ON cases
    FOR ALL USING (is_admin());

-- User Case Link table policies
CREATE POLICY "All authenticated users can view case links" ON user_case_link
    FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Analysts can manage case links" ON user_case_link
    FOR ALL USING (auth.role() = 'authenticated');
