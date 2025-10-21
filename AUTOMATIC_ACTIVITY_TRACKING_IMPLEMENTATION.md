# Automatic Activity Tracking Implementation

## Overview

I have successfully implemented automatic activity tracking for user investigations and content analysis activities. The system now automatically logs all user activities when they perform investigations and content analysis on the site, creating a comprehensive audit trail of analyst work.

## 🎯 What Was Implemented

### 1. **Activity Tracking Service** (`flask_backend/services/activity_tracker.py`)

Created a comprehensive activity tracking service that automatically logs:

#### **User Investigation Activities**
- **Trigger**: When users investigate usernames using OSINT tools
- **Activity Type**: `investigation`
- **Auto-captured Data**:
  - Target username and platform
  - Number of profiles found
  - Risk level assessment
  - Tools used in investigation
  - Investigation timestamp
  - Estimated time spent

#### **Content Analysis Activities**
- **Trigger**: When users analyze content for drug-related keywords
- **Activity Type**: `content_analysis`
- **Auto-captured Data**:
  - Content text preview
  - Platform and author
  - Suspicion score and intent
  - Matched keywords
  - Flagged status
  - Analysis confidence

#### **Batch Analysis Activities**
- **Trigger**: When users perform batch content analysis
- **Activity Type**: `batch_analysis`
- **Auto-captured Data**:
  - Total items analyzed
  - Number of flagged items
  - Average suspicion score
  - Platform being analyzed

#### **OSINT Search Activities**
- **Trigger**: When users perform OSINT searches
- **Activity Type**: `osint_search`
- **Auto-captured Data**:
  - Search query and type
  - Results count
  - Risk score
  - Search status

### 2. **Enhanced Activity Types**

Added new activity types to the system:

```python
INVESTIGATION = "investigation"          # User investigation activity
CONTENT_ANALYSIS = "content_analysis"    # Content analysis activity
OSINT_SEARCH = "osint_search"            # OSINT search activity
BATCH_ANALYSIS = "batch_analysis"        # Batch content analysis
PLATFORM_SCRAPING = "platform_scraping" # Platform scraping activity
```

### 3. **Automatic Integration**

#### **Investigation Endpoint Integration**
- **File**: `flask_backend/routes/osint.py`
- **Endpoint**: `/api/osint/investigate-user`
- **Integration**: Automatically tracks when users investigate usernames
- **Data Captured**: Username, platform, results, risk level, tools used

#### **Content Analysis Integration**
- **File**: `flask_backend/routes/content_analysis.py`
- **Endpoint**: `/api/content-analysis/analyze`
- **Integration**: Automatically tracks individual content analysis
- **Data Captured**: Content, platform, author, suspicion score, intent, keywords

#### **Batch Analysis Integration**
- **File**: `flask_backend/routes/content_analysis.py`
- **Endpoint**: `/api/content-analysis/analyze-batch`
- **Integration**: Automatically tracks batch content analysis
- **Data Captured**: Total items, flagged count, average scores

### 4. **Frontend Updates**

#### **Enhanced Activity Types in UI**
- Updated all activity type dropdowns to include new types
- Added investigation and analysis specific activity types
- Enhanced filtering capabilities

#### **Updated Components**
- `cyber/src/app/dashboard/reports/page.tsx`
- `cyber/src/components/analyst-activity-dashboard.tsx`
- `cyber/src/components/analyst-performance-dashboard.tsx`

## 🔧 Technical Implementation

### 1. **Activity Tracking Service**

```python
class ActivityTracker:
    def track_investigation_activity(self, user_id, username, platform, results):
        # Creates investigation activity with:
        # - Risk-based priority
        # - Investigation metadata
        # - Time estimation
        # - Confidentiality controls
        
    def track_content_analysis_activity(self, user_id, content, platform, username, results):
        # Creates content analysis activity with:
        # - Suspicion score-based priority
        # - Analysis metadata
        # - Content preview
        # - Flagged status
        
    def track_batch_analysis_activity(self, user_id, batch_results, platform):
        # Creates batch analysis activity with:
        # - Batch statistics
        # - Flagged item count
        # - Average scores
```

### 2. **Automatic Priority Assignment**

#### **Investigation Activities**
- **Low Risk**: Low priority
- **Medium Risk**: Medium priority
- **High Risk**: High priority
- **Critical Risk**: Critical priority

#### **Content Analysis Activities**
- **Score 0-40**: Low priority
- **Score 40-60**: Medium priority
- **Score 60-80**: High priority
- **Score 80+**: Critical priority

### 3. **Time Estimation**

#### **Investigation Time**
- Base: 15 minutes
- Additional: 2 minutes per profile found
- Maximum: 2 hours

#### **Content Analysis Time**
- Base: 5 minutes
- Additional: 1 minute per 100 characters
- Maximum: 30 minutes

#### **Batch Analysis Time**
- 2 minutes per item analyzed
- Maximum: 1 hour

### 4. **Confidentiality Controls**

#### **Investigation Activities**
- High/Critical risk → Confidential
- Low/Medium risk → Team visibility

#### **Content Analysis Activities**
- Flagged + High suspicion → Confidential
- Non-flagged → Team visibility

## 📊 Activity Metadata

### 1. **Investigation Activities**
```json
{
  "investigation_type": "user_investigation",
  "target_username": "suspected_user",
  "platform": "Instagram",
  "total_profiles_found": 5,
  "risk_level": "high",
  "tools_used": ["sherlock", "spiderfoot"],
  "investigation_timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. **Content Analysis Activities**
```json
{
  "analysis_type": "content_analysis",
  "platform": "Telegram",
  "author": "user123",
  "suspicion_score": 85,
  "intent": "selling",
  "is_flagged": true,
  "matched_keywords": ["drug", "buy", "cheap"],
  "content_preview": "Buy drugs cheap...",
  "analysis_timestamp": "2024-01-15T10:30:00Z"
}
```

### 3. **Batch Analysis Activities**
```json
{
  "analysis_type": "batch_content_analysis",
  "platform": "Instagram",
  "total_items_analyzed": 50,
  "flagged_items": 12,
  "average_suspicion_score": 65.5,
  "batch_timestamp": "2024-01-15T10:30:00Z"
}
```

## 🚀 Usage Examples

### 1. **User Investigation**
```javascript
// When user investigates a username
const response = await apiClient.investigateUser('suspected_user', 'Instagram');

// Activity automatically created:
// - Type: investigation
// - Title: "User Investigation: suspected_user on Instagram"
// - Priority: Based on risk level
// - Time: Estimated based on results
// - Confidential: If high risk
```

### 2. **Content Analysis**
```javascript
// When user analyzes content
const response = await apiClient.analyzeContent({
  platform: 'Telegram',
  username: 'user123',
  content: 'Buy drugs cheap'
});

// Activity automatically created:
// - Type: content_analysis
// - Title: "Content Analysis: user123 on Telegram"
// - Priority: Based on suspicion score
// - Time: Estimated based on content length
// - Confidential: If flagged and high suspicion
```

### 3. **Batch Analysis**
```javascript
// When user performs batch analysis
const response = await apiClient.analyzeBatchContent({
  platform: 'Instagram',
  content_items: [/* array of content */]
});

// Activity automatically created:
// - Type: batch_analysis
// - Title: "Batch Content Analysis: Instagram"
// - Priority: Based on flagged count
// - Time: Estimated based on item count
// - Confidential: If high percentage flagged
```

## 📈 Benefits

### 1. **Automatic Tracking**
- ✅ No manual activity logging required
- ✅ All investigations and analyses automatically tracked
- ✅ Comprehensive audit trail
- ✅ Time tracking without user input

### 2. **Intelligent Prioritization**
- ✅ Risk-based priority assignment
- ✅ Suspicion score-based prioritization
- ✅ Automatic confidentiality controls
- ✅ Smart time estimation

### 3. **Enhanced Reporting**
- ✅ Investigation activities in PDF reports
- ✅ Content analysis activities in reports
- ✅ Batch analysis summaries
- ✅ OSINT search activities

### 4. **Performance Analytics**
- ✅ Investigation productivity metrics
- ✅ Content analysis efficiency
- ✅ Batch processing statistics
- ✅ OSINT search effectiveness

## 🔒 Security & Privacy

### 1. **Confidentiality Controls**
- High-risk investigations → Confidential
- Flagged content analysis → Confidential
- Sensitive OSINT searches → Confidential

### 2. **Access Control**
- Activities linked to specific analysts
- Case-based access controls
- Role-based visibility

### 3. **Data Protection**
- Content previews truncated
- Sensitive data in attachments
- Secure metadata storage

## 📋 Summary

The automatic activity tracking system now provides:

✅ **Complete Activity Coverage** - All user investigations and content analysis automatically tracked
✅ **Intelligent Prioritization** - Risk and suspicion-based priority assignment
✅ **Smart Time Tracking** - Automatic time estimation based on activity complexity
✅ **Enhanced Security** - Automatic confidentiality controls for sensitive activities
✅ **Comprehensive Metadata** - Rich activity data for reporting and analytics
✅ **Seamless Integration** - No changes required to existing user workflows
✅ **Performance Insights** - Detailed analytics on investigation and analysis activities

The system now automatically captures all analyst work when they perform investigations and content analysis, creating a comprehensive audit trail that enhances reporting capabilities and provides valuable insights into team productivity and investigation patterns.
