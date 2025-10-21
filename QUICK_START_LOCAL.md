# 🚀 Quick Start - Local Development

## Prerequisites
- Python 3.12+
- Node.js 18+
- Git

---

## 🏃‍♂️ Start Development (2 Simple Steps)

### 1️⃣ Start Backend (Flask)

```powershell
cd flask_backend
python run.py
```

**That's it!** The backend will:
- ✅ Use local SQLite database automatically
- ✅ Create admin user: `admin@cyber.com` / `admin123456`
- ✅ Run at: http://127.0.0.1:5000

You'll see:
```
============================================================
🚀 Starting Flask Development Server
============================================================
📍 Backend URL: http://127.0.0.1:5000
📍 Health Check: http://127.0.0.1:5000/api/health
🗄️  Database: Local SQLite (flask_backend/cyber_intel.db)
👤 Admin Login: admin@cyber.com / admin123456
============================================================
```

### 2️⃣ Start Frontend (Next.js) - New Terminal

```powershell
cd cyber
npm run dev
```

Frontend runs at: http://localhost:9002

---

## 🔑 Login

1. Go to http://localhost:9002
2. Sign in with:
   - **Email**: `admin@cyber.com`
   - **Password**: `admin123456`

---

## ⚙️ Configuration

### Backend `.env` (Optional)
Create `flask_backend/.env` if you need custom settings:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Frontend `.env.local`
Create `cyber/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:5000
```

---

## 📦 Database

- **Location**: `flask_backend/cyber_intel.db`
- **Type**: SQLite (file-based, no server needed)
- **Migrations**: Run automatically on first start

To reset database:
```powershell
cd flask_backend
rm cyber_intel.db
python run.py  # Will recreate fresh database
```

---

## 🛠️ Common Tasks

### Install Dependencies

**Backend**:
```powershell
cd flask_backend
pip install -r requirements.txt
```

**Frontend**:
```powershell
cd cyber
npm install
```

### Run Database Migrations
```powershell
cd flask_backend
alembic upgrade head
```

### Check Backend Health
Visit: http://127.0.0.1:5000/api/health

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 5000 is already in use
- Verify Python 3.12+ is installed: `python --version`
- Install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- Check if port 9002 is already in use
- Verify Node.js 18+ is installed: `node --version`
- Install dependencies: `npm install`
- Delete `.next` folder and try again

### Can't login
- Ensure backend is running at http://127.0.0.1:5000
- Check `cyber/.env.local` has `NEXT_PUBLIC_API_URL=http://127.0.0.1:5000`
- Try default credentials: `admin@cyber.com` / `admin123456`

### CORS errors
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Restart both backend and frontend

---

## 🎯 What's Running?

| Service | URL | Port |
|---------|-----|------|
| **Backend API** | http://127.0.0.1:5000 | 5000 |
| **Frontend** | http://localhost:9002 | 9002 |
| **Database** | `cyber_intel.db` (file) | N/A |

---

## 📝 Notes

- **No production setup needed** - `run.py` is development-only
- **No DATABASE_URL needed** - SQLite is used automatically
- **Admin user auto-created** - Login immediately after first start
- **Hot reload enabled** - Backend auto-restarts on code changes

---

## 🚀 Next Steps

Once local development is working:
- For production deployment, see `DEPLOYMENT_COMPLETE_GUIDE.md`
- To use Railway database locally, set `DATABASE_URL` env variable
- For production setup on Render, use `gunicorn run:app`

---

**Ready to code? Just run `python run.py` and `npm run dev`!** 🎉

