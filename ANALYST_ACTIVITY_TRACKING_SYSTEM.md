# Analyst Activity Tracking System

## Overview

The Analyst Activity Tracking System provides comprehensive tracking, management, and reporting of all analyst work and activities within the investigation platform. This system enables unique identification of each analyst's contributions, detailed activity logging, and enhanced PDF report generation with analyst-specific sections.

## 🎯 Key Features

### 1. **Unique Analyst Identification**
- Each activity is uniquely linked to a specific analyst
- Analyst-specific activity dashboards
- Individual performance metrics and analytics
- Activity attribution in all reports

### 2. **Comprehensive Activity Tracking**
- 15 different activity types (notes, findings, evidence, interviews, etc.)
- Time tracking for each activity
- Priority and status management
- Tag-based categorization
- Confidentiality controls

### 3. **Enhanced Reporting**
- Analyst-specific activity sections in PDF reports
- Activity filtering and inclusion controls
- Professional report formatting with analyst attribution
- Time tracking summaries

### 4. **Performance Analytics**
- Productivity metrics
- Consistency scoring
- Quality assessments
- Collaboration tracking
- Trend analysis

## 📊 Activity Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Note** | General investigation notes | Daily logs, observations |
| **Finding** | Important discoveries | Breakthroughs, key evidence |
| **Evidence** | Evidence collection | Documenting proof, artifacts |
| **Interview** | Interview notes | Suspect interviews, witness statements |
| **Analysis** | Data analysis | Pattern recognition, assessments |
| **Action** | Actions taken | Steps performed during investigation |
| **Meeting** | Meeting notes | Team meetings, briefings |
| **Communication** | Communication logs | Calls, messages, correspondence |
| **Task** | Task completion | Assigned tasks, deliverables |
| **Update** | Status updates | Progress reports, status changes |
| **Milestone** | Milestone achievements | Key accomplishments |
| **Observation** | Observations made | Field observations |
| **Recommendation** | Recommendations given | Suggested actions, next steps |
| **Decision** | Decisions made | Important choices, resolutions |
| **Other** | Other activities | Miscellaneous work |

## 🔧 System Components

### Frontend Components

#### 1. **Enhanced Reports Page** (`cyber/src/app/dashboard/reports/page.tsx`)
- **Analyst Activity Tracking Section**: Shows all activities for the active case
- **Activity Summary Statistics**: Total activities, time tracked, contributors
- **Advanced Filtering**: By analyst, type, status, and search terms
- **Activity Management**: Add, edit, delete, and toggle report inclusion
- **Real-time Updates**: Live activity tracking and notifications

#### 2. **Analyst Activity Dashboard** (`cyber/src/components/analyst-activity-dashboard.tsx`)
- **Analyst Selection**: Choose specific analyst to view their activities
- **Activity History**: Complete activity timeline for selected analyst
- **Cross-case Activities**: View activities across all cases
- **Activity Management**: Full CRUD operations for activities
- **Advanced Search**: Filter by type, case, date range

#### 3. **Analyst Performance Dashboard** (`cyber/src/components/analyst-performance-dashboard.tsx`)
- **Performance Metrics**: Productivity, consistency, quality, collaboration scores
- **Activity Analytics**: Detailed breakdown by type, case, and time
- **Trend Analysis**: Activity patterns over time
- **Performance Scoring**: Automated scoring based on activity patterns
- **Visual Analytics**: Charts and graphs for performance visualization

### Backend Components

#### 1. **Case Activity Model** (`flask_backend/models/case_activity.py`)
```python
class CaseActivity(db.Model):
    # Core fields
    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    analyst_id = db.Column(db.Integer, db.ForeignKey('system_users.id'))
    
    # Activity details
    activity_type = db.Column(db.Enum(ActivityType))
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    status = db.Column(db.Enum(ActivityStatus))
    
    # Metadata
    tags = db.Column(db.JSON)
    priority = db.Column(db.String(20))
    time_spent_minutes = db.Column(db.Integer)
    
    # Report inclusion
    include_in_report = db.Column(db.Boolean, default=True)
    is_confidential = db.Column(db.Boolean, default=False)
    
    # Relationships
    case = db.relationship('Case', backref='activities')
    analyst = db.relationship('SystemUser', foreign_keys=[analyst_id])
```

#### 2. **API Endpoints** (`flask_backend/routes/case_activities.py`)

**Case Activities:**
- `GET /api/cases/{case_id}/activities` - List case activities
- `POST /api/cases/{case_id}/activities` - Create new activity
- `GET /api/cases/{case_id}/activities/{activity_id}` - Get specific activity
- `PUT /api/cases/{case_id}/activities/{activity_id}` - Update activity
- `DELETE /api/cases/{case_id}/activities/{activity_id}` - Delete activity
- `GET /api/cases/{case_id}/activities/summary` - Get activity summary

**Analyst Activities:**
- `GET /api/analysts/{analyst_id}/activities` - Get analyst's activities
- `GET /api/analysts/{analyst_id}/activities/summary` - Get analyst performance data

#### 3. **Enhanced PDF Report Generator** (`flask_backend/services/pdf_report_generator.py`)
- **Analyst Activities Section**: Dedicated section for analyst work
- **Activity Grouping**: Activities grouped by type for better organization
- **Analyst Attribution**: Clear identification of who performed each activity
- **Time Tracking**: Detailed time summaries and breakdowns
- **Professional Formatting**: Clean, professional report layout

## 📈 Performance Metrics

### 1. **Productivity Score**
- **Calculation**: Activities per day over time period
- **Range**: 0-100%
- **Target**: 80%+ for excellent performance

### 2. **Consistency Score**
- **Calculation**: Regularity of activity over time
- **Range**: 0-100%
- **Target**: 70%+ for consistent performance

### 3. **Quality Score**
- **Calculation**: Percentage of activities marked for reports
- **Range**: 0-100%
- **Target**: 60%+ for quality work

### 4. **Collaboration Score**
- **Calculation**: Number of different cases worked on
- **Range**: 0-100%
- **Target**: 40%+ for good collaboration

## 🚀 Usage Guide

### For Analysts

#### 1. **Adding Activities**
```typescript
// Navigate to Reports tab
// Click "Add Activity" button
// Fill in activity details:
// - Type: Select from 15 activity types
// - Title: Descriptive title
// - Description: Detailed notes
// - Time Spent: Duration in minutes
// - Tags: Comma-separated keywords
// - Priority: Low, Medium, High, Critical
// - Include in Report: Toggle for PDF inclusion
```

#### 2. **Managing Activities**
- **Edit**: Click edit icon to modify activity
- **Delete**: Click delete icon to remove activity
- **Toggle Report**: Click eye icon to include/exclude from PDF
- **Filter**: Use dropdowns to filter by type, analyst, status

#### 3. **Viewing Performance**
- **Analyst Dashboard**: View your activity history
- **Performance Metrics**: Check your scores and trends
- **Activity Analytics**: See breakdown by type and case

### For Administrators

#### 1. **Monitoring Team Performance**
- **Performance Dashboard**: View all analysts' metrics
- **Activity Reports**: Generate team activity reports
- **Trend Analysis**: Monitor team productivity trends

#### 2. **Report Generation**
- **Enhanced PDFs**: Generate reports with analyst activities
- **Activity Filtering**: Include/exclude specific activities
- **Analyst Attribution**: Clear identification of contributors

## 🔒 Security & Privacy

### 1. **Access Control**
- **Analyst-specific Access**: Users can only see their own activities
- **Admin Override**: Administrators can view all activities
- **Case-based Permissions**: Activities tied to case access

### 2. **Confidentiality**
- **Confidential Activities**: Mark sensitive activities as confidential
- **Visibility Levels**: Control who can see specific activities
- **Report Inclusion**: Separate controls for report inclusion

### 3. **Data Integrity**
- **Edit History**: Track all changes to activities
- **Version Control**: Maintain activity history
- **Audit Trail**: Complete activity audit logs

## 📊 Analytics & Reporting

### 1. **Activity Analytics**
- **By Type**: Breakdown of activity types
- **By Time**: Activity patterns over time
- **By Case**: Activities per case
- **By Analyst**: Individual analyst performance

### 2. **Performance Trends**
- **Monthly Trends**: Activity patterns by month
- **Productivity Trends**: Performance over time
- **Quality Trends**: Report inclusion rates
- **Collaboration Trends**: Cross-case involvement

### 3. **Report Generation**
- **PDF Reports**: Professional reports with analyst activities
- **Activity Summaries**: Detailed activity breakdowns
- **Performance Reports**: Analyst performance metrics
- **Team Reports**: Team-wide activity summaries

## 🎯 Best Practices

### 1. **Activity Documentation**
- **Be Descriptive**: Write detailed activity descriptions
- **Use Tags**: Tag activities for easy filtering
- **Track Time**: Accurately record time spent
- **Mark Priority**: Set appropriate priority levels

### 2. **Report Management**
- **Review Activities**: Check activities before generating reports
- **Toggle Inclusion**: Control which activities appear in reports
- **Maintain Quality**: Ensure only relevant activities are included

### 3. **Performance Optimization**
- **Regular Updates**: Keep activities current
- **Consistent Logging**: Log activities regularly
- **Quality Focus**: Mark high-quality activities for reports
- **Collaboration**: Work across multiple cases

## 🔧 Technical Implementation

### 1. **Database Schema**
```sql
CREATE TABLE case_activities (
    id INTEGER PRIMARY KEY,
    case_id INTEGER NOT NULL,
    analyst_id INTEGER NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    tags JSON,
    priority VARCHAR(20),
    activity_date DATETIME NOT NULL,
    time_spent_minutes INTEGER DEFAULT 0,
    include_in_report BOOLEAN DEFAULT TRUE,
    is_confidential BOOLEAN DEFAULT FALSE,
    visibility_level VARCHAR(20) DEFAULT 'team',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(id),
    FOREIGN KEY (analyst_id) REFERENCES system_users(id)
);
```

### 2. **API Integration**
```typescript
// Load case activities
const activities = await apiClient.getCaseActivities(caseId);

// Create new activity
const newActivity = await apiClient.createActivity(caseId, {
  title: "Interview with suspect",
  description: "Detailed interview notes...",
  activity_type: "interview",
  time_spent_minutes: 120,
  include_in_report: true
});

// Get analyst performance
const performance = await apiClient.getAnalystPerformance(analystId);
```

### 3. **PDF Generation**
```python
# Generate report with activities
pdf_path = generate_case_pdf_report(
    case=case,
    activities=activities,
    content_items=content_items,
    output_path="report.pdf"
)
```

## 📋 Summary

The Analyst Activity Tracking System provides:

✅ **Unique Analyst Identification** - Each activity is linked to a specific analyst
✅ **Comprehensive Activity Tracking** - 15 activity types with full metadata
✅ **Enhanced PDF Reports** - Professional reports with analyst activities
✅ **Performance Analytics** - Detailed metrics and scoring
✅ **Advanced Filtering** - Search and filter by multiple criteria
✅ **Real-time Updates** - Live activity tracking and notifications
✅ **Security Controls** - Confidentiality and access management
✅ **Professional Formatting** - Clean, organized report layout

This system enables complete tracking of analyst work, unique identification of contributions, and enhanced reporting capabilities that provide valuable insights into investigation progress and team performance.
