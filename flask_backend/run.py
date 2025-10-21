"""
Flask development server runner
For local development with SQLite database
"""
import os
from app import create_app

# Always use development mode when running this script directly
app = create_app('development')

if __name__ == '__main__':
    import os
    use_prod_db = os.environ.get('USE_PRODUCTION_DB', '').lower() == 'true'
    
    print("=" * 60)
    print("🚀 Starting Flask Development Server")
    print("=" * 60)
    print("📍 Backend URL: http://127.0.0.1:5000")
    print("📍 Health Check: http://127.0.0.1:5000/api/health")
    
    if use_prod_db:
        print("🗄️  Database: Railway PostgreSQL (Production)")
    else:
        print("🗄️  Database: Local SQLite (cyber_intel.db)")
    
    print("👤 Admin Login: admin@cyber.com / admin123456")
    print("=" * 60)
    if not use_prod_db:
        print("💡 Tip: Set USE_PRODUCTION_DB=true to connect to Railway")
    print("=" * 60)
    print()
    
    # Run development server
    app.run(
        host='127.0.0.1',  # localhost only for development
        port=5000,
        debug=True  # Always debug mode in development
    )