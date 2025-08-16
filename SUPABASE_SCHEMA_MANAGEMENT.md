# Supabase Schema Management

## Database Schema Overview

The cyber intelligence platform uses the following tables:

### Core Tables
- `sources` - Data sources (Telegram, Instagram, WhatsApp)
- `users` - Platform users being monitored
- `content` - Scraped content from sources
- `keywords` - Detection keywords with categories and weights
- `detections` - Keyword matches in content
- `identifiers` - User identifiers (email, phone, crypto wallets)
- `osint_results` - OSINT investigation results
- `cases` - Investigation cases
- `user_case_link` - Links users to cases
- `system_users` - System users (extends Supabase auth)

## Making Schema Changes

### 1. Using Supabase Dashboard SQL Editor
- Go to SQL Editor in your Supabase dashboard
- Write your migration SQL
- Run the script
- Save as a migration for version control

### 2. Version Control Your Migrations
Create migration files in `migrations/` folder:

```sql
-- migrations/001_initial_schema.sql
-- migrations/002_enable_rls.sql
-- migrations/003_add_new_features.sql
```

### 3. Common Schema Operations

#### Adding a Column
```sql
ALTER TABLE content 
ADD COLUMN sentiment_score DECIMAL(3,2);
```

#### Adding an Index
```sql
CREATE INDEX idx_content_sentiment 
ON content(sentiment_score);
```

#### Updating RLS Policies
```sql
DROP POLICY IF EXISTS "policy_name" ON table_name;
CREATE POLICY "new_policy_name" ON table_name
    FOR SELECT USING (condition);
```

### 4. Backup Before Changes
```sql
-- Create backup table
CREATE TABLE content_backup AS 
SELECT * FROM content;
```

### 5. Testing Schema Changes
- Always test in development first
- Use transactions for complex changes
- Have rollback scripts ready

## Current Schema Features

### Data Types
- **UUID Primary Keys**: All tables use UUID for better distribution
- **ENUMs**: Strict typing for categories and statuses
- **Timestamps**: All tables have created_at/updated_at
- **Foreign Keys**: Proper relationships with CASCADE options

### Indexes
- Primary keys auto-indexed
- Foreign keys indexed for performance
- Search fields indexed (usernames, handles, terms)
- Composite indexes for unique constraints

### Triggers
- Automatic updated_at timestamp updates
- Data validation triggers
- Audit logging triggers

## Best Practices

1. **Always backup before major changes**
2. **Test RLS policies thoroughly**
3. **Use descriptive migration names**
4. **Document breaking changes**
5. **Keep migration files in version control**
6. **Use UUIDs for all primary keys**
7. **Add proper indexes for query performance**
8. **Use ENUMs for controlled vocabularies**
