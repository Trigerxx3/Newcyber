"""
Flask app using SQLAlchemy with PostgreSQL/SQLite
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Disable automatic trailing slash redirects to prevent CORS preflight issues
    app.url_map.strict_slashes = False
    
    # Configure CORS with comprehensive settings
    CORS(app, 
         origins=[
             'http://localhost:3000',
             'http://127.0.0.1:3000', 
             'http://localhost:9002',
             'http://127.0.0.1:9002',
             'http://localhost:9003',
             'http://127.0.0.1:9003'
         ],
         allow_headers=[
             'Content-Type', 
             'Authorization', 
             'X-Requested-With',
             'Accept',
             'Origin',
             'X-CSRF-Token'
         ],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         supports_credentials=True,
         send_wildcard=False,
         automatic_options=True)
    
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
                    admin.set_password('admin123456')  # Set password before adding to session
                    db.session.add(admin)
                    db.session.commit()
                else:
                    # Reset password on each boot in dev for predictable creds
                    admin.set_password('admin123456')
    except Exception as e:
        print(f"⚠️  Bootstrap admin failed: {e}")
    
    # Add global OPTIONS handler for CORS preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({})
            response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
            response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With,Accept,Origin,X-CSRF-Token")
            response.headers.add('Access-Control-Allow-Methods', "GET,POST,PUT,DELETE,OPTIONS,PATCH")
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            return response
    
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
        from routes.admin import admin_bp
        from routes.scraping import scraping_bp
        
        app.register_blueprint(sources_bp, url_prefix='/api/sources')
        app.register_blueprint(content_bp, url_prefix='/api/content')
        app.register_blueprint(osint_bp, url_prefix='/api/osint')
        app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
        app.register_blueprint(users_bp, url_prefix='/api/users')
        app.register_blueprint(cases_bp, url_prefix='/api/cases')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
        app.register_blueprint(scraping_bp, url_prefix='/api/scraping')
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



