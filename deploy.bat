@echo off
echo 🚀 Cyber Intelligence Platform Deployment
echo ========================================

REM Check if git is initialized
if not exist ".git" (
    echo ❌ Git not initialized. Please run:
    echo    git init
    echo    git add .
    echo    git commit -m "Initial commit"
    pause
    exit /b 1
)

REM Check if files exist
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found
    pause
    exit /b 1
)

if not exist "Procfile" (
    echo ❌ Procfile not found
    pause
    exit /b 1
)

if not exist "flask_backend" (
    echo ❌ flask_backend directory not found
    pause
    exit /b 1
)

if not exist "cyber" (
    echo ❌ cyber directory not found
    pause
    exit /b 1
)

echo ✅ All required files found!

REM Check git status
echo.
echo 📋 Git Status:
git status --porcelain

REM Ask for confirmation
echo.
set /p confirm="🤔 Ready to push to GitHub? (y/n): "
if /i not "%confirm%"=="y" (
    echo ❌ Deployment cancelled
    pause
    exit /b 1
)

REM Push to GitHub
echo.
echo 📤 Pushing to GitHub...
git add .
git commit -m "Deploy to production - Render + Vercel"
git push origin main

echo.
echo 🎉 Code pushed to GitHub!
echo.
echo 📋 Next Steps:
echo 1. 🌐 Go to https://render.com and deploy your backend
echo 2. 🎨 Go to https://vercel.com and deploy your frontend
echo 3. 🔗 Follow the instructions in DEPLOYMENT_INSTRUCTIONS.md
echo.
echo 🚀 Your Cyber Intelligence Platform will be live soon!
pause
