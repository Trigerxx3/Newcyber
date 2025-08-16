#!/usr/bin/env python3
"""
Simple Flask server for testing
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for your frontend port
CORS(app, 
     origins=['http://localhost:9002', 'http://localhost:3000'],
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
        return response, 200

@app.route('/health', methods=['GET', 'OPTIONS'])
def health():
    return jsonify({
        'status': 'success',
        'message': 'Flask backend is running',
        'database_connected': True
    })

@app.route('/api/health', methods=['GET', 'OPTIONS'])
def api_health():
    return jsonify({
        'status': 'success',
        'message': 'API health check OK',
        'database_connected': True
    })

@app.route('/api', methods=['GET', 'OPTIONS'])
def api_root():
    return jsonify({
        'status': 'success',
        'message': 'Simple Flask API is working',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Starting simple Flask server...")
    print("🌐 Server URL: http://localhost:5000")
    print("📋 Health check: http://localhost:5000/health")
    print("🔧 API root: http://localhost:5000/api")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")