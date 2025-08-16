from flask import Flask
from config import config
from extensions import init_extensions
import os

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # Initialize extensions
    init_extensions(app)

    # Import models to ensure they are registered with SQLAlchemy
    # Explicit imports to satisfy linters
    from models.user import User, SystemUser, SystemUserRole
    from models.source import Source
    from models.content import Content
    from models.keyword import Keyword
    from models.detection import Detection
    from models.identifier import Identifier
    from models.osint_result import OSINTResult
    from models.case import Case
    from models.user_case_link import UserCaseLink
    from models.osint_identifier_link import OSINTIdentifierLink

    # Bootstrap: ensure at least one admin exists in dev
    try:
        from extensions import db
        if app.config.get('ENV') == 'development':
            # Ensure default admin exists with known credentials
            admin_email = 'admin@cyber.com'
            admin = SystemUser.get_by_email(admin_email)
            if not admin:
                admin = SystemUser(email=admin_email, username='admin', role=SystemUserRole.ADMIN)
                db.session.add(admin)
                db.session.commit()
            # Always reset password in dev so creds are predictable
            admin.set_password('admin123456')
    except Exception:
        pass

    # Register blueprints
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

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Flask backend is running'}

    return app 