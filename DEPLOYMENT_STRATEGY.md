# Render Deployment Strategy

## Phase 1: Initial Deployment (Without Sherlock)
1. Use `requirements_minimal.txt`
2. Deploy to Render with these settings:
   - Root Directory: `flask_backend`
   - Build Command: `pip install --upgrade pip setuptools wheel && pip install -r requirements_minimal.txt`
   - Publish Directory: `flask_backend`
   - Start Command: `python run.py`

## Phase 2: Add Sherlock (After Successful Deployment)
1. Test that your app is working
2. Update requirements.txt to `requirements_with_sherlock.txt`
3. Redeploy with these settings:
   - Root Directory: `flask_backend`
   - Build Command: `pip install --upgrade pip setuptools wheel && pip install numpy>=1.24.0 && pip install --only-binary=all pandas>=2.2.0 && pip install -r requirements_with_sherlock.txt`
   - Publish Directory: `flask_backend`
   - Start Command: `python run.py`

## Alternative: Manual Installation
If automatic installation fails, you can:
1. SSH into your Render instance
2. Run: `pip install pandas>=2.2.0 sherlock-project>=0.14.1`
3. Restart your service

## Fallback: Disable Sherlock Features
If sherlock continues to cause issues:
1. Comment out sherlock imports in your code
2. Add feature flags to disable OSINT features
3. Deploy without sherlock functionality
