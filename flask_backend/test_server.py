#!/usr/bin/env python3
"""
Minimal test server to verify Flask is working
"""
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=[
    'http://localhost:3000',
    'http://localhost:9002',
    'http://127.0.0.1:9002'
])

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS")
        return response

@app.route('/health')
def health():
    return jsonify({'status': 'success', 'message': 'Test server is running'})

@app.route('/api/health')
def api_health():
    return jsonify({'status': 'success', 'message': 'API health check OK'})

@app.route('/api')
def api_root():
    return jsonify({'message': 'Minimal Flask API is working'})

if __name__ == '__main__':
    print("🚀 Starting minimal test server on http://localhost:5000")
    print("🌐 CORS enabled for http://localhost:9002")
    app.run(debug=True, host='0.0.0.0', port=5000)