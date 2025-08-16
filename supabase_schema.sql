-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create custom types
CREATE TYPE user_role AS ENUM ('Admin', 'Analyst');
CREATE TYPE content_source AS ENUM ('Telegram', 'Instagram', 'WhatsApp');
CREATE TYPE source_type AS ENUM ('Channel', 'Group', 'Profile');
CREATE TYPE keyword_category AS ENUM ('Drug', 'Slang', 'Emoji', 'Payment');
CREATE TYPE identifier_type AS ENUM ('Email', 'Phone', 'Crypto_Wallet', 'Other');
CREATE TYPE case_status AS ENUM ('Open', 'Under Review', 'Closed');

-- 1. Sources table
CREATE TABLE sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    platform content_source NOT NULL,
    source_handle TEXT UNIQUE NOT NULL,
    source_name TEXT,
    source_type source_type,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Users table (platform users, not system users)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(source_id),
    platform_user_id TEXT,
    username TEXT,
    full_name TEXT,
    bio TEXT,
    is_flagged BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Content table
CREATE TABLE content (
    content_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID NOT NULL REFERENCES sources(source_id),
    user_id UUID NOT NULL REFERENCES users(user_id),
    platform_content_id TEXT,
    text_content TEXT,
    posted_at TIMESTAMP WITH TIME ZONE,
    suspicion_score INTEGER CHECK(suspicion_score >= 0 AND suspicion_score <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Keywords table
CREATE TABLE keywords (
    keyword_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    term TEXT NOT NULL,
    category keyword_category,
    weight INTEGER CHECK(weight >= 1 AND weight <= 10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Detections table
CREATE TABLE detections (
    detection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    content_id UUID NOT NULL REFERENCES content(content_id),
    keyword_id UUID NOT NULL REFERENCES keywords(keyword_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Identifiers table
CREATE TABLE identifiers (
    identifier_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    identifier_type identifier_type,
    identifier_value TEXT NOT NULL,
    source_content_id UUID REFERENCES content(content_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. OSINT Results table
CREATE TABLE osint_results (
    osint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    found_platform TEXT,
    found_url TEXT,
    checked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 8. Cases table
CREATE TABLE cases (
    case_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_name TEXT NOT NULL,
    status case_status DEFAULT 'Open',
    analyst_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 9. User Case Link table
CREATE TABLE user_case_link (
    link_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id),
    case_id UUID NOT NULL REFERENCES cases(case_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 10. System Users table (extends Supabase auth.users)
CREATE TABLE system_users (
    system_user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    email TEXT UNIQUE,
    role user_role NOT NULL DEFAULT 'Analyst',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_sources_platform ON sources(platform);
CREATE INDEX idx_sources_handle ON sources(source_handle);
CREATE INDEX idx_users_source_id ON users(source_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_flagged ON users(is_flagged);
CREATE INDEX idx_content_source_id ON content(source_id);
CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_content_posted_at ON content(posted_at);
CREATE INDEX idx_content_suspicion_score ON content(suspicion_score);
CREATE INDEX idx_keywords_term ON keywords(term);
CREATE INDEX idx_keywords_category ON keywords(category);
CREATE INDEX idx_detections_content_id ON detections(content_id);
CREATE INDEX idx_detections_keyword_id ON detections(keyword_id);
CREATE INDEX idx_identifiers_user_id ON identifiers(user_id);
CREATE INDEX idx_identifiers_type ON identifiers(identifier_type);
CREATE INDEX idx_osint_user_id ON osint_results(user_id);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_user_case_link_user ON user_case_link(user_id);
CREATE INDEX idx_user_case_link_case ON user_case_link(case_id);
CREATE INDEX idx_system_users_username ON system_users(username);
CREATE INDEX idx_system_users_email ON system_users(email);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_updated_at BEFORE UPDATE ON content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_keywords_updated_at BEFORE UPDATE ON keywords FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_identifiers_updated_at BEFORE UPDATE ON identifiers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_system_users_updated_at BEFORE UPDATE ON system_users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
