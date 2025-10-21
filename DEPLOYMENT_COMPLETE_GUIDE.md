# ✅ Deployment Complete - Migration & Setup Guide

## What Was Done

### 1. ✅ Generated Database Migration
- Created initial migration script: `flask_backend/migrations/versions/d8729531dd5d_initial_schema_from_models.py`
- Added missing `script.py.mako` template
- Created `migrations/versions/` directory
- Migration includes the missing `case_content_links` table and fixes all schema mismatches

### 2. ✅ Applied Migration to Railway Database
- Successfully ran `alembic upgrade head` against Railway PostgreSQL
- All tables now match the Flask models (correct boolean types, foreign keys, etc.)
- Fixed the schema errors you were seeing in the logs

### 3. ✅ Seeded Admin User
- Created admin user in production database:
  - **Email:** `admin@cyber.com`
  - **Password:** `admin123456`
  - **Role:** Admin
- ⚠️ **Please change this password after your first login!**

### 4. ✅ Fixed CORS Configuration
- Resolved CORS error preventing production mode from starting
- Updated `flask_backend/app.py` to handle production CORS properly

### 5. ✅ Committed & Pushed to GitHub
- All changes committed and pushed to `master` branch
- Render will auto-deploy when it detects the new commits

---

## Next Steps for Render Deployment

### 1. Update Render Environment Variables

Go to your Render dashboard for the `narcointel1` service and ensure these are set:

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://postgres:GWexlGlzyawuhOotbpSviKOuraoLYmFb@maglev.proxy.rlwy.net:26614/railway
SECRET_KEY=<generate-a-strong-random-secret-32+-characters>
JWT_SECRET_KEY=<generate-another-strong-random-secret>
```

**Important Notes:**
- The `DATABASE_URL` above is your Railway database URL
- Generate strong random secrets for `SECRET_KEY` and `JWT_SECRET_KEY` in production
- You can generate secrets using: `openssl rand -hex 32` or any password generator

### 2. Update Render Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt && flask db upgrade
```

**Start Command (choose one):**
```bash
gunicorn run:app
```
Or if you don't have gunicorn:
```bash
python run.py
```

### 3. Trigger Render Redeployment

Since you've pushed to GitHub, Render should auto-deploy. If not:
1. Go to your Render dashboard
2. Click "Manual Deploy" → "Deploy latest commit"

### 4. Verify Deployment

Once deployed, test these endpoints:
- Health check: `https://narcointel1.onrender.com/api/health`
- Sign in: `https://narcointel1.onrender.com/api/auth/signin` (POST with admin credentials)

---

## Testing the Fix

### Test Sign-In API

Use this curl command or Postman:

```bash
curl -X POST https://narcointel1.onrender.com/api/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@cyber.com", "password": "admin123456"}'
```

You should get a response like:
```json
{
  "message": "Login successful",
  "access_token": "eyJ...",
  "user": {
    "id": 1,
    "email": "admin@cyber.com",
    "username": "admin",
    "role": "Admin"
  }
}
```

---

## For Local Development

If you want to test locally against your Railway database:

### Set Environment Variables (PowerShell)
```powershell
cd "D:\new cyber\flask_backend"
$env:FLASK_APP="run.py"
$env:FLASK_ENV="development"
$env:DATABASE_URL="postgresql://postgres:GWexlGlzyawuhOotbpSviKOuraoLYmFb@maglev.proxy.rlwy.net:26614/railway"
$env:SECRET_KEY="dev-secret-key-change-in-production-2024"
$env:JWT_SECRET_KEY="jwt-secret-key-change-in-production-2024"
python run.py
```

### Frontend Local Setup

In `cyber/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

Then start the frontend:
```powershell
cd "D:\new cyber\cyber"
npm run dev
```

---

## Files Changed in This Session

- ✅ `flask_backend/migrations/env.py` - Added missing model imports
- ✅ `flask_backend/migrations/script.py.mako` - Created migration template
- ✅ `flask_backend/migrations/versions/d8729531dd5d_initial_schema_from_models.py` - Initial migration
- ✅ `flask_backend/app.py` - Fixed production CORS configuration
- ✅ `flask_backend/seed_admin.py` - Created (for admin seeding, not in git)
- ✅ `flask_backend/create_migration.py` - Created (helper script, not in git)

---

## Troubleshooting

### If you still get 500 errors on /api/auth/signin:

1. **Check Render logs** for the specific error
2. **Verify DATABASE_URL** is correctly set on Render (copy-paste from Railway)
3. **Ensure migrations ran** - Check Render build logs for "Running upgrade"
4. **Verify SECRET_KEY and JWT_SECRET_KEY** are set on Render

### If migrations fail on Render:

The build command includes `flask db upgrade`. If it fails:
- Check that `FLASK_APP=run.py` is set
- Check that `DATABASE_URL` is correct and starts with `postgresql://`
- Manually run migrations from Render shell if available

### To check what's in your Railway database:

```bash
# Connect to Railway DB (you may need to install psql)
psql "postgresql://postgres:GWexlGlzyawuhOotbpSviKOuraoLYmFb@maglev.proxy.rlwy.net:26614/railway"

# List tables
\dt

# Check system_users table
SELECT * FROM system_users;

# Check active_cases table structure
\d active_cases
```

---

## Security Recommendations

After deployment:

1. **Change the admin password** immediately after first login
2. **Generate strong secrets** for `SECRET_KEY` and `JWT_SECRET_KEY` in production
3. **Add your frontend URL** to Render's `FRONTEND_URLS` environment variable
4. **Enable HTTPS only** for production API calls
5. **Consider rate limiting** for authentication endpoints

---

## Summary

✅ Database schema is now correctly migrated
✅ Admin user exists in the production database  
✅ Migration files are committed to git
✅ CORS issue is fixed
✅ Ready for Render to redeploy

**The 500 errors on `/api/auth/signin` should be resolved once Render redeploys with these changes!**

