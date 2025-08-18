# 🗄️ Single Database Deployment Guide
## SQLAlchemy-Only Architecture

Your project has been successfully migrated to use **SQLAlchemy as the single database approach**, eliminating the dual database complexity. Here's how to deploy it.

---

## 📊 **Current Architecture Overview**

### **✅ What We Have Now:**
```
Frontend (Next.js) ──► Flask Backend ──► SQLAlchemy ──► Database
                                                        ├── SQLite (Development)
                                                        └── PostgreSQL (Production)
```

### **🗑️ What We Removed:**
- ❌ Supabase client connections
- ❌ Dual authentication systems  
- ❌ Frontend database dependencies
- ❌ Supabase environment variables
- ❌ Conflicting data access patterns

---

## 🚀 **Deployment Options**

### **Option 1: Railway (Recommended)**
Railway provides the easiest deployment with automatic PostgreSQL:

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and init
railway login
railway init

# 3. Add PostgreSQL service
railway add postgresql

# 4. Deploy
railway deploy

# 5. Railway will automatically:
# - Set DATABASE_URL environment variable
# - Install psycopg2-binary for PostgreSQL
# - Handle SSL connections
```

**Environment Variables (Railway auto-sets DATABASE_URL):**
```env
SECRET_KEY=generate-secure-random-key
JWT_SECRET_KEY=generate-jwt-specific-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FLASK_ENV=production
```

---

### **Option 2: Heroku**
```bash
# 1. Create Heroku app
heroku create your-app-name

# 2. Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# 3. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set JWT_SECRET_KEY=your-jwt-key
heroku config:set GOOGLE_CLIENT_ID=your-client-id
heroku config:set GOOGLE_CLIENT_SECRET=your-client-secret
heroku config:set FLASK_ENV=production

# 4. Deploy
git push heroku main

# 5. Run migrations
heroku run flask db upgrade
```

---

### **Option 3: DigitalOcean App Platform**
Create `app.yaml`:
```yaml
name: cyber-intelligence
services:
- name: backend
  source_dir: flask_backend
  github:
    repo: your-username/your-repo
    branch: main
  run_command: python app.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    value: ${db.DATABASE_URL}
  - key: SECRET_KEY
    scope: RUN_AND_BUILD_TIME
    value: your-secret-key
  - key: JWT_SECRET_KEY
    scope: RUN_AND_BUILD_TIME
    value: your-jwt-key

databases:
- name: db
  engine: PG
  version: "14"
```

---

## 🛠️ **Pre-Deployment Setup**

### **1. Backend Configuration**
Your Flask backend is already configured for single database usage:

**✅ Enhanced Production Config (`config.py`):**
- PostgreSQL connection pooling
- SSL-required connections
- Environment validation
- Production logging

**✅ Updated Requirements (`requirements.txt`):**
- Added `psycopg2-binary==2.9.9` for PostgreSQL support
- All Flask extensions included

**✅ Migration System:**
- Flask-Migrate configured
- All models properly imported
- Ready for database initialization

### **2. Frontend Configuration**
**Create `cyber/.env.local`:**
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

For local development:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 🔧 **Database Initialization**

### **Development (SQLite)**
```bash
cd flask_backend
python app.py
# Automatically creates local.db and admin user
```

### **Production (PostgreSQL)**
```bash
# Set environment variables first
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-key"
export FLASK_ENV="production"

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Start application
python app.py
```

---

## 📋 **Environment Variables Checklist**

### **Required for Production:**
- [ ] `DATABASE_URL` - PostgreSQL connection string
- [ ] `SECRET_KEY` - Flask secret key (256-bit random)
- [ ] `JWT_SECRET_KEY` - JWT signing key (256-bit random)
- [ ] `FLASK_ENV=production`

### **Optional:**
- [ ] `GOOGLE_CLIENT_ID` - For Google OAuth
- [ ] `GOOGLE_CLIENT_SECRET` - For Google OAuth
- [ ] `JWT_ACCESS_TOKEN_EXPIRES=24` - Token expiry hours
- [ ] `UPLOAD_FOLDER=/app/uploads` - File upload directory
- [ ] `MAX_CONTENT_LENGTH=16777216` - Max upload size

---

## 🧪 **Testing the Setup**

### **1. Test Backend Health**
```bash
curl https://your-backend-url.com/health
# Expected: {"status": "healthy", "database_connected": true}
```

### **2. Test Authentication**
```bash
# Sign up
curl -X POST https://your-backend-url.com/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","username":"testuser"}'

# Sign in
curl -X POST https://your-backend-url.com/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### **3. Test Frontend Connection**
1. Deploy frontend to Vercel/Netlify
2. Set `NEXT_PUBLIC_API_URL` to your backend URL
3. Visit login page and test authentication

---

## 🔍 **Database Inspection**

### **Development (SQLite)**
```bash
cd flask_backend
python check_db.py
```

### **Production (PostgreSQL)**
```bash
# Connect via psql
psql $DATABASE_URL

# List tables
\dt

# Check system users
SELECT email, username, role FROM system_users;

# Check database size
SELECT pg_size_pretty(pg_database_size(current_database()));
```

---

## 📈 **Performance Optimization**

### **Connection Pooling**
Your production config already includes optimized settings:
- Pool size: 20 connections
- Max overflow: 50 connections  
- Connection recycling: 1 hour
- SSL required for security

### **Recommended Database Specs**
- **Development**: SQLite (built-in)
- **Production**: 
  - Small app: 1GB RAM, 25GB storage
  - Medium app: 2GB RAM, 50GB storage
  - Large app: 4GB RAM, 100GB storage

---

## 🚨 **Troubleshooting**

### **Common Issues:**

**1. PostgreSQL Driver Missing**
```bash
# If deployment fails with PostgreSQL errors:
pip install psycopg2-binary==2.9.9
```

**2. Database Connection Failed**
```bash
# Check DATABASE_URL format:
# Correct: postgresql://user:pass@host:port/db
# Wrong:   postgres://user:pass@host:port/db (old format)
```

**3. Frontend Can't Connect**
```bash
# Check CORS is enabled (already configured)
# Verify NEXT_PUBLIC_API_URL in frontend environment
```

**4. Authentication Errors**
```bash
# Clear browser localStorage and cookies
# Check JWT_SECRET_KEY is set in production
```

---

## ✅ **Success Criteria**

Your single database deployment is successful when:

- [ ] Backend health endpoint returns `database_connected: true`
- [ ] Frontend can successfully sign in/sign up
- [ ] Dashboard loads without database errors
- [ ] All API endpoints respond correctly
- [ ] Database tables are properly created
- [ ] Admin user can be created and authenticated

---

## 🎯 **Next Steps**

1. **Choose hosting platform** (Railway recommended)
2. **Deploy backend** with PostgreSQL database
3. **Deploy frontend** with backend URL configured
4. **Test authentication** end-to-end
5. **Monitor performance** and optimize as needed

Your project is now **production-ready** with a simplified, single database architecture! 🚀