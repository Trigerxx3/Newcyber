# 🚀 Deploy to Render + Vercel - Step by Step Guide

## 📋 **Overview**

This guide will help you deploy your Cyber Intelligence Platform:
- **Backend**: Flask API on Render
- **Frontend**: Next.js on Vercel
- **Features**: User Investigation with OSINT tools

## 🔧 **Step 1: Prepare Your Repository**

### 1.1 Push to GitHub

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 1.2 Repository Structure

Your repo should have:
```
your-repo/
├── flask_backend/          # Flask API
├── cyber/                  # Next.js frontend  
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment
├── render.yaml            # Render configuration
└── vercel.json            # Vercel configuration
```

## 🎯 **Step 2: Deploy Backend to Render**

### 2.1 Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Connect your repository

### 2.2 Deploy Web Service

1. **Click "New +"** → **"Web Service"**
2. **Connect Repository**: Select your GitHub repo
3. **Configure Service**:
   ```
   Name: cyber-intel-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python flask_backend/run.py
   ```

### 2.3 Environment Variables

Add these environment variables in Render dashboard:

```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=postgresql://... (Render provides this)
FRONTEND_URL=https://your-vercel-app.vercel.app
```

### 2.4 Deploy Database

1. **Click "New +"** → **"PostgreSQL"**
2. **Configure**:
   ```
   Name: cyber-intel-db
   Database: cyber_intel
   User: cyber_intel_user
   ```
3. **Copy the DATABASE_URL** from the database dashboard

### 2.5 Test Backend

After deployment, test your backend:
```bash
curl https://your-backend.onrender.com/api/health
```

Should return:
```json
{"status": "healthy", "message": "Cyber Intelligence Backend is running"}
```

## 🎨 **Step 3: Deploy Frontend to Vercel**

### 3.1 Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Import your repository

### 3.2 Configure Project

1. **Framework Preset**: Next.js
2. **Root Directory**: `cyber`
3. **Build Command**: `npm run build`
4. **Output Directory**: `.next`

### 3.3 Environment Variables

Add in Vercel dashboard:

```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### 3.4 Deploy

1. Click **"Deploy"**
2. Wait for build to complete
3. Get your frontend URL (e.g., `https://your-app.vercel.app`)

## 🔗 **Step 4: Connect Frontend to Backend**

### 4.1 Update Backend CORS

In Render dashboard, add environment variable:
```
FRONTEND_URL=https://your-app.vercel.app
```

### 4.2 Test Connection

Visit your frontend URL and test the User Investigation feature:
1. Go to `/dashboard/user-investigation`
2. Enter a username (e.g., "github")
3. Click "Start Investigation"
4. Should see results from OSINT tools

## 🎯 **Step 5: Production Features**

### 5.1 What Works in Production

✅ **User Investigation**:
- URL pattern checking (10+ platforms)
- GitHub API integration
- Fast results (5-15 seconds)
- Beautiful UI with tool attribution

✅ **All Other Features**:
- User authentication
- Case management
- Content analysis
- Admin dashboard

### 5.2 Performance

```
🔍 URL Checker: 10-15 profiles
🔍 GitHub API: Detailed user info
⚠️ Spiderfoot: Falls back gracefully
⏱️ Response Time: 5-15 seconds
```

## 🔧 **Step 6: Optional Enhancements**

### 6.1 Add Sherlock for More Platforms

In Render, add environment variable:
```
SHERLOCK_ENABLED=true
```

This will enable 400+ platform checking.

### 6.2 Custom Domain

1. **Vercel**: Add custom domain in project settings
2. **Render**: Add custom domain in service settings
3. **Update CORS**: Add new domain to `FRONTEND_URL`

## 📊 **Step 7: Monitor Your Deployment**

### 7.1 Render Monitoring

- **Logs**: View real-time logs
- **Metrics**: CPU, memory usage
- **Health**: Service uptime

### 7.2 Vercel Analytics

- **Performance**: Page load times
- **Usage**: User analytics
- **Functions**: API call metrics

## 🚨 **Troubleshooting**

### Common Issues:

#### Backend Won't Start
```bash
# Check logs in Render dashboard
# Common fixes:
pip install gunicorn  # Add to requirements.txt
```

#### CORS Errors
```bash
# Add your Vercel URL to FRONTEND_URL
# Restart Render service
```

#### Database Connection Issues
```bash
# Check DATABASE_URL format
# Should be: postgresql://user:pass@host:port/db
```

#### Frontend Can't Connect to Backend
```bash
# Verify NEXT_PUBLIC_API_URL is correct
# Check backend is running
```

## ✅ **Success Checklist**

- [ ] Backend deployed to Render
- [ ] Database connected and working
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS properly set up
- [ ] User Investigation feature working
- [ ] Authentication working
- [ ] All features tested

## 🎉 **You're Live!**

Your Cyber Intelligence Platform is now deployed and accessible worldwide!

**Frontend**: `https://your-app.vercel.app`
**Backend**: `https://your-backend.onrender.com`

### **Features Available:**
- 🔍 **User Investigation** with OSINT tools
- 👤 **User Management** and authentication
- 📊 **Case Management** system
- 🎯 **Content Analysis** with AI
- 📈 **Admin Dashboard** with analytics
- 🔐 **Secure API** with JWT authentication

**Congratulations! Your platform is production-ready!** 🚀
