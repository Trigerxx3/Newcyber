# Cases Module API Documentation

## Overview
The Cases module provides comprehensive case management functionality for analysts to track drug-related investigations on social media. Each case can be linked to suspicious users and flagged content for deeper OSINT investigation.

## Base URL
```
http://localhost:5000/api/cases
```

## Authentication
All endpoints require authentication. Include the authorization token in the request headers:
```
Authorization: Bearer <your_token>
```

## API Endpoints

### 1. Create a New Case
**POST** `/api/cases/`

Creates a new investigation case.

#### Request Body
```json
{
  "title": "Drug trafficking investigation - Instagram user @suspicious_user",
  "description": "Investigation into suspicious drug-related posts and user behavior",
  "type": "drug_trafficking_investigation",
  "priority": "high",
  "summary": "Initial investigation summary",
  "objectives": "Identify drug trafficking network",
  "methodology": "Social media analysis and OSINT techniques",
  "tags": ["drug-trafficking", "instagram", "urgent"]
}
```

#### Response (201 Created)
```json
{
  "status": "success",
  "message": "Case created successfully",
  "data": {
    "id": 1,
    "title": "Drug trafficking investigation - Instagram user @suspicious_user",
    "description": "Investigation into suspicious drug-related posts and user behavior",
    "case_number": "CASE-2024-001",
    "type": "drug_trafficking_investigation",
    "status": "open",
    "priority": "high",
    "created_by_id": 1,
    "summary": "Initial investigation summary",
    "objectives": "Identify drug trafficking network",
    "methodology": "Social media analysis and OSINT techniques",
    "risk_score": 0.0,
    "risk_level": "low",
    "tags": ["drug-trafficking", "instagram", "urgent"],
    "start_date": "2024-01-15T10:30:00",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

### 2. Get All Cases
**GET** `/api/cases/`

Retrieves all cases with optional filtering and pagination.

#### Query Parameters
- `status` (optional): Filter by case status (`open`, `in_progress`, `pending`, `resolved`, `closed`, `archived`)
- `priority` (optional): Filter by priority (`low`, `medium`, `high`, `critical`)
- `type` (optional): Filter by case type (`threat_investigation`, `osint_investigation`, etc.)
- `assigned_to_id` (optional): Filter by assigned user ID
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)

#### Example Request
```
GET /api/cases/?status=open&priority=high&page=1&per_page=20
```

#### Response (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Drug trafficking investigation - Instagram user @suspicious_user",
      "case_number": "CASE-2024-001",
      "status": "open",
      "priority": "high",
      "user_count": 3,
      "content_count": 5,
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### 3. Get Case Details
**GET** `/api/cases/{case_id}`

Retrieves detailed information about a specific case including linked users and content.

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "title": "Drug trafficking investigation - Instagram user @suspicious_user",
    "description": "Investigation into suspicious drug-related posts and user behavior",
    "case_number": "CASE-2024-001",
    "type": "drug_trafficking_investigation",
    "status": "open",
    "priority": "high",
    "summary": "Initial investigation summary",
    "objectives": "Identify drug trafficking network",
    "methodology": "Social media analysis and OSINT techniques",
    "findings": "",
    "recommendations": "",
    "risk_score": 0.0,
    "risk_level": "low",
    "tags": ["drug-trafficking", "instagram", "urgent"],
    "start_date": "2024-01-15T10:30:00",
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "linked_users": [
      {
        "id": 1,
        "user_id": 5,
        "case_id": 1,
        "role": "investigator",
        "status": "active",
        "can_edit": true,
        "can_delete": false,
        "can_assign": false,
        "can_comment": true,
        "can_view_sensitive": true,
        "assigned_at": "2024-01-15T10:35:00",
        "assignment_reason": "Primary investigator",
        "user": {
          "id": 5,
          "username": "suspicious_user",
          "full_name": "John Doe",
          "platform_user_id": "123456789",
          "is_flagged": true,
          "source": {
            "id": 1,
            "name": "Instagram",
            "platform_type": "social_media"
          }
        }
      }
    ],
    "linked_content": [],
    "statistics": {
      "user_count": 1,
      "content_count": 0,
      "days_open": 5,
      "is_overdue": false,
      "progress_percentage": 25
    }
  }
}
```

### 4. Link User to Case
**POST** `/api/cases/{case_id}/users`

Links a suspicious user to a case for investigation.

#### Request Body
```json
{
  "user_id": 5,
  "role": "investigator",
  "assignment_reason": "Primary suspect in drug trafficking investigation",
  "notes": "User has posted multiple drug-related content"
}
```

#### Response (201 Created)
```json
{
  "status": "success",
  "message": "User linked to case successfully",
  "data": {
    "id": 1,
    "user_id": 5,
    "case_id": 1,
    "role": "investigator",
    "status": "active",
    "can_edit": true,
    "can_delete": false,
    "can_assign": false,
    "can_comment": true,
    "can_view_sensitive": true,
    "assigned_at": "2024-01-15T10:35:00",
    "assignment_reason": "Primary suspect in drug trafficking investigation",
    "notes": "User has posted multiple drug-related content"
  }
}
```

### 5. Close Case
**PUT** `/api/cases/{case_id}/close`

Closes a case with optional closing notes.

#### Request Body
```json
{
  "notes": "Investigation completed. User identified as low-risk. No further action required."
}
```

#### Response (200 OK)
```json
{
  "status": "success",
  "message": "Case closed successfully",
  "data": {
    "id": 1,
    "status": "closed",
    "actual_completion": "2024-01-20T15:45:00",
    "progress_percentage": 100,
    "findings": "Investigation completed. User identified as low-risk. No further action required."
  }
}
```

### 6. Update Case Status
**PUT** `/api/cases/{case_id}/status`

Updates the status of a case.

#### Request Body
```json
{
  "status": "in_progress"
}
```

#### Response (200 OK)
```json
{
  "status": "success",
  "message": "Case status updated successfully",
  "data": {
    "id": 1,
    "status": "in_progress",
    "updated_at": "2024-01-16T09:15:00"
  }
}
```

### 7. Update Case Progress
**PUT** `/api/cases/{case_id}/progress`

Updates the progress percentage of a case.

#### Request Body
```json
{
  "progress_percentage": 75
}
```

#### Response (200 OK)
```json
{
  "status": "success",
  "message": "Case progress updated successfully",
  "data": {
    "id": 1,
    "progress_percentage": 75,
    "updated_at": "2024-01-16T09:15:00"
  }
}
```

### 8. Unlink User from Case
**DELETE** `/api/cases/{case_id}/users/{user_id}`

Removes a user from a case.

#### Response (200 OK)
```json
{
  "status": "success",
  "message": "User unlinked from case successfully"
}
```

### 9. Get Cases by User
**GET** `/api/cases/user/{user_id}`

Retrieves all cases linked to a specific user.

#### Query Parameters
- `role` (optional): Filter by user's role in cases

#### Response (200 OK)
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "title": "Drug trafficking investigation",
      "status": "open",
      "priority": "high",
      "user_role": "investigator",
      "user_permissions": {
        "can_edit": true,
        "can_delete": false,
        "can_assign": false,
        "can_comment": true,
        "can_view_sensitive": true
      }
    }
  ]
}
```

### 10. Get Case Statistics
**GET** `/api/cases/statistics`

Retrieves overall case statistics.

#### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "total_cases": 25,
    "by_status": {
      "open": 8,
      "in_progress": 12,
      "pending": 3,
      "resolved": 1,
      "closed": 1,
      "archived": 0
    },
    "by_priority": {
      "low": 5,
      "medium": 15,
      "high": 4,
      "critical": 1
    },
    "by_type": {
      "osint_investigation": 10,
      "threat_investigation": 8,
      "incident_response": 4,
      "forensic_analysis": 2,
      "custom": 1
    },
    "average_duration_days": 12.5,
    "overdue_cases": 3
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Title is required"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Case not found"
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Failed to create case: Database connection error"
}
```

## Case Status Values
- `open`: Case is newly created and ready for investigation
- `in_progress`: Case is actively being investigated
- `pending`: Case is waiting for additional information or resources
- `resolved`: Case investigation is complete with findings
- `closed`: Case is closed and archived
- `archived`: Case is archived for long-term storage

## Case Priority Values
- `low`: Low priority investigation
- `medium`: Standard priority investigation
- `high`: High priority investigation requiring attention
- `critical`: Critical investigation requiring immediate action

## Case Type Values
- `drug_trafficking_investigation`: Investigation of drug trafficking activities
- `substance_abuse_detection`: Detection and analysis of substance abuse content
- `social_media_monitoring`: Monitoring social media platforms for suspicious activity
- `suspicious_content_analysis`: Analysis of flagged suspicious content
- `user_behavior_analysis`: Analysis of user behavior patterns
- `network_disruption`: Investigation of network disruption activities
- `compliance_enforcement`: Enforcement of platform compliance policies
- `osint_investigation`: Open source intelligence investigation
- `threat_investigation`: Investigation of potential threats
- `incident_response`: Response to security incidents
- `vulnerability_assessment`: Assessment of system vulnerabilities
- `compliance_audit`: Compliance and audit investigations
- `forensic_analysis`: Digital forensic analysis
- `malware_analysis`: Malware analysis and investigation
- `network_monitoring`: Network monitoring and analysis
- `custom`: Custom investigation type

## User Roles in Cases
- `owner`: Full control over the case
- `assignee`: Assigned to work on the case
- `investigator`: Conducting investigation activities
- `analyst`: Analyzing data and evidence
- `reviewer`: Reviewing case materials
- `viewer`: Read-only access to case
- `contributor`: Contributing to case investigation

## Integration with OSINT Module

To run OSINT investigation on a linked user, use the existing OSINT endpoint:
```
POST /api/osint/username/{username}
```

This can be called from the case details page to investigate suspicious users linked to the case.
