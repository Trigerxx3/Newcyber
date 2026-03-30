# Database Data Summary - Cyber Intelligence Platform

## 📊 **Current Database Status**

Your Cyber Intelligence Platform database contains **222 total records** across **19 tables**.

## 🗄️ **Database Overview**

### **Database File Location**
- **Primary Database**: `flask_backend/cyber_intel.db` (344 KB)
- **Backup Database**: `flask_backend/temp.db` (12 KB)
- **Type**: SQLite (Local Development)

### **Total Data**
- **Tables**: 19
- **Total Records**: 222
- **Database Size**: 344 KB

## 📋 **Table Breakdown**

| Table Name | Records | Purpose |
|------------|---------|---------|
| `system_users` | 24 | User accounts and authentication |
| `content` | 111 | Scraped content and analysis |
| `sources` | 31 | Data sources for scraping |
| `cases` | 14 | Investigation cases |
| `user_case_links` | 10 | User-case assignments |
| `email_verifications` | 11 | Email verification records |
| `user_approvals` | 11 | User approval workflow |
| `active_cases` | 3 | Currently active case sessions |
| `case_content_links` | 3 | Content linked to cases |
| `case_activities` | 1 | Case activity tracking |
| `osint_results` | 1 | OSINT investigation results |
| `alembic_version` | 1 | Database migration tracking |

## 👥 **User Data**

### **Active Users (13)**
- **Admin Users**: 1 (admin@cyber.com)
- **Analyst Users**: 12
- **Total Active**: 13 users

### **User Roles**
- **ADMIN**: 1 user
- **ANALYST**: 23 users

### **Recent Users**
- tom (tom@1234.com) - Active
- newuser456 (newuser456@example.com) - Active  
- newuser123 (newuser123@example.com) - Active
- test_analyst (analyst@test.com) - Active
- sam (admin@cyber-intel.com) - Active

## 📁 **Case Data**

### **Total Cases: 14**
- **Open Cases**: 9 cases
- **Closed Cases**: 1 case
- **Recent Cases**:
  - CASE-2025-014: "dsfdf" (OPEN, HIGH priority)
  - CASE-2025-013: "Admin Test Case" (OPEN, HIGH priority)
  - CASE-2025-012: "Analyst Test Case" (OPEN, MEDIUM priority)
  - CASE-2025-011: "sd" (OPEN, MEDIUM priority)
  - CASE-2025-010: "test" (OPEN, CRITICAL priority)

### **Case Priorities**
- **CRITICAL**: 1 case
- **HIGH**: 3 cases  
- **MEDIUM**: 5 cases

## 📄 **Content Data**

### **Total Content: 111 items**
- **Scraped Content**: 111 items
- **Content Sources**: 31 sources
- **Linked Content**: 3 items linked to cases

### **Content Sources**
- **Sources Available**: 31 data sources
- **Content Items**: 111 scraped items
- **Analysis Data**: Content analysis and risk assessment

## 🔗 **Relationships**

### **User-Case Links (10)**
- Users assigned to cases
- Role-based access control
- Activity tracking

### **Case-Content Links (3)**
- Content linked to specific cases
- Evidence and documentation
- Report generation data

### **Case Activities (1)**
- Activity tracking for cases
- Interview records
- Investigation progress

## 🛠️ **Database Access Methods**

### **1. Direct SQLite Access**
```bash
# Navigate to database
cd flask_backend

# Access SQLite database
sqlite3 cyber_intel.db

# Common commands
.tables          # List all tables
.schema          # Show all schemas
SELECT * FROM cases LIMIT 5;  # Query data
```

### **2. Python Database Explorer**
```bash
# Run the database explorer
cd flask_backend
python simple_db_explorer.py
```

### **3. Flask Application API**
```bash
# Start the backend server
cd flask_backend
python run.py

# Access via API endpoints
# http://127.0.0.1:5000/api/health
# http://127.0.0.1:5000/api/cases
# http://127.0.0.1:5000/api/users
```

## 📊 **Data Analysis Queries**

### **User Statistics**
```sql
-- Active users by role
SELECT role, COUNT(*) as count 
FROM system_users 
WHERE is_active = 1 
GROUP BY role;

-- Recent user registrations
SELECT username, email, created_at 
FROM system_users 
ORDER BY created_at DESC 
LIMIT 10;
```

### **Case Statistics**
```sql
-- Cases by status
SELECT status, COUNT(*) as count 
FROM cases 
GROUP BY status;

-- Cases by priority
SELECT priority, COUNT(*) as count 
FROM cases 
GROUP BY priority;

-- Recent cases
SELECT title, case_number, status, created_at 
FROM cases 
ORDER BY created_at DESC 
LIMIT 10;
```

### **Content Analysis**
```sql
-- Content by source
SELECT source_id, COUNT(*) as count 
FROM content 
GROUP BY source_id;

-- Recent content
SELECT id, text, author, created_at 
FROM content 
ORDER BY created_at DESC 
LIMIT 10;
```

## 🔍 **Data Export Options**

### **Export to CSV**
```bash
# Export cases
sqlite3 cyber_intel.db -header -csv "SELECT * FROM cases;" > cases_export.csv

# Export users
sqlite3 cyber_intel.db -header -csv "SELECT * FROM system_users;" > users_export.csv

# Export content
sqlite3 cyber_intel.db -header -csv "SELECT * FROM content;" > content_export.csv
```

### **Backup Database**
```bash
# Create backup
cp cyber_intel.db cyber_intel_backup_$(date +%Y%m%d).db

# SQLite backup command
sqlite3 cyber_intel.db ".backup backup_$(date +%Y%m%d).db"
```

## 📈 **Data Growth Trends**

### **Recent Activity**
- **New Cases**: 5 cases created in last 2 days
- **New Users**: 3 users registered recently
- **Content**: 111 content items available
- **Sources**: 31 data sources configured

### **Database Health**
- **Tables**: All 19 tables present
- **Relationships**: Properly linked
- **Data Integrity**: No corruption detected
- **Size**: 344 KB (efficient storage)

## 🎯 **Quick Access Commands**

### **Start Database Access**
```bash
# Navigate to backend
cd flask_backend

# Access SQLite directly
sqlite3 cyber_intel.db

# Or run Python explorer
python simple_db_explorer.py
```

### **Common Queries**
```sql
-- Show all tables
.tables

-- Show table schema
.schema cases

-- Query recent data
SELECT * FROM cases ORDER BY created_at DESC LIMIT 5;
SELECT * FROM system_users WHERE is_active = 1;
SELECT * FROM content ORDER BY created_at DESC LIMIT 5;
```

## ✅ **Summary**

Your Cyber Intelligence Platform database is **fully operational** with:

- ✅ **222 total records** across 19 tables
- ✅ **13 active users** (1 admin, 12 analysts)
- ✅ **14 investigation cases** (9 open, 1 closed)
- ✅ **111 content items** from 31 sources
- ✅ **Proper relationships** and data integrity
- ✅ **Multiple access methods** available

The database contains comprehensive data for case management, user authentication, content analysis, and OSINT operations, all properly structured and accessible through multiple interfaces.



