"""
Flask app using SQLAlchemy with PostgreSQL/SQLite
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import fnmatch

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Disable automatic trailing slash redirects to prevent CORS preflight issues
    app.url_map.strict_slashes = False
    
    # Configure CORS with comprehensive settings
    explicit_origins = [
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:9002',
        'http://127.0.0.1:9002',
        'http://localhost:9003',
        'http://127.0.0.1:9003',
        # Known Vercel deployments
        'https://cyber-605eu5nyd-athul-s-projects.vercel.app',
        'https://cyber-kohl-two.vercel.app',
        'https://cyber-euiexr8oc-athul-s-projects.vercel.app'
    ]

    # Wildcard patterns allowed (evaluated via fnmatch)
    wildcard_patterns = [
        'https://*.vercel.app',
        'https://*.vercel.com'
    ]

    # Add production frontend URLs from env (comma-separated)
    if os.getenv('FRONTEND_URL'):
        explicit_origins.append(os.getenv('FRONTEND_URL').strip())
    if os.getenv('FRONTEND_URLS'):
        for o in os.getenv('FRONTEND_URLS').split(','):
            if o.strip():
                explicit_origins.append(o.strip())

    def is_allowed_origin(origin: str) -> bool:
        if not origin:
            return False
        if origin in explicit_origins:
            return True
        for pattern in wildcard_patterns:
            if fnmatch.fnmatch(origin, pattern):
                return True
        return False

    # CORS setup
    if os.getenv('FLASK_ENV') != 'production':
        CORS(app,
             origins="*",
             allow_headers=[
                 'Content-Type',
                 'Authorization',
                 'X-Requested-With',
                 'Accept',
                 'Origin',
                 'X-CSRF-Token'
             ],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
             supports_credentials=True)
    else:
        # In production, allow all but rely on after_request to echo allowed Origin
        CORS(app,
             resources={r"/api/*": {"origins": "*"}, r"/health": {"origins": "*"}},
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
             send_wildcard=True,
             automatic_options=True)
    
    # Manual CORS headers as backup (and to ensure correct Origin echoing)
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if is_allowed_origin(origin):
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Vary'] = 'Origin'
        else:
            # Fallback for non-browser or dev tools
            response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Accept,Origin,X-CSRF-Token'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS,PATCH'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '86400'
        return response
    
    # Add a simple health check endpoint for debugging
    @app.route('/')
    def root():
        return jsonify({
            'status': 'running',
            'message': 'Narcotics Intelligence Platform API',
            'version': '1.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'cases': '/api/cases'
            }
        })
    
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running',
            'cors_origins': explicit_origins,
            'wildcard_patterns': wildcard_patterns,
            'flask_env': os.getenv('FLASK_ENV', 'development')
        })
    
    # Load configuration
    try:
        app.config.from_object(f'config.{config_name.title()}Config')
    except ImportError:
        # Fallback configuration if config file doesn't exist
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Production database configuration
    if os.getenv('FLASK_ENV') == 'production':
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            # Handle PostgreSQL URL format for Render
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Initialize extensions
    try:
        from extensions import init_extensions
        init_extensions(app)
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize extensions: {e}")
    
    # Ensure critical auxiliary tables exist (safe for dev; no-op if already migrated)
    try:
        from extensions import db
        from sqlalchemy import inspect
        from models.active_case import ActiveCase
        with app.app_context():
            inspector = inspect(db.engine)
            existing = set(inspector.get_table_names())
            if 'active_cases' not in existing:
                print('ℹ️  Creating missing table: active_cases')
                ActiveCase.__table__.create(db.engine, checkfirst=True)
    except Exception as e:
        print(f"⚠️  Could not verify/create auxiliary tables: {e}")
    
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
            origin = request.headers.get('Origin')
            if is_allowed_origin(origin):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Vary'] = 'Origin'
            else:
                response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = "Content-Type,Authorization,X-Requested-With,Accept,Origin,X-CSRF-Token"
            response.headers['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS,PATCH"
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '86400'
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

    # Individually register each API blueprint to avoid all-or-nothing failures
    def safe_register(import_path: str, var_name: str, url_prefix: str):
        try:
            module = __import__(import_path, fromlist=[var_name])
            bp = getattr(module, var_name)
            app.register_blueprint(bp, url_prefix=url_prefix)
            print(f"✅ Registered {import_path} at {url_prefix}")
        except Exception as e:
            print(f"⚠️  Warning: Failed to register {import_path}: {e}")

    safe_register('routes.auth', 'auth_bp', '/api/auth')
    safe_register('routes.sources', 'sources_bp', '/api/sources')
    safe_register('routes.content', 'content_bp', '/api/content')
    safe_register('routes.content_analysis', 'content_analysis_bp', '/api/content-analysis')
    safe_register('routes.osint', 'osint_bp', '/api/osint')
    safe_register('routes.dashboard', 'dashboard_bp', '/api/dashboard')
    safe_register('routes.users', 'users_bp', '/api/users')
    safe_register('routes.cases', 'cases_bp', '/api/cases')
    safe_register('routes.reports', 'reports_bp', '/api/reports')
    safe_register('routes.admin', 'admin_bp', '/api/admin')
    safe_register('routes.scraping', 'scraping_bp', '/api/scraping')
    safe_register('routes.instagram', 'instagram_bp', '/api')
    
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
                'content-analysis': '/api/content-analysis/*',
                'osint': '/api/osint',
                'dashboard': '/api/dashboard',
                'cases': '/api/cases',
                'reports': '/api/reports'
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
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)



