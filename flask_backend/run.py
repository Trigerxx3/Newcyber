#!/usr/bin/env python3
"""
Flask application runner
"""
from app import create_app
import os

def main():
    """Run the Flask application"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    try:
        app = create_app(config_name)
        
        debug = config_name == 'development'
        print(f"\n🚀 Starting Cyber Intelligence Platform API server...")
        print(f"   Environment: {config_name}")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Debug: {debug}")
        print(f"\n🌐 API URL: http://{host}:{port}")
        print(f"📋 Health check: http://{host}:{port}/health")
        print(f"📖 API docs: http://{host}:{port}/api")
        
        app.run(debug=debug, host=host, port=port, threaded=True)
        
    except Exception as e:
        print(f"❌ Failed to start Flask server: {e}")
        print("Make sure all dependencies are installed and database is accessible")
        raise

if __name__ == '__main__':
    main()
