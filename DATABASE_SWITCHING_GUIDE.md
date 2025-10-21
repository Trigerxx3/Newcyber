# 🔄 Database Switching Guide

Your setup now supports **both local SQLite and Railway PostgreSQL** with a simple toggle!

---

## 🏠 Local Development (Default - SQLite)

**Just run:**
```powershell
cd flask_backend
python run.py
```

**Uses:**
- ✅ Local SQLite database (`cyber_intel.db`)
- ✅ All credentials from `.env` file
- ✅ Fast, no internet needed
- ✅ Separate from production data

---

## 🌐 Connect to Railway Database (From Local)

**Set environment variable:**
```powershell
cd flask_backend
$env:USE_PRODUCTION_DB="true"
python run.py
```

**Uses:**
- ✅ Railway PostgreSQL (production database)
- ✅ Same data as deployed backend
- ✅ Credentials from `.env` file (`DATABASE_URL`)
- ⚠️ Changes affect production data!

---

## 🚀 Production (Render)

**Automatic - no changes needed!**

Render uses:
- ✅ `FLASK_ENV=production` (set in Render dashboard)
- ✅ Railway PostgreSQL from env vars
- ✅ Never touches local SQLite

---

## 📋 Your `.env` File

Keep your `.env` file with **ALL credentials**:

```env
# This stays in .env for both scenarios
DATABASE_URL=postgresql://postgres:GWexl...@maglev.proxy.rlwy.net:26614/railway

# All other credentials
SECRET_KEY=...
JWT_SECRET_KEY=...
GOOGLE_CLIENT_ID=...
TELEGRAM_API_ID=...
INSTAGRAM_USERNAME=...
# etc.
```

**The app automatically chooses**:
- No `USE_PRODUCTION_DB` set → Local SQLite ✅
- `USE_PRODUCTION_DB=true` → Railway PostgreSQL 🌐

---

## 🎯 Quick Reference

| Scenario | Command | Database Used |
|----------|---------|---------------|
| **Local Dev** | `python run.py` | SQLite (local) |
| **Test with Prod DB** | `$env:USE_PRODUCTION_DB="true"; python run.py` | Railway PostgreSQL |
| **Production (Render)** | Automatic | Railway PostgreSQL |

---

## 💡 Tips

### Keep databases in sync (migrations)

**Local SQLite:**
```powershell
# Make sure USE_PRODUCTION_DB is NOT set
alembic upgrade head
```

**Railway PostgreSQL:**
```powershell
$env:USE_PRODUCTION_DB="true"
alembic upgrade head
```

### Switch back to local SQLite
```powershell
Remove-Item Env:\USE_PRODUCTION_DB
python run.py
```

### Commit your changes
```bash
git add flask_backend/config.py flask_backend/run.py
git commit -m "Add smart database switching for dev/prod"
git push origin master
```

**Note:** Your `.env` file is gitignored and will NOT be committed (this is correct!)

---

## ✅ Benefits

- ✅ **One `.env` file** with all credentials
- ✅ **Easy switching** with one environment variable
- ✅ **Safe local development** (default = SQLite)
- ✅ **Test with production data** when needed
- ✅ **Production unchanged** (still uses Railway)

---

## 🔐 Security

- `.env` file is **gitignored** ✅
- Never committed to GitHub ✅
- Each developer has their own `.env` ✅
- Production uses Render's environment variables ✅

---

**Now you can develop locally with SQLite and switch to Railway when needed!** 🎉

