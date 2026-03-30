# Database Access Guide - Cyber Intelligence Platform

## 📊 **Database Overview**

Your Cyber Intelligence Platform uses **PostgreSQL** for production and **SQLite** for local development. Here's how to access and manage your data.

## 🗄️ **Database Locations**

### **Production Database (Railway)**
- **Type**: PostgreSQL
- **Location**: Railway Cloud
- **Connection**: Via environment variables
- **Access**: Through Flask app or direct connection

### **Local Development Database**
- **Type**: SQLite
- **Location**: `flask_backend/cyber_intel.db`
- **Backup**: `flask_backend/instance/cyber_backend.db`
- **Access**: Direct file access or through Flask app

## 🔧 **Database Access Methods**

### **1. Through Flask Application**

#### **Start the Backend Server**
```bash
cd flask_backend
python run.py
```

#### **Access Database via API**
- **Health Check**: `http://127.0.0.1:5000/api/health`
- **Database Status**: Check server logs for database connection status

### **2. Direct Database Access**

#### **For Local SQLite Database**
```bash
# Navigate to backend directory
cd flask_backend

# Access SQLite database directly
sqlite3 cyber_intel.db

# Or use a GUI tool like DB Browser for SQLite
```

#### **For Production PostgreSQL**
```bash
# Connect to Railway PostgreSQL (if you have credentials)
psql "postgresql://username:password@host:port/database"

# Or use Railway CLI
railway connect
```

## 📋 **Database Schema & Tables**

### **Core Tables**

| Table Name | Purpose | Key Fields |
|------------|---------|------------|
| `system_users` | User management | id, username, email, role, is_active |
| `cases` | Investigation cases | id, title, case_number, status, priority |
| `content` | Scraped content | id, text, author, platform, risk_level |
| `sources` | Data sources | id, name, url, type, status |
| `keywords` | Detection keywords | id, keyword, type, severity |
| `detections` | Keyword matches | id, content_id, keyword_id, confidence |
| `osint_results` | OSINT findings | id, query, results, analysis |
| `case_activities` | Case activities | id, case_id, title, description, type |

### **Relationship Tables**

| Table Name | Purpose |
|------------|---------|
| `user_case_links` | Users assigned to cases |
| `case_content_links` | Content linked to cases |
| `osint_identifier_links` | OSINT results linked to identifiers |
| `active_cases` | Currently active case sessions |

## 🛠️ **Database Management Scripts**

### **Available Scripts**

#### **1. Data Synchronization**
```bash
# Sync Railway data to local
python sync_railway_to_local.py

# Comprehensive data check
python comprehensive_data_check.py

# Sync all data
python sync_all_data.py
```

#### **2. Database Testing**
```bash
# Test database connection
python test_models_debug.py

# Test content analysis
python test_content_analysis.py

# Test PDF generation
python test_pdf_generation.py
```

#### **3. Database Setup**
```bash
# Create case activities table
python create_case_activities_table.py

# Initialize case requests table
python init_case_requests_table.py

# Create test analyst user
python create_test_analyst.py
```

## 📊 **Data Access Examples**

### **1. View All Tables**
```sql
-- List all tables
.tables

-- Show table schema
.schema table_name
```

### **2. Query Examples**

#### **View All Cases**
```sql
SELECT id, title, case_number, status, priority, created_at 
FROM cases 
ORDER BY created_at DESC;
```

#### **View All Users**
```sql
SELECT id, username, email, role, is_active, last_login 
FROM system_users 
ORDER BY created_at DESC;
```

#### **View Content with Risk Assessment**
```sql
SELECT id, text, author, platform, risk_level, sentiment_score, created_at 
FROM content 
WHERE risk_level IN ('high', 'critical') 
ORDER BY created_at DESC;
```

#### **View Case Activities**
```sql
SELECT ca.id, ca.title, ca.activity_type, ca.status, c.title as case_title
FROM case_activities ca
JOIN cases c ON ca.case_id = c.id
ORDER BY ca.created_at DESC;
```

### **3. Data Analysis Queries**

#### **Content Statistics**
```sql
-- Content by platform
SELECT platform, COUNT(*) as count 
FROM content 
GROUP BY platform 
ORDER BY count DESC;

-- Risk level distribution
SELECT risk_level, COUNT(*) as count 
FROM content 
GROUP BY risk_level 
ORDER BY count DESC;

-- Recent content (last 7 days)
SELECT COUNT(*) as recent_content 
FROM content 
WHERE created_at >= datetime('now', '-7 days');
```

#### **Case Statistics**
```sql
-- Cases by status
SELECT status, COUNT(*) as count 
FROM cases 
GROUP BY status 
ORDER BY count DESC;

-- Cases by priority
SELECT priority, COUNT(*) as count 
FROM cases 
GROUP BY priority 
ORDER BY count DESC;

-- Active cases
SELECT c.title, c.case_number, c.status, u.username as assigned_to
FROM cases c
JOIN active_cases ac ON c.id = ac.case_id
JOIN system_users u ON ac.user_id = u.id;
```

## 🔍 **Database Inspection Tools**

### **1. SQLite Browser (Recommended for Local)**
- Download: [DB Browser for SQLite](https://sqlitebrowser.org/)
- Open: `flask_backend/cyber_intel.db`
- Features: Visual query builder, data export, schema editing

### **2. Command Line Access**
```bash
# SQLite command line
sqlite3 cyber_intel.db

# Common commands
.tables          # List all tables
.schema          # Show all schemas
.schema table    # Show specific table schema
.headers on      # Show column headers
.mode column     # Format output as columns
```

### **3. Python Database Access**
```python
# Connect to database via Flask
from app import create_app
from extensions import db

app = create_app()
with app.app_context():
    # Query examples
    from models import Case, Content, SystemUser
    
    # Get all cases
    cases = Case.query.all()
    
    # Get high-risk content
    high_risk_content = Content.query.filter(
        Content.risk_level.in_(['high', 'critical'])
    ).all()
    
    # Get active users
    active_users = SystemUser.query.filter_by(is_active=True).all()
```

## 📈 **Data Export & Backup**

### **Export Data**
```bash
# Export to CSV
sqlite3 cyber_intel.db -header -csv "SELECT * FROM cases;" > cases.csv
sqlite3 cyber_intel.db -header -csv "SELECT * FROM content;" > content.csv
sqlite3 cyber_intel.db -header -csv "SELECT * FROM system_users;" > users.csv
```

### **Backup Database**
```bash
# Create backup
cp cyber_intel.db cyber_intel_backup_$(date +%Y%m%d).db

# Or use SQLite backup command
sqlite3 cyber_intel.db ".backup backup_$(date +%Y%m%d).db"
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Errors**
```bash
# Check if database file exists
ls -la cyber_intel.db

# Check file permissions
chmod 644 cyber_intel.db
```

#### **2. Schema Issues**
```bash
# Recreate database tables
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

#### **3. Data Sync Issues**
```bash
# Run comprehensive data check
python comprehensive_data_check.py

# Sync missing data
python sync_railway_to_local.py
```

## 📊 **Database Monitoring**

### **Check Database Health**
```bash
# Run health check
python test_models_debug.py

# Check data integrity
python comprehensive_data_check.py
```

### **Monitor Database Size**
```bash
# Check SQLite file size
ls -lh cyber_intel.db

# Check table sizes
sqlite3 cyber_intel.db "SELECT name, COUNT(*) as rows FROM sqlite_master WHERE type='table' GROUP BY name;"
```

## 🎯 **Quick Access Commands**

### **Start Database Access**
```bash
# Navigate to backend
cd flask_backend

# Start Flask server (for API access)
python run.py

# Or access SQLite directly
sqlite3 cyber_intel.db
```

### **Common Queries**
```sql
-- Quick stats
SELECT 'Cases' as table_name, COUNT(*) as count FROM cases
UNION ALL
SELECT 'Content', COUNT(*) FROM content
UNION ALL
SELECT 'Users', COUNT(*) FROM system_users
UNION ALL
SELECT 'Activities', COUNT(*) FROM case_activities;

-- Recent activity
SELECT 'Recent Cases' as type, COUNT(*) as count 
FROM cases 
WHERE created_at >= datetime('now', '-7 days')
UNION ALL
SELECT 'Recent Content', COUNT(*) 
FROM content 
WHERE created_at >= datetime('now', '-7 days');
```

## ✅ **Summary**

Your database is accessible through:

1. **Flask Application**: `http://127.0.0.1:5000` (with API endpoints)
2. **Direct SQLite**: `sqlite3 cyber_intel.db`
3. **GUI Tools**: DB Browser for SQLite
4. **Python Scripts**: Various management and sync scripts

The database contains comprehensive data for cases, content, users, activities, and OSINT results, all properly structured with relationships and constraints for data integrity.



