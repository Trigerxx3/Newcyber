from flask import Blueprint, jsonify, request, current_app
from extensions import db
from sqlalchemy import text
from datetime import datetime

health_bp = Blueprint('health', __name__)


def _db_ok() -> bool:
    try:
        db.session.execute(text('SELECT 1')).fetchone()
        return True
    except Exception:
        return False


def _meta() -> dict:
    return {
        'service': 'Cyber Intelligence Platform API',
        'environment': current_app.config.get('FLASK_ENV', 'development'),
        'database_url': current_app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown'),
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    }


@health_bp.route('/health', methods=['GET', 'OPTIONS'])
def health_root():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    ok = _db_ok()
    return jsonify({
        'status': 'success' if ok else 'error',
        'message': 'OK' if ok else 'Database connection failed',
        'database_connected': ok,
        **_meta(),
    }), 200


@health_bp.route('/api/health', methods=['GET', 'OPTIONS'])
def health_api():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    ok = _db_ok()
    return jsonify({
        'status': 'success' if ok else 'error',
        'message': 'OK' if ok else 'Database connection failed',
        'database_connected': ok,
        **_meta(),
    }), 200


@health_bp.route('/api', methods=['GET', 'OPTIONS'])
def api_index():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    return jsonify({
        'status': 'success',
        'message': 'Cyber Intelligence Platform API',
        'version': '2.0.0',
        'database': 'SQLAlchemy with PostgreSQL/SQLite',
        'endpoints': {
            'auth': {
                'signup': 'POST /api/auth/signup',
                'signin': 'POST /api/auth/signin',
                'signout': 'POST /api/auth/signout',
                'profile': 'GET /api/auth/profile',
                'users': 'GET /api/auth/users (Admin only)'
            },
            'sources': 'GET/POST /api/sources',
            'users': 'GET/POST /api/users',
            'content': 'GET/POST /api/content',
            'cases': 'GET/POST /api/cases',
            'osint': 'POST /api/osint/investigate-user',
            'dashboard': 'GET /api/dashboard',
            'health': 'GET /health or GET /api/health'
        },
        **_meta(),
    }), 200

