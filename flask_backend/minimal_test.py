#!/usr/bin/env python3
"""
Absolute minimal Flask test with CORS
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
        return response

@app.route('/')
def home():
    return jsonify({"message": "Hello World! Flask is working!"})

@app.route('/health')
def health():
    return jsonify({"status": "success", "message": "Server is running", "database_connected": True})

@app.route('/api')
def api_root():
    return jsonify({"status": "success", "message": "API is working"})

@app.route('/api/health')
def api_health():
    return jsonify({"status": "success", "message": "API health OK", "database_connected": True})

if __name__ == '__main__':
    print("🚀 Starting Flask server with CORS...")
    print("📍 URL: http://127.0.0.1:5000")
    print("📍 Health: http://127.0.0.1:5000/health")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except Exception as e:
        print(f"❌ Server failed to start: {e}")

