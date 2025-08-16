# Cyber Intelligence Platform - Backend API

A Flask-based REST API for cyber threat intelligence data analysis and management. This backend has been migrated from Supabase to use SQLAlchemy ORM with PostgreSQL (production) and SQLite (development).

## 🚀 Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **Database Management**: SQLAlchemy ORM with Flask-Migrate for database migrations
- **Multi-Database Support**: PostgreSQL for production, SQLite for development
- **Threat Intelligence**: Advanced content analysis, keyword detection, and OSINT integration
- **Case Management**: Investigation case tracking and user assignment
- **RESTful API**: Comprehensive REST API with proper error handling
- **Content Analysis**: Risk assessment and automated threat detection

## 🏗️ Architecture

### Database Models
- **Users**: Both platform users (suspects) and system users (analysts)
- **Sources**: Social media sources (Telegram, Instagram, WhatsApp)
- **Content**: Analyzed social media content with risk assessments
- **Keywords**: Threat detection keywords with pattern matching
- **Detections**: Links between content and detected keywords
- **Identifiers**: Extracted entities (emails, IPs, domains, etc.)
- **OSINT Results**: Open source intelligence search results
- **Cases**: Investigation case management
- **User-Case Links**: Many-to-many relationships for case assignments

### Technology Stack
- **Framework**: Flask 2.3.3
- **Database**: SQLAlchemy 3.0.5 + Flask-Migrate 4.0.5
- **Authentication**: JWT tokens with Flask-JWT-Extended 4.5.3
- **Database Drivers**: psycopg2-binary (PostgreSQL), SQLite (development)
- **Password Security**: Werkzeug password hashing

## 📋 Requirements

- Python 3.8+
- PostgreSQL (for production)
- SQLite (for development - included with Python)

## 🔧 Installation

### 1. Clone and Setup
```bash
cd flask_backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy and update the environment file:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/cyber_intelligence_db

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=24

# File Storage
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### 3. Database Setup

#### For Development (SQLite):
```bash
python init_db.py
```

#### For Production (PostgreSQL):
1. Create PostgreSQL database:
```sql
CREATE DATABASE cyber_intelligence_db;
CREATE USER cyber_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cyber_intelligence_db TO cyber_user;
```

2. Update `.env` with PostgreSQL connection string:
```env
DATABASE_URL=postgresql://cyber_user:your_password@localhost:5432/cyber_intelligence_db
FLASK_ENV=production
```

3. Initialize database:
```bash
python init_db.py
```

### 4. Start the Server
```bash
python run.py
```

The API will be available at: `http://localhost:5000`

## 🔐 Authentication

### Default Admin Account
After running `init_db.py`, you can login with:
- **Email**: `admin@cyber-intel.com`
- **Password**: `AdminPass123!`
- **Role**: Admin

**⚠️ Important**: Change the default password after first login!

### API Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### User Roles
- **Admin**: Full system access, user management
- **Analyst**: Data analysis, case management, content review

## 📖 API Documentation

### Authentication Endpoints
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/signin` - User login
- `POST /api/auth/refresh` - Refresh JWT token
- `POST /api/auth/signout` - User logout
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update user profile
- `GET /api/auth/users` - List all users (Admin only)
- `PUT /api/auth/users/<id>` - Update user (Admin only)

### Core Data Endpoints
- `GET /api/sources` - List sources
- `POST /api/sources` - Create source (Admin only)
- `GET /api/sources/<id>` - Get source details
- `PUT /api/sources/<id>` - Update source (Admin only)
- `DELETE /api/sources/<id>` - Delete source (Admin only)

- `GET /api/content` - List content
- `POST /api/content` - Create content
- `GET /api/content/<id>` - Get content details
- `GET /api/content/high-risk` - Get high-risk content

- `GET /api/keywords` - List keywords
- `POST /api/keywords` - Create keyword (Admin only)
- `PUT /api/keywords/<id>` - Update keyword (Admin only)
- `DELETE /api/keywords/<id>` - Delete keyword (Admin only)

### Investigation Endpoints
- `GET /api/cases` - List cases
- `POST /api/cases` - Create case
- `GET /api/cases/<id>` - Get case details
- `PUT /api/cases/<id>/status` - Update case status
- `POST /api/cases/<id>/users` - Assign users to case

### System Endpoints
- `GET /health` - Health check
- `GET /api` - API documentation
- `GET /test-db` - Database connection test

## 🔄 Database Migrations

### Creating Migrations
```bash
# After model changes
flask db migrate -m "Description of changes"
flask db upgrade
```

### Migration Commands
```bash
# Initialize migrations (done by init_db.py)
flask db init

# Create migration
flask db migrate -m "Migration message"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## 🧪 Testing

### Basic API Testing
```bash
# Health check
curl http://localhost:5000/health

# Login
curl -X POST http://localhost:5000/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@cyber-intel.com", "password": "AdminPass123!"}'

# Get profile (with token)
curl http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Database Testing
```bash
python test_api.py
```

## 🔧 Configuration

### Development vs Production

**Development (SQLite)**:
- Database: `local.db` file
- Debug mode enabled
- Detailed error messages
- Auto-reload on code changes

**Production (PostgreSQL)**:
- Database: PostgreSQL server
- Debug mode disabled
- Error logging to syslog
- Production-ready security

### Environment Variables
- `FLASK_ENV`: `development` or `production`
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: Flask secret key
- `JWT_SECRET_KEY`: JWT signing key
- `PORT`: Server port (default: 5000)
- `HOST`: Server host (default: 0.0.0.0)

## 🚨 Security Features

### Authentication Security
- Password strength validation (8+ chars, uppercase, lowercase, numbers)
- JWT token expiration (24 hours by default)
- Refresh token support
- Role-based access control

### Database Security
- SQL injection protection via SQLAlchemy ORM
- Password hashing with Werkzeug
- Database connection pooling
- Migration version control

### API Security
- CORS configuration
- Request rate limiting ready
- Input validation
- Error handling without sensitive data exposure

## 📁 Project Structure

```
flask_backend/
├── models/                 # Database models
│   ├── __init__.py        # Model imports
│   ├── base.py            # Base model class
│   ├── user.py            # User models
│   ├── source.py          # Source model
│   ├── content.py         # Content model
│   ├── keyword.py         # Keyword model
│   ├── detection.py       # Detection model
│   ├── identifier.py      # Identifier model
│   ├── osint_result.py    # OSINT result model
│   ├── case.py            # Case model
│   └── user_case_link.py  # User-case relationships
├── routes/                # API routes
│   ├── auth.py           # Authentication routes
│   ├── sources.py        # Source management
│   ├── content.py        # Content analysis
│   ├── keywords.py       # Keyword management
│   ├── cases.py          # Case management
│   ├── users.py          # User management
│   ├── osint.py          # OSINT operations
│   └── dashboard.py      # Dashboard data
├── services/             # Business logic
│   ├── keyword_detector.py
│   ├── osint_handler.py
│   ├── osint_tools.py
│   └── scraper.py
├── migrations/           # Database migrations
├── uploads/              # File uploads
├── app.py               # Flask application factory
├── auth.py              # Authentication system
├── config.py            # Configuration classes
├── extensions.py        # Flask extensions
├── init_db.py           # Database initialization
├── run.py               # Application runner
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
└── README.md           # This file
```

## 🔄 Migration from Supabase

This backend has been completely migrated from Supabase to SQLAlchemy:

### Changes Made
1. **Database Layer**: Replaced Supabase client with SQLAlchemy ORM
2. **Authentication**: Migrated from Supabase Auth to JWT-based authentication
3. **Models**: Converted all models from Supabase queries to SQLAlchemy models
4. **Configuration**: Updated for PostgreSQL/SQLite support
5. **Dependencies**: Removed Supabase, added SQLAlchemy, PostgreSQL, JWT packages

### Data Migration
If migrating from existing Supabase data:
1. Export data from Supabase
2. Create mapping scripts for model differences
3. Import data using SQLAlchemy models
4. Update foreign key relationships

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/api`
2. Test database connectivity at `/test-db`
3. Verify health status at `/health`
4. Review logs for detailed error information

---

**Note**: This backend provides a complete REST API for cyber threat intelligence analysis and is ready for both development and production deployment.
