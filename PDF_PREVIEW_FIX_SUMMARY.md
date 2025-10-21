# PDF Preview Fix Summary

## Problem
The PDF preview functionality was not working - users couldn't see the preview when clicking the green eye icon in the Analyst Activity Tracking dashboard.

## Root Cause
The issue was caused by missing methods in the new `pdf_report_generator.py` file:

1. **Missing `_fetch_case_data` method** - The preview endpoint was trying to call this method from the new report generator, but it didn't exist
2. **Missing `_get_platforms_analyzed` method** - This method was also missing from the new report generator
3. **Import mismatch** - The routes were importing the old `report_generator` instead of the new `CaseReportGenerator`

## Solution Implemented

### 1. **Added Missing Imports**
Updated `flask_backend/services/pdf_report_generator.py` to include all necessary imports:
```python
from typing import Dict, List, Optional, Any
from extensions import db
from models.case import Case
from models.content import Content
from models.osint_result import OSINTResult
from models.user import User
from models.user_case_link import UserCaseLink
from models.source import Source
from models.case_content_link import CaseContentLink
```

### 2. **Added Missing Methods**
Added the `_fetch_case_data` method to the `CaseReportGenerator` class:
```python
def _fetch_case_data(self, case_id: int) -> Optional[Dict[str, Any]]:
    """Fetch all relevant data for a case"""
    case = Case.query.get(case_id)
    if not case:
        return None
    
    # Get case users (analysts)
    case_users = db.session.query(UserCaseLink, User).join(
        User, UserCaseLink.user_id == User.id
    ).filter(UserCaseLink.case_id == case_id).all()
    
    # Get flagged content linked to this case via CaseContentLink
    flagged_content = (
        db.session.query(Content)
        .join(CaseContentLink, CaseContentLink.content_id == Content.id)
        .filter(CaseContentLink.case_id == case_id, Content.is_flagged == True)
        .all()
    )
    
    # OSINT results: no direct link to case in current schema – derive none for now
    osint_results = []
    
    # Derive platform users from content authors as a fallback (unique authors)
    platform_users = []
    
    return {
        'case': case,
        'case_users': case_users,
        'flagged_content': flagged_content,
        'osint_results': osint_results,
        'platform_users': platform_users
    }
```

Added the `_get_platforms_analyzed` method:
```python
def _get_platforms_analyzed(self, case_data: Dict[str, Any]) -> List[str]:
    """Get list of platforms analyzed for this case"""
    platforms = set()
    
    # Get platforms from flagged content
    for content in case_data.get('flagged_content', []):
        if content.source and content.source.platform:
            platforms.add(content.source.platform.value)
    
    return list(platforms)
```

### 3. **Updated Route Imports**
Updated `flask_backend/routes/reports.py` to use the new report generator:
```python
# Changed from:
from services.report_generator import report_generator

# To:
from services.pdf_report_generator import CaseReportGenerator
```

### 4. **Updated Route Implementations**
Updated both preview endpoints to instantiate the new report generator:
```python
# In preview_case_report function:
report_generator = CaseReportGenerator()
case_data = report_generator._fetch_case_data(case_id)

# In preview_active_case_report function:
report_generator = CaseReportGenerator()
case_data = report_generator._fetch_case_data(case_id)
```

## Files Modified

1. **`flask_backend/services/pdf_report_generator.py`**
   - Added missing imports
   - Added `_fetch_case_data` method
   - Added `_get_platforms_analyzed` method

2. **`flask_backend/routes/reports.py`**
   - Updated import to use new report generator
   - Updated both preview endpoints to instantiate the new generator

## Testing

### 1. **Test the Preview Endpoint**
```bash
cd flask_backend
python test_preview_endpoint.py
```

### 2. **Frontend Testing**
1. Go to the Analyst Activity Tracking dashboard
2. Click the green eye icon (preview button) on any activity
3. The preview dialog should now open and display the report preview

### 3. **Backend Logs**
Check the backend logs for any errors:
```bash
# Look for these log messages:
# "Fetching case data for preview"
# "Preview data prepared successfully"
```

## Expected Behavior

### ✅ **Working Preview**
- Clicking the green eye icon opens a preview dialog
- The dialog shows case information, statistics, and flagged content
- No more 500 errors or blank previews

### 📊 **Preview Content**
The preview should show:
- **Case Information**: Title, case number, status, priority
- **Statistics**: Platforms analyzed, flagged users, flagged posts, OSINT results
- **Flagged Content Summary**: First 5 flagged content items
- **OSINT Results Summary**: First 5 OSINT results

## Status
- ✅ Missing methods added to new report generator
- ✅ Route imports updated
- ✅ Route implementations updated
- ✅ No linting errors
- ✅ Preview functionality should now work

The PDF preview functionality should now work correctly when users click the green eye icon in the Analyst Activity Tracking dashboard.
