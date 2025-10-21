# 🚀 Local Development - Complete Setup Guide

Your development environment is now **fully configured** to work seamlessly with both local SQLite and Railway PostgreSQL!

---

## ✅ What's Configured

### 1. **Smart Database Switching**
- **Default**: Local SQLite (safe for development)
- **Optional**: Railway PostgreSQL (when you need production data)
- **Toggle**: One environment variable (`USE_PRODUCTION_DB`)

### 2. **Session Persistence**
- Instagram: ✅ No verification codes needed (session saved)
- Telegram: ✅ Automatic session management
- All scrapers: ✅ Login once, reuse forever

### 3. **Unified Environment**
- One `.env` file with ALL credentials
- Works for both local and production
- No need to swap files or edit configs

---

## 🎯 Quick Start (Local Development)

### Step 1: Start Backend (Flask)

Open **Terminal 1**:
```powershell
cd "D:\new cyber\flask_backend"
python run.py
```

**Expected output:**
```
============================================================
🚀 Starting Flask Development Server
============================================================
📍 Backend URL: http://127.0.0.1:5000
📍 Health Check: http://127.0.0.1:5000/api/health
🗄️  Database: Local SQLite (cyber_intel.db)
👤 Admin Login: admin@cyber.com / admin123456
============================================================
💡 Tip: Set USE_PRODUCTION_DB=true to connect to Railway
============================================================
✅ Loaded saved Instagram session for: cyber_intel0
🔥 REAL INSTAGRAM SCRAPING IS NOW ACTIVE!
 * Running on http://127.0.0.1:5000
```

**Keep this terminal open!**

---

### Step 2: Start Frontend (Next.js)

Open **Terminal 2**:
```powershell
cd "D:\new cyber\cyber"
npm run dev
```

**Expected output:**
```
▲ Next.js 15.5.6 (Turbopack)
- Local:        http://localhost:9002
```

**Keep this terminal open!**

---

### Step 3: Access Application

Open browser: **http://localhost:9002**

**Login with:**
- Email: `admin@cyber.com`
- Password: `admin123456`

---

## 🔄 Database Switching

### Local SQLite (Default) ✅

**Use when:**
- Developing new features
- Testing locally
- Don't want to affect production

**Command:**
```powershell
cd "D:\new cyber\flask_backend"
python run.py
```

**Uses:** `cyber_intel.db` (local SQLite file)

---

### Railway PostgreSQL (Production Data) 🌐

**Use when:**
- Testing with production data
- Debugging production issues
- Running migrations on production

**Command:**
```powershell
cd "D:\new cyber\flask_backend"
$env:USE_PRODUCTION_DB="true"
python run.py
```

**Uses:** Railway PostgreSQL from `.env` file

⚠️ **Warning:** Changes affect production database!

---

## 🗄️ Database Migrations

### Create New Migration

When you change models:
```powershell
cd "D:\new cyber\flask_backend"
alembic revision --autogenerate -m "description of changes"
```

### Apply Migrations Locally (SQLite)

```powershell
cd "D:\new cyber\flask_backend"
alembic upgrade head
```

**Output:**
```
💾 Alembic: Using local SQLite database
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
```

### Apply Migrations to Production (Railway)

```powershell
cd "D:\new cyber\flask_backend"
$env:USE_PRODUCTION_DB="true"
alembic upgrade head
```

**Output:**
```
🌐 Alembic: Using Railway PostgreSQL database
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
```

---

## 📁 File Structure

```
flask_backend/
├── .env                    ✅ ALL credentials (local + production)
├── cyber_intel.db          💾 Local SQLite database
├── instagram_session.json  🔐 Instagram session (gitignored)
├── telegram_session.session 🔐 Telegram session (gitignored)
├── run.py                  🚀 Development server entry point
├── config.py               ⚙️ Smart database config
└── migrations/
    └── env.py              ⚙️ Smart migration config
```

---

## 🔐 Environment Variables

Your `.env` file contains **everything**:

```env
# Database (for production - ignored in local dev by default)
DATABASE_URL=postgresql://postgres:...@maglev.proxy.rlwy.net:26614/railway

# Flask Secrets
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your-app-password

# Frontend
FRONTEND_URL=http://localhost:9002

# Social Media Scrapers
INSTAGRAM_USERNAME=cyber_intel0
INSTAGRAM_PASSWORD=your-instagram-password
TELEGRAM_API_ID=your-api-id
TELEGRAM_API_HASH=your-api-hash
# ... and more
```

**The app automatically chooses:**
- `USE_PRODUCTION_DB` not set → SQLite
- `USE_PRODUCTION_DB=true` → PostgreSQL from DATABASE_URL

---

## 🎮 Common Commands

### Start Development (Both Servers)

**Terminal 1 (Backend):**
```powershell
cd "D:\new cyber\flask_backend"
python run.py
```

**Terminal 2 (Frontend):**
```powershell
cd "D:\new cyber\cyber"
npm run dev
```

### Stop Servers

Press `Ctrl+C` in each terminal

Or force-kill Python:
```powershell
Stop-Process -Name python -Force
```

### Reset Local Database

```powershell
cd "D:\new cyber\flask_backend"
Remove-Item cyber_intel.db
alembic upgrade head
python run.py
```

### Clear Instagram Session (Re-login)

```powershell
cd "D:\new cyber\flask_backend"
Remove-Item instagram_session.json
python run.py
```

---

## 🐛 Troubleshooting

### Backend Error: "no such table: system_users"

**Problem:** Database tables not created

**Solution:**
```powershell
cd "D:\new cyber\flask_backend"
alembic upgrade head
python run.py
```

### Frontend Error: "Request timeout"

**Problem:** Backend not running

**Solution:**
```powershell
# Check if backend is running
curl http://127.0.0.1:5000/api/health

# If not, start it
cd "D:\new cyber\flask_backend"
python run.py
```

### Instagram Asks for Verification Again

**Problem:** Session expired (normal every few weeks)

**Solution:**
- Just enter the verification code
- New session will be saved automatically
- Won't ask again for weeks

### Alembic Using Wrong Database

**Problem:** Migrations going to wrong database

**Solution:**
```powershell
# Check what Alembic will use
cd "D:\new cyber\flask_backend"
alembic upgrade head

# Should show:
# 💾 Alembic: Using local SQLite database  ← Correct for local
# or
# 🌐 Alembic: Using Railway PostgreSQL     ← Only if USE_PRODUCTION_DB=true
```

### Google Login Not Working

**Problem:** OAuth redirect URI mismatch

**Solution:** Update Google Cloud Console:
1. Go to: https://console.cloud.google.com
2. Select your project
3. APIs & Services → Credentials
4. Edit OAuth 2.0 Client
5. Add Authorized Redirect URIs:
   - `http://127.0.0.1:5000/api/auth/google/callback`
   - `http://localhost:9002`
   - `https://narcointel1.onrender.com/api/auth/google/callback` (production)

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Development                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend (Next.js)          Backend (Flask)                │
│  localhost:9002        ←→    127.0.0.1:5000                 │
│                              │                               │
│                              ▼                               │
│                         SQLite (local)                       │
│                         cyber_intel.db                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Production Deployment                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Frontend (Vercel)         Backend (Render)                 │
│  your-app.vercel.app  ←→   narcointel1.onrender.com        │
│                             │                                │
│                             ▼                                │
│                        PostgreSQL (Railway)                  │
│                        maglev.proxy.rlwy.net                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist: Is Everything Working?

- [ ] Backend starts: `python run.py` shows "Running on http://127.0.0.1:5000"
- [ ] Frontend starts: `npm run dev` shows "Local: http://localhost:9002"
- [ ] Health check works: Visit http://127.0.0.1:5000/api/health
- [ ] Login works: Email `admin@cyber.com`, Password `admin123456`
- [ ] Instagram session loaded: See "✅ Loaded saved Instagram session"
- [ ] No verification codes: Instagram doesn't ask for code
- [ ] Database created: File `cyber_intel.db` exists (45+ KB)

---

## 🎉 You're All Set!

Your development environment is **production-ready** with:
- ✅ Smart database switching (local ↔ production)
- ✅ Session persistence (no verification codes)
- ✅ One unified `.env` file
- ✅ Easy migrations (Alembic)
- ✅ Complete isolation (local changes don't affect production)

**Happy coding!** 🚀

---

## 📝 Quick Reference Card

| Task | Command |
|------|---------|
| **Start backend** | `cd flask_backend` → `python run.py` |
| **Start frontend** | `cd cyber` → `npm run dev` |
| **Run migrations (local)** | `alembic upgrade head` |
| **Run migrations (production)** | `$env:USE_PRODUCTION_DB="true"` → `alembic upgrade head` |
| **Use production DB locally** | `$env:USE_PRODUCTION_DB="true"` → `python run.py` |
| **Reset local DB** | `Remove-Item cyber_intel.db` → `alembic upgrade head` |
| **Clear Instagram session** | `Remove-Item instagram_session.json` |

---

**Need help? Check the logs!**
- Backend logs: In the terminal running `python run.py`
- Frontend logs: In the terminal running `npm run dev` or browser console
- Database issues: Run `alembic upgrade head` first

**Everything is automatic - just run and code!** 🎊

