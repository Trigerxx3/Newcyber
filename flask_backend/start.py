#!/usr/bin/env python3
"""
Simple Flask server startup with dependency checking
"""
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['flask', 'flask_cors']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install flask flask-cors")
        return False
    
    return True

def main():
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print("\n🚀 Starting Flask server...")
    
    # Simple Flask app
    from flask import Flask, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app, origins=['http://localhost:3000'])
    
    @app.route('/health')
    @app.route('/api/health')
    def health():
        return jsonify({
            'status': 'success',
            'message': 'Flask backend is running',
            'service': 'Cyber Intelligence Platform API'
        })
    
    @app.route('/api')
    def api_root():
        return jsonify({
            'status': 'success',
            'message': 'Simple Flask API is running',
            'endpoints': {
                'health': '/health or /api/health'
            }
        })
    
    print("🌐 Server starting on http://localhost:5000")
    print("📋 Health check: http://localhost:5000/health")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()