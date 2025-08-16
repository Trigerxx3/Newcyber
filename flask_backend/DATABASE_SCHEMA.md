# Database Schema Documentation

## Overview

This document describes the PostgreSQL database schema for the Cyber Intelligence Platform. The schema is designed to support comprehensive threat intelligence, OSINT operations, case management, and user collaboration.

## Table Structure

### 1. Sources Table (`sources`)

**Purpose**: Store data sources for content collection and monitoring.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `name` (String): Source name (indexed)
- `url` (String): Source URL
- `type` (Enum): Source type (dark_web, social_media, news, etc.)
- `status` (Enum): Source status (active, inactive, suspended, error)
- `config` (JSON): Source-specific configuration
- `credentials` (JSON): Encrypted credentials
- `is_active` (Boolean): Active status flag
- `is_verified` (Boolean): Verification status
- `last_scraped` (DateTime): Last scraping timestamp
- `error_count` (Integer): Error tracking

**Relationships**:
- One-to-Many with `content`
- One-to-Many with `detections`

### 2. Users Table (`users`)

**Purpose**: User management and authentication.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `username` (String): Unique username (indexed)
- `email` (String): Unique email (indexed)
- `password_hash` (String): Hashed password
- `first_name`, `last_name` (String): User names
- `role` (Enum): User role (admin, analyst, investigator, viewer, guest)
- `status` (Enum): User status (active, inactive, suspended, pending)
- `preferences` (JSON): User preferences
- `last_login` (DateTime): Last login timestamp
- `login_count` (Integer): Login tracking

**Relationships**:
- One-to-Many with `content` (created_by)
- One-to-Many with `detections` (detected_by)
- One-to-Many with `user_case_links`
- One-to-Many with `verified_identifiers`
- One-to-Many with `verified_osint_links`

### 3. Content Table (`content`)

**Purpose**: Store analyzed content from various sources.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `source_id` (Foreign Key): Reference to sources table
- `created_by_id` (Foreign Key): Reference to users table
- `title` (String): Content title
- `text` (Text): Content text (required)
- `url` (String): Content URL
- `content_type` (Enum): Content type (text, html, json, etc.)
- `risk_level` (Enum): Risk assessment (low, medium, high, critical)
- `status` (Enum): Content status (pending, processed, analyzed, etc.)
- `keywords` (JSON): Detected keywords array
- `analysis_data` (JSON): Detailed analysis results
- `language` (String): Content language
- `word_count`, `character_count` (Integer): Text metrics
- `sentiment_score`, `confidence_score` (Float): Analysis scores

**Relationships**:
- Many-to-One with `sources`
- Many-to-One with `users` (created_by)
- One-to-Many with `detections`

### 4. Keywords Table (`keywords`)

**Purpose**: Store threat detection keywords and patterns.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `keyword` (String): Keyword value (unique, indexed)
- `type` (Enum): Keyword type (threat, malware, exploit, etc.)
- `severity` (Enum): Severity level (low, medium, high, critical)
- `status` (Enum): Status (active, inactive, deprecated, testing)
- `pattern` (String): Regex pattern for matching
- `is_regex` (Boolean): Whether pattern is regex
- `case_sensitive` (Boolean): Case sensitivity flag
- `context` (JSON): Additional context
- `aliases` (JSON): Alternative spellings
- `tags` (JSON): Categorization tags
- `detection_count` (Integer): Usage statistics
- `confidence_threshold` (Float): Minimum confidence for detection

**Relationships**:
- One-to-Many with `detections`

### 5. Detections Table (`detections`)

**Purpose**: Link table between content and keywords with detection details.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `content_id` (Foreign Key): Reference to content table
- `keyword_id` (Foreign Key): Reference to keywords table
- `source_id` (Foreign Key): Reference to sources table
- `detected_by_id` (Foreign Key): Reference to users table
- `matched_text` (Text): Actual matched text
- `context_before`, `context_after` (Text): Surrounding context
- `position_start`, `position_end` (Integer): Text positions
- `confidence_score` (Float): Detection confidence
- `confidence_level` (Enum): Confidence level (low, medium, high, very_high)
- `status` (Enum): Detection status (new, reviewed, confirmed, etc.)
- `metadata` (JSON): Additional detection metadata
- `notes` (Text): Analyst notes
- `tags` (JSON): Categorization tags
- `reviewed_by_id` (Foreign Key): Reviewer reference
- `reviewed_at` (DateTime): Review timestamp

**Relationships**:
- Many-to-One with `content`
- Many-to-One with `keywords`
- Many-to-One with `sources`
- Many-to-One with `users` (detected_by, reviewed_by)

### 6. Identifiers Table (`identifiers`)

**Purpose**: Track entities (emails, IPs, domains, etc.) across investigations.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `value` (String): Identifier value (indexed)
- `type` (Enum): Identifier type (email, phone, ip_address, etc.)
- `status` (Enum): Status (active, inactive, verified, suspicious, blocked)
- `description` (Text): Description
- `confidence_score` (Float): Confidence in identifier
- `verification_status` (Boolean): Verification flag
- `verified_by_id` (Foreign Key): Verifier reference
- `context` (JSON): Additional context
- `aliases` (JSON): Alternative representations
- `tags` (JSON): Categorization tags
- `detection_count` (Integer): Usage statistics
- `risk_score` (Float): Risk assessment
- `risk_level` (String): Risk level
- `threat_indicators` (JSON): Associated threats

**Relationships**:
- Many-to-One with `users` (verified_by)
- One-to-Many with `osint_identifier_links`

### 7. OSINT Results Table (`osint_results`)

**Purpose**: Store OSINT search results and analysis.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `query` (String): Search query (indexed)
- `search_type` (Enum): Search type (general, threat, person, etc.)
- `status` (Enum): Result status (pending, in_progress, completed, etc.)
- `search_sources` (JSON): Sources to search
- `search_parameters` (JSON): Search parameters
- `filters` (JSON): Search filters
- `results` (JSON): Raw search results
- `analysis` (JSON): Analysis results
- `summary` (Text): Human-readable summary
- `total_sources_searched` (Integer): Performance metrics
- `successful_sources` (Integer): Success count
- `failed_sources` (Integer): Failure count
- `processing_time` (Float): Processing time
- `risk_score` (Float): Risk assessment
- `risk_level` (String): Risk level
- `threat_indicators` (JSON): Detected threats
- `tags` (JSON): Categorization tags
- `notes` (Text): Analyst notes
- `priority` (Integer): Priority level
- `error_message` (Text): Error information
- `retry_count` (Integer): Retry tracking
- `completed_at` (DateTime): Completion timestamp

**Relationships**:
- One-to-Many with `osint_identifier_links`

### 8. Cases Table (`cases`)

**Purpose**: Manage investigations and cases.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `title` (String): Case title (indexed)
- `description` (Text): Case description
- `case_number` (String): Unique case number (indexed)
- `type` (Enum): Case type (threat_investigation, incident_response, etc.)
- `status` (Enum): Case status (open, in_progress, resolved, etc.)
- `priority` (Enum): Priority level (low, medium, high, critical)
- `assigned_to_id` (Foreign Key): Assignee reference
- `created_by_id` (Foreign Key): Creator reference
- `owner_id` (Foreign Key): Owner reference
- `summary` (Text): Case summary
- `objectives` (Text): Case objectives
- `methodology` (Text): Investigation methodology
- `findings` (Text): Investigation findings
- `recommendations` (Text): Recommendations
- `risk_score` (Float): Risk assessment
- `risk_level` (String): Risk level
- `threat_indicators` (JSON): Associated threats
- `tags` (JSON): Categorization tags
- `metadata` (JSON): Additional metadata
- `external_references` (JSON): External references
- `start_date` (DateTime): Case start date
- `due_date` (DateTime): Due date
- `estimated_completion` (DateTime): Estimated completion
- `actual_completion` (DateTime): Actual completion
- `progress_percentage` (Integer): Progress tracking
- `milestones` (JSON): Case milestones
- `checkpoints` (JSON): Progress checkpoints

**Relationships**:
- Many-to-One with `users` (assigned_to, created_by, owner)
- One-to-Many with `user_case_links`

### 9. User Case Links Table (`user_case_links`)

**Purpose**: Many-to-many relationship between users and cases with roles and permissions.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `user_id` (Foreign Key): Reference to users table
- `case_id` (Foreign Key): Reference to cases table
- `role` (Enum): User role (owner, assignee, investigator, etc.)
- `status` (Enum): Link status (active, inactive, suspended, removed)
- `can_edit` (Boolean): Edit permission
- `can_delete` (Boolean): Delete permission
- `can_assign` (Boolean): Assignment permission
- `can_comment` (Boolean): Comment permission
- `can_view_sensitive` (Boolean): Sensitive data permission
- `assigned_by_id` (Foreign Key): Assigner reference
- `assigned_at` (DateTime): Assignment timestamp
- `assignment_reason` (Text): Assignment reason
- `last_activity` (DateTime): Last activity
- `activity_count` (Integer): Activity tracking
- `notes` (Text): Notes
- `metadata` (JSON): Additional metadata

**Relationships**:
- Many-to-One with `users` (user, assigned_by)
- Many-to-One with `cases`

**Constraints**:
- Unique constraint on (user_id, case_id)

### 10. OSINT Identifier Links Table (`osint_identifier_links`)

**Purpose**: Many-to-many relationship between OSINT results and identifiers.

**Key Fields**:
- `id` (Primary Key): Auto-incrementing integer
- `osint_result_id` (Foreign Key): Reference to osint_results table
- `identifier_id` (Foreign Key): Reference to identifiers table
- `link_type` (Enum): Link type (direct, indirect, associated, etc.)
- `confidence_score` (Float): Link confidence
- `confidence_level` (Enum): Confidence level (low, medium, high, very_high)
- `context` (Text): Context where link was found
- `evidence` (JSON): Supporting evidence
- `source_url` (String): Source URL
- `source_type` (String): Source type
- `analysis_notes` (Text): Analyst notes
- `risk_assessment` (JSON): Risk assessment
- `verification_status` (Boolean): Verification flag
- `verified_by_id` (Foreign Key): Verifier reference
- `verified_at` (DateTime): Verification timestamp
- `tags` (JSON): Categorization tags
- `metadata` (JSON): Additional metadata

**Relationships**:
- Many-to-One with `osint_results`
- Many-to-One with `identifiers`
- Many-to-One with `users` (verified_by)

**Constraints**:
- Unique constraint on (osint_result_id, identifier_id)

## PostgreSQL-Specific Features

### Data Types Used

1. **Enums**: Used for status, types, and levels to ensure data integrity
2. **JSON**: Used for flexible metadata storage
3. **Text**: Used for long text content
4. **Float**: Used for scores and measurements
5. **DateTime**: Used for timestamps with timezone support
6. **Boolean**: Used for flags and status indicators
7. **Integer**: Used for IDs, counts, and percentages

### Indexes

- Primary keys are auto-indexed
- Foreign keys are indexed for performance
- String fields used in searches are indexed
- Composite indexes for unique constraints

### Constraints

- Primary key constraints on all tables
- Foreign key constraints with cascade options
- Unique constraints on business keys
- Check constraints for data validation
- Not null constraints on required fields

### Relationships

- **One-to-Many**: Sources → Content, Users → Content, etc.
- **Many-to-Many**: Users ↔ Cases (via UserCaseLink), OSINT Results ↔ Identifiers (via OSINTIdentifierLink)
- **Self-Referencing**: Users can reference other users (assigned_by, verified_by, etc.)

## Performance Considerations

1. **Indexing Strategy**: Critical fields are indexed for query performance
2. **JSON Fields**: Used for flexible data but should be queried carefully
3. **Cascade Options**: Properly configured for data integrity
4. **Partitioning**: Large tables can be partitioned by date if needed
5. **Archiving**: Old data can be archived to separate tables

## Security Features

1. **Password Hashing**: User passwords are hashed using Werkzeug
2. **Role-Based Access**: Comprehensive role and permission system
3. **Audit Trail**: Timestamps and user tracking for all changes
4. **Data Validation**: Enums and constraints ensure data integrity
5. **Sensitive Data**: Separate flags for sensitive data access

## Migration Strategy

1. **Version Control**: All schema changes are versioned
2. **Backward Compatibility**: New fields are nullable where possible
3. **Data Migration**: Scripts for data transformation
4. **Rollback Plan**: Ability to rollback schema changes
5. **Testing**: Comprehensive testing of schema changes

This schema provides a robust foundation for a comprehensive cyber intelligence platform with proper relationships, data integrity, and performance optimization. 