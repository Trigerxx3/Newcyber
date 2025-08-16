from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import text

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
jwt = JWTManager()

def init_extensions(app):
    """Initialize Flask extensions"""
    # Initialize SQLAlchemy
    db.init_app(app)
    
    # Initialize Flask-Migrate
    migrate.init_app(app, db)
    
    # Initialize JWT Manager
    jwt.init_app(app)
    
    # Initialize CORS with explicit settings to satisfy preflight
    cors.init_app(
        app,
        resources={r"/*": {"origins": [
            "http://localhost:3000",
            "http://localhost:9002",
            "http://127.0.0.1:9002",
            "http://127.0.0.1:3000",
        ]}},
        supports_credentials=True,
        expose_headers=["Content-Type", "Authorization"],
        allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        max_age=600,
    )
    
    # Test database connection on startup
    with app.app_context():
        try:
            # Test the database connection
            result = db.session.execute(text('SELECT 1'))
            result.fetchone()
            print(f"✅ Database connection successful! Using: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Unknown')}")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            print("Make sure your database is running and DATABASE_URL is set correctly")
