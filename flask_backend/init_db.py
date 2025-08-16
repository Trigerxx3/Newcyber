#!/usr/bin/env python3
"""
Database initialization script
This script initializes the database with tables and creates an admin user
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from extensions import db, init_extensions
from config import config
from models import *
from auth import Auth

def create_app():
    """Create Flask application"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    return app

def initialize_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Initializing database...")
        
        # Check if migrations directory exists
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        if not os.path.exists(migrations_dir):
            print("Initializing Flask-Migrate...")
            try:
                from flask_migrate import init
                init(directory='migrations')
                print("✅ Flask-Migrate initialized successfully!")
            except Exception as e:
                print(f"❌ Error initializing Flask-Migrate: {e}")
                return False
        
        try:
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Skip migration creation for now - just use db.create_all()
            print("✅ Database initialization completed!")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
        
        return True

def create_admin_user():
    """Create initial admin user"""
    app = create_app()
    
    with app.app_context():
        print("\nCreating admin user...")
        
        # Check if admin already exists
        admin = SystemUser.get_by_email('admin@cyber-intel.com')
        if admin:
            print("✅ Admin user already exists!")
            return True
        
        try:
            # Create admin user
            result = Auth.register_user(
                email='admin@cyber-intel.com',
                password='AdminPass123!',
                username='admin',
                role='Admin'
            )
            
            if result['success']:
                print("✅ Admin user created successfully!")
                print("   Email: admin@cyber-intel.com")
                print("   Password: AdminPass123!")
                print("   Username: admin")
                print("   Role: Admin")
                print("\n⚠️  IMPORTANT: Change the default password after first login!")
                return True
            else:
                print(f"❌ Error creating admin user: {result['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            return False

def create_sample_data():
    """Create sample data for testing"""
    app = create_app()
    
    with app.app_context():
        print("\nCreating sample data...")
        
        try:
            # Create sample sources
            if Source.query.count() == 0:
                sample_sources = [
                    Source(
                        platform=PlatformType.TELEGRAM,
                        source_handle='@cyberthreat_intel',
                        source_name='Cyber Threat Intelligence',
                        source_type=SourceType.CHANNEL,
                        description='Telegram channel for cyber threat intelligence'
                    ),
                    Source(
                        platform=PlatformType.INSTAGRAM,
                        source_handle='@security_news',
                        source_name='Security News',
                        source_type=SourceType.PROFILE,
                        description='Instagram profile sharing security news'
                    )
                ]
                
                for source in sample_sources:
                    db.session.add(source)
                
                db.session.commit()
                print("✅ Sample sources created!")
            
            # Create sample keywords
            if Keyword.query.count() == 0:
                sample_keywords = [
                    Keyword(
                        keyword='malware',
                        description='Malicious software',
                        type=KeywordType.MALWARE,
                        severity=KeywordSeverity.HIGH
                    ),
                    Keyword(
                        keyword='ransomware',
                        description='Ransom malware',
                        type=KeywordType.MALWARE,
                        severity=KeywordSeverity.CRITICAL
                    ),
                    Keyword(
                        keyword='data breach',
                        description='Security incident involving data exposure',
                        type=KeywordType.THREAT,
                        severity=KeywordSeverity.HIGH
                    )
                ]
                
                for keyword in sample_keywords:
                    db.session.add(keyword)
                
                db.session.commit()
                print("✅ Sample keywords created!")
            
            print("✅ Sample data creation completed!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating sample data: {e}")
            return False

def main():
    """Main initialization function"""
    print("=" * 60)
    print("🚀 Cyber Intelligence Platform - Database Initialization")
    print("=" * 60)
    
    # Initialize database
    if not initialize_database():
        print("\n❌ Database initialization failed!")
        sys.exit(1)
    
    # Create admin user
    if not create_admin_user():
        print("\n❌ Admin user creation failed!")
        sys.exit(1)
    
    # Create sample data
    if not create_sample_data():
        print("\n❌ Sample data creation failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Database initialization completed successfully!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Start the Flask development server: python run.py")
    print("2. Access the API at: http://localhost:5000")
    print("3. Test the health endpoint: http://localhost:5000/health")
    print("4. Login with admin credentials: admin@cyber-intel.com / AdminPass123!")
    print("\n⚠️  Remember to change the default admin password!")

if __name__ == '__main__':
    main()
