# Case Activities & Report Generation Guide

## Overview

The Case Activities feature allows analysts to track all investigation work, notes, findings, and activities on cases. These activities can then be automatically included in comprehensive PDF reports.

---

## Features

### 1. **Activity Tracking**
- Record all analyst work on cases
- Multiple activity types supported
- Edit history tracking
- Time tracking

### 2. **Activity Types**
- **Note**: General investigation notes
- **Finding**: Important discoveries
- **Evidence**: Evidence collected
- **Interview**: Interview notes
- **Analysis**: Analysis/assessment
- **Action**: Actions taken
- **Meeting**: Meeting notes
- **Communication**: Communication logs
- **Task**: Task completion
- **Update**: Status updates
- **Milestone**: Milestone achievements
- **Observation**: Observations made
- **Recommendation**: Recommendations given
- **Decision**: Decisions made
- **Other**: Other activities

### 3. **Report Generation**
- Comprehensive PDF reports
- Include/exclude specific activities
- Professional formatting
- Automatic grouping by activity type

---

## API Endpoints

### Get All Activities for a Case
```
GET /api/cases/{case_id}/activities

Query Parameters:
  - type: Filter by activity type
  - include_in_report: Filter by report inclusion
  - analyst_id: Filter by analyst
```

### Create New Activity
```
POST /api/cases/{case_id}/activities

Body:
{
  "title": "Interview with Subject",
  "description": "Detailed notes from interview...",
  "activity_type": "interview",
  "status": "active",
  "tags": ["interview", "suspect-1"],
  "priority": "high",
  "time_spent_minutes": 120,
  "include_in_report": true,
  "is_confidential": false,
  "visibility_level": "team"
}
```

### Get Specific Activity
```
GET /api/cases/{case_id}/activities/{activity_id}
```

### Update Activity
```
PUT /api/cases/{case_id}/activities/{activity_id}

Body:
{
  "title": "Updated title",
  "description": "Updated description",
  "status": "completed"
}
```

### Delete Activity
```
DELETE /api/cases/{case_id}/activities/{activity_id}
```

### Toggle Report Inclusion
```
POST /api/cases/{case_id}/activities/{activity_id}/toggle-report
```

### Get Activities Summary
```
GET /api/cases/{case_id}/activities/summary

Returns:
{
  "total_activities": 25,
  "total_time_spent_minutes": 1500,
  "total_time_spent_hours": 25.0,
  "by_type": {
    "note": 10,
    "finding": 5,
    "interview": 3
  },
  "by_analyst": {
    "john_doe": 15,
    "jane_smith": 10
  },
  "report_items_count": 20,
  "recent_activities": [...]
}
```

### Generate PDF Report with Activities
```
GET /api/reports/{case_id}/generate-detailed

Query Parameters:
  - include_activities: true/false (default: true)
  - include_content: true/false (default: true)

Returns: PDF file download
```

---

## Usage Examples

### 1. Record Investigation Notes
```javascript
const response = await fetch(`/api/cases/${caseId}/activities`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    title: 'Initial suspect identification',
    description: 'Through social media analysis, identified 3 potential suspects...',
    activity_type: 'finding',
    tags: ['social-media', 'suspects'],
    priority: 'high',
    time_spent_minutes: 180,
    include_in_report: true
  })
});
```

### 2. Edit Existing Activity
```javascript
const response = await fetch(`/api/cases/${caseId}/activities/${activityId}`, {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    description: 'Updated with additional findings...',
    status: 'completed'
  })
});
```

### 3. Generate PDF Report
```javascript
// Download PDF report with all activities
const response = await fetch(
  `/api/reports/${caseId}/generate-detailed?include_activities=true&include_content=true`,
  {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

const blob = await response.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `case_${caseId}_report.pdf`;
a.click();
```

### 4. Get Case Activity Summary
```javascript
const response = await fetch(`/api/cases/${caseId}/activities/summary`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const summary = await response.json();
console.log(`Total time spent: ${summary.total_time_spent_hours} hours`);
```

---

## Activity Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ | Activity title |
| `description` | text | ✅ | Detailed description |
| `activity_type` | enum | ✅ | Type of activity |
| `status` | enum | No | draft/active/completed/archived |
| `tags` | array | No | Tags for categorization |
| `priority` | string | No | low/medium/high/critical |
| `activity_date` | datetime | No | When activity occurred |
| `time_spent_minutes` | integer | No | Time spent (minutes) |
| `include_in_report` | boolean | No | Include in PDF report |
| `is_confidential` | boolean | No | Mark as confidential |
| `visibility_level` | string | No | public/team/restricted/confidential |
| `attachments` | array | No | File attachments |
| `evidence_links` | array | No | Links to evidence |
| `related_content_ids` | array | No | Related content IDs |
| `related_source_ids` | array | No | Related source IDs |

---

## Database Schema

### case_activities Table
```sql
CREATE TABLE case_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER NOT NULL,
    analyst_id INTEGER NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    tags JSON,
    priority VARCHAR(20),
    attachments JSON,
    evidence_links JSON,
    related_content_ids JSON,
    related_source_ids JSON,
    activity_date DATETIME NOT NULL,
    time_spent_minutes INTEGER DEFAULT 0,
    include_in_report BOOLEAN DEFAULT TRUE,
    is_confidential BOOLEAN DEFAULT FALSE,
    visibility_level VARCHAR(20) DEFAULT 'team',
    edited_at DATETIME,
    edited_by_id INTEGER,
    edit_count INTEGER DEFAULT 0,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (case_id) REFERENCES cases(id),
    FOREIGN KEY (analyst_id) REFERENCES system_users(id),
    FOREIGN KEY (edited_by_id) REFERENCES system_users(id)
);
```

---

## Report Features

### PDF Report Sections
1. **Header**
   - Case title and number
   - Status, priority, risk level
   - Generation date

2. **Case Overview**
   - Description
   - Summary
   - Objectives
   - Methodology

3. **Case Details**
   - Timeline
   - Duration
   - Progress

4. **Analyst Activities**
   - Grouped by type
   - Chronological order
   - Analyst attribution
   - Time tracking

5. **Related Evidence & Content**
   - Linked content items
   - Risk assessments
   - Flagged items

6. **Findings & Recommendations**
   - Key findings
   - Recommendations
   - Next steps

---

## Best Practices

### 1. **Activity Organization**
- Use descriptive titles
- Tag activities for easy filtering
- Set appropriate priority levels
- Track time spent accurately

### 2. **Report Inclusion**
- Mark important activities for report inclusion
- Review before generating final reports
- Use confidentiality flags appropriately

### 3. **Editing**
- Edit activities to keep them current
- Add new findings as they emerge
- Update status as work progresses

### 4. **Time Tracking**
- Record time spent on each activity
- Use summary endpoint for time reports
- Track billable hours if needed

---

## Migration

The `case_activities` table was added via migration:
```bash
alembic revision --autogenerate -m "add_case_activities_table"
alembic upgrade head
```

For production (Railway):
```bash
# Set environment variable
export USE_PRODUCTION_DB=true

# Run migration
alembic upgrade head
```

---

## Example Workflow

### Investigation Workflow
1. **Create Case** → Analyst assigned
2. **Record Initial Notes** → Create "note" activity
3. **Conduct Interviews** → Create "interview" activities
4. **Analyze Evidence** → Create "analysis" activities
5. **Document Findings** → Create "finding" activities
6. **Make Recommendations** → Create "recommendation" activities
7. **Generate Report** → Download PDF with all activities
8. **Close Case** → Mark activities as completed

---

## Frontend Integration Tips

### React Component Example
```typescript
const CaseActivities = ({ caseId }) => {
  const [activities, setActivities] = useState([]);
  
  useEffect(() => {
    fetchActivities();
  }, [caseId]);
  
  const fetchActivities = async () => {
    const response = await apiClient.get(`/cases/${caseId}/activities`);
    setActivities(response.data.activities);
  };
  
  const addActivity = async (activityData) => {
    await apiClient.post(`/cases/${caseId}/activities`, activityData);
    fetchActivities();
  };
  
  const generateReport = async () => {
    const response = await fetch(
      `/api/reports/${caseId}/generate-detailed`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    const blob = await response.blob();
    // Download logic...
  };
  
  return (
    <div>
      <button onClick={generateReport}>Generate PDF Report</button>
      {/* Activity list and forms */}
    </div>
  );
};
```

---

## Support

For issues or questions:
- Check API response errors
- Verify authentication tokens
- Ensure case exists before adding activities
- Check database migrations are applied

---

**Last Updated**: October 2025

