"""
Flask app using SQLAlchemy with PostgreSQL/SQLite
"""
from flask import Flask, jsonify, request
import os

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Add global CORS preflight handler
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({})
            # Dynamically reflect origin for preflight to avoid wildcard conflicts
            origin = request.headers.get('Origin')
            allowed_origins = {
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost:9002',
                'http://127.0.0.1:9002',
                'http://localhost:9003',
                'http://127.0.0.1:9003',
            }
            if origin in allowed_origins:
                response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
            response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
            response.headers['Access-Control-Max-Age'] = '600'
            return response

    # Add CORS headers to all responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        allowed_origins = {
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:9002',
            'http://127.0.0.1:9002',
            'http://localhost:9003',
            'http://127.0.0.1:9003',
        }

        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
        # Only set credentials when origin is explicitly allowed
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
        response.headers['Access-Control-Max-Age'] = '600'
        return response
    
    # Load configuration
    try:
        app.config.from_object(f'config.{config_name.title()}Config')
    except ImportError:
        # Fallback configuration if config file doesn't exist
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    try:
        from extensions import init_extensions
        init_extensions(app)
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize extensions: {e}")
    
    # Development bootstrap: ensure a default admin exists
    try:
        from extensions import db
        from models.user import SystemUser, SystemUserRole
        env = app.config.get('ENV', 'development')
        if env == 'development':
            with app.app_context():
                admin_email = 'admin@cyber.com'
                admin = SystemUser.get_by_email(admin_email)
                if not admin:
                    admin = SystemUser(email=admin_email, username='admin', role=SystemUserRole.ADMIN)
                    db.session.add(admin)
                    db.session.commit()
                # Reset password on each boot in dev for predictable creds
                admin.set_password('admin123456')
    except Exception as e:
        print(f"⚠️  Bootstrap admin failed: {e}")
    
    # Register blueprints
    try:
        from routes.health import health_bp
        app.register_blueprint(health_bp)
        print("✅ Health routes registered")
    except ImportError as e:
        print(f"⚠️  Warning: Could not import health routes: {e}")
        # Create a simple health endpoint as fallback
        @app.route('/health')
        @app.route('/api/health')
        def health():
            return jsonify({
                'status': 'success',
                'message': 'Flask backend is running',
                'service': 'Cyber Intelligence Platform API'
            })
    
    try:
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        print("✅ Auth routes registered")
    except ImportError as e:
        print(f"⚠️  Warning: Could not import auth routes: {e}")
    
    try:
        from routes.sources import sources_bp
        from routes.content import content_bp
        from routes.osint import osint_bp
        from routes.dashboard import dashboard_bp
        from routes.users import users_bp
        from routes.cases import cases_bp
        
        app.register_blueprint(sources_bp, url_prefix='/api/sources')
        app.register_blueprint(content_bp, url_prefix='/api/content')
        app.register_blueprint(osint_bp, url_prefix='/api/osint')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        app.register_blueprint(users_bp, url_prefix='/api/users')
        app.register_blueprint(cases_bp, url_prefix='/api/cases')
        print("✅ All API routes registered")
    except ImportError as e:
        print(f"⚠️  Warning: Could not import some API routes: {e}")
    
    # Add a simple API root endpoint
    @app.route('/api')
    def api_root():
        return jsonify({
            'status': 'success',
            'message': 'Cyber Intelligence Platform API',
            'version': '2.0.0',
            'endpoints': {
                'health': '/health or /api/health',
                'auth': '/api/auth/*',
                'sources': '/api/sources',
                'content': '/api/content',
                'osint': '/api/osint',
                'dashboard': '/api/dashboard'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)



