"""
Flask server runner - works for both local development and production
"""
import os
from app import create_app

# Determine environment
is_production = os.getenv('FLASK_ENV') == 'production' or os.getenv('RENDER') == 'true'
config_name = 'production' if is_production else 'development'

# Create Flask app
app = create_app(config_name)

if __name__ == '__main__':
    if is_production:
        # Production settings
        port = int(os.getenv('PORT', 10000))
        print(f"🚀 Starting Flask Production Server on port {port}")
        print(f"🗄️  Database: {os.getenv('DATABASE_URL', 'SQLite')}")
        
        app.run(
            host='0.0.0.0',  # Must bind to 0.0.0.0 for production
            port=port,
            debug=False
        )
    else:
        # Development settings
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