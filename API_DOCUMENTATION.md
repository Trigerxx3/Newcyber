# API Documentation - Cyber Intelligence Platform

## 🚀 **Project API Overview**

This Cyber Intelligence Platform uses a **Flask REST API backend** with a **Next.js frontend**, implementing a comprehensive narcotics investigation and OSINT system.

## 📡 **Backend API Architecture**

### **Base URL**
- **Development**: `http://127.0.0.1:5000`
- **Production**: Configured via environment variables

### **API Structure**
- **Framework**: Flask (Python)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Authentication**: JWT (JSON Web Tokens)
- **CORS**: Enabled for cross-origin requests
- **Blueprint Pattern**: Modular route organization

## 🔗 **API Endpoints by Category**

### **1. Authentication API (`/api/auth`)**
```
POST   /api/auth/signup          # User registration
POST   /api/auth/signin          # User login
GET    /api/auth/google/login    # Google OAuth login
GET    /api/auth/google/callback # Google OAuth callback
GET    /api/auth/profile         # Get user profile
```

### **2. Cases Management API (`/api/cases`)**
```
GET    /api/cases                    # Get all cases
POST   /api/cases                    # Create new case
GET    /api/cases/{id}               # Get specific case
PUT    /api/cases/{id}/status        # Update case status
PUT    /api/cases/{id}/close         # Close case
PUT    /api/cases/{id}/archive       # Archive case
POST   /api/cases/{id}/users        # Assign users to case
DELETE /api/cases/{id}/users/{user_id} # Remove user from case
POST   /api/cases/{id}/content      # Link content to case
DELETE /api/cases/{id}/content/{content_id} # Unlink content
PUT    /api/cases/{id}/progress     # Update case progress
GET    /api/cases/active            # Get active case
POST   /api/cases/active            # Set active case
DELETE /api/cases/active            # Clear active case
GET    /api/cases/statistics         # Get case statistics
GET    /api/cases/requests          # Get case requests
POST   /api/cases/requests/{id}/approve # Approve case request
POST   /api/cases/requests/{id}/reject # Reject case request
GET    /api/cases/can-create        # Check if user can create case
```

### **3. Content Analysis API (`/api/content-analysis`)**
```
POST   /api/content-analysis/analyze        # Analyze content for drugs
POST   /api/content-analysis/analyze-batch  # Batch content analysis
GET    /api/content-analysis/flagged        # Get flagged content
GET    /api/content-analysis/stats          # Get analysis statistics
PUT    /api/content-analysis/{id}/flag      # Flag/unflag content
GET    /api/content-analysis/scraped-content # Get scraped content
```

### **4. Scraping API (`/api/scraping`)**
```
GET    /api/scraping/stats                 # Get scraping statistics
GET    /api/scraping/jobs                  # Get scraping jobs
POST   /api/scraping/jobs                  # Create scraping job
POST   /api/scraping/jobs/{id}/control     # Control scraping job
POST   /api/scraping/jobs/{id}/toggle      # Toggle job status
POST   /api/scraping/jobs/{id}/run         # Run scraping job
GET    /api/scraping/content               # Get scraped content
DELETE /api/scraping/content/{id}          # Delete content
GET    /api/scraping/export/{type}         # Export data
GET    /api/scraping/telegram/status       # Telegram scraper status
GET    /api/scraping/telegram/channels     # Get Telegram channels
POST   /api/scraping/telegram/scrape       # Scrape Telegram
GET    /api/scraping/instagram/profiles    # Get Instagram profiles
POST   /api/scraping/instagram/scrape      # Scrape Instagram
GET    /api/scraping/whatsapp/groups       # Get WhatsApp groups
GET    /api/scraping/health-check          # Scraping health check
```

### **5. OSINT API (`/api/osint`)**
```
GET    /api/osint/                        # OSINT root endpoint
POST   /api/osint/search                  # Perform OSINT search
GET    /api/osint/results                 # Get OSINT results
GET    /api/osint/results/{id}            # Get specific result
POST   /api/osint/analyze                 # Analyze OSINT data
GET    /api/osint/sources                 # Get OSINT sources
POST   /api/osint/monitor                 # Start monitoring
DELETE /api/osint/monitor/{id}            # Stop monitoring
POST   /api/osint/investigate-user         # Investigate user
GET    /api/osint/tools/status            # Get tools status
```

### **6. Reports API (`/api/reports`)**
```
GET    /api/reports/{id}/generate         # Generate case report
GET    /api/reports/{id}/preview          # Preview case report
GET    /api/reports/active/generate       # Generate active case report
GET    /api/reports/active/preview        # Preview active case report
GET    /api/reports/list                  # List available reports
GET    /api/reports/{id}/generate-detailed # Generate detailed report
GET    /api/reports/health                # Reports health check
```

### **7. Dashboard API (`/api/dashboard`)**
```
GET    /api/dashboard/                    # Dashboard root
GET    /api/dashboard/stats               # Dashboard statistics
GET    /api/dashboard/recent-content      # Recent content
GET    /api/dashboard/high-risk-content   # High-risk content
GET    /api/dashboard/trends              # Content trends
GET    /api/dashboard/alerts              # System alerts
PUT    /api/dashboard/alerts/{id}/read    # Mark alert as read
```

### **8. Admin API (`/api/admin`)**
```
GET    /api/admin/stats                   # Admin statistics
GET    /api/admin/users                   # Manage users
POST   /api/admin/users/{id}/toggle-active # Toggle user status
GET    /api/admin/sources                 # Manage sources
POST   /api/admin/sources                 # Create source
POST   /api/admin/sources/{id}/toggle     # Toggle source
GET    /api/admin/keywords                # Manage keywords
POST   /api/admin/keywords                # Create keyword
POST   /api/admin/keywords/{id}/toggle    # Toggle keyword
GET    /api/admin/data/stats              # Data statistics
GET    /api/admin/data/platform-users     # Platform users
POST   /api/admin/data/platform-users/{id}/flag # Flag user
GET    /api/admin/data/content            # Content data
GET    /api/admin/data/cases              # Cases data
GET    /api/admin/data/export/{type}      # Export data
GET    /api/admin/activity               # Admin activity
GET    /api/admin/api-status              # API status
```

### **9. Case Activities API (`/api/cases/{id}/activities`)**
```
GET    /api/cases/{id}/activities         # Get case activities
POST   /api/cases/{id}/activities         # Create activity
GET    /api/cases/{id}/activities/{activity_id} # Get specific activity
PUT    /api/cases/{id}/activities/{activity_id} # Update activity
DELETE /api/cases/{id}/activities/{activity_id} # Delete activity
POST   /api/cases/{id}/activities/{activity_id}/toggle-report # Toggle report inclusion
GET    /api/cases/{id}/activities/summary # Get activities summary
```

### **10. Health & Utility APIs**
```
GET    /api/health                        # Health check
GET    /api/                             # API root
GET    /api/content                      # Content management
GET    /api/users                        # User management
GET    /api/sources                      # Source management
GET    /api/keywords                     # Keyword management
```

## 🔧 **Frontend API Client**

### **API Client Location**: `cyber/src/lib/api.ts`

### **Key Features**:
- **Automatic JWT token management**
- **Request/response interceptors**
- **Error handling with retry logic**
- **Timeout management**
- **CORS support**

### **API Client Methods**:
```typescript
// Authentication
signUp(email, password, username, role)
signIn(email, password)
getProfile()

// Cases
getCases(status?)
createCase(caseData)
getCase(caseId)
linkContentToCase(caseId, contentIds)
closeCase(caseId, notes?)
archiveCase(caseId, notes?)

// Content Analysis
analyzeContent(contentData)
getContentAnalysisScrapedContent(limit?)

// Scraping
getScrapingStats()
getScrapedContent(limit?)
scrapeTelegramChannel(channel, limit)
getTelegramChannels()

// OSINT
investigateUser(username, platform)
getOsintToolsStatus()

// Reports
generateCaseReport(caseId)
previewCaseReport(caseId)
generateDetailedCaseReport(caseId, params?)

// Dashboard
getDashboardInfo()
getSources(params?)
getUsers(params?)
getContent(params?)
```

## 🛠️ **External APIs & Services**

### **1. Telegram API**
- **Library**: Telethon (Python)
- **Purpose**: Telegram channel/user scraping
- **Authentication**: API ID, API Hash, Phone Number
- **Endpoints**: Channel messages, user profiles

### **2. Instagram API**
- **Library**: Custom scraper service
- **Purpose**: Instagram profile/post scraping
- **Features**: Profile data, post content, hashtag analysis

### **3. WhatsApp API**
- **Library**: Custom WhatsApp scraper
- **Purpose**: WhatsApp group monitoring
- **Features**: Group messages, user analysis

### **4. OSINT Tools Integration**
- **Sherlock**: Username investigation across platforms
- **Spiderfoot**: Network reconnaissance and OSINT
- **Custom Tools**: Social media analysis

### **5. Google OAuth**
- **Service**: Google OAuth 2.0
- **Purpose**: User authentication
- **Implementation**: Flask-OAuthlib

## 📊 **Database APIs**

### **Database**: SQLite (Development) / PostgreSQL (Production)
### **ORM**: SQLAlchemy
### **Models**:
- `SystemUser` - User management
- `Case` - Investigation cases
- `Content` - Scraped content
- `Source` - Data sources
- `OSINTResult` - OSINT findings
- `CaseActivity` - Case activities
- `Keyword` - Monitoring keywords

## 🔐 **Authentication & Security**

### **JWT Authentication**
- **Access Tokens**: Short-lived (15 minutes)
- **Refresh Tokens**: Long-lived (7 days)
- **Role-based Access**: Admin, Analyst roles
- **Protected Routes**: Most endpoints require authentication

### **CORS Configuration**
- **Development**: All origins allowed
- **Production**: Restricted to specific domains
- **Headers**: Authorization, Content-Type, etc.
- **Methods**: GET, POST, PUT, DELETE, OPTIONS

## 📈 **API Usage Examples**

### **1. User Authentication**
```javascript
// Login
const response = await apiClient.signIn('user@example.com', 'password');
localStorage.setItem('access_token', response.access_token);

// Access protected endpoint
const cases = await apiClient.getCases();
```

### **2. Content Analysis**
```javascript
// Analyze content for drugs
const analysis = await apiClient.analyzeContent({
  platform: 'Instagram',
  username: 'user123',
  content: 'Buy drugs here',
  save_to_database: true
});
```

### **3. OSINT Investigation**
```javascript
// Investigate user across platforms
const results = await apiClient.investigateUser('username', 'Instagram');
```

### **4. Case Management**
```javascript
// Create case
const case = await apiClient.createCase({
  title: 'Drug Investigation',
  description: 'Investigation details',
  priority: 'HIGH'
});

// Link content to case
await apiClient.linkContentToCase(caseId, [contentId1, contentId2]);
```

## 🚀 **Deployment APIs**

### **Production URLs**
- **Backend**: Railway/Render deployment
- **Frontend**: Vercel deployment
- **Database**: PostgreSQL (Railway/Render)

### **Environment Variables**
```bash
# Backend
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
FLASK_ENV=production

# Frontend
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## 📋 **API Response Format**

### **Success Response**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### **Error Response**
```json
{
  "status": "error",
  "message": "Error description",
  "error_code": "ERROR_CODE"
}
```

### **Pagination Response**
```json
{
  "status": "success",
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 100,
    "pages": 10
  }
}
```

## 🔍 **API Testing**

### **Health Check**
```bash
curl http://127.0.0.1:5000/api/health
```

### **Authentication Test**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@cyber.com","password":"password"}'
```

This comprehensive API system provides a complete narcotics investigation platform with real-time data scraping, content analysis, OSINT capabilities, and case management functionality.



