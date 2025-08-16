#!/usr/bin/env python3
"""
Database setup script for Flask backend (SQLite version)
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_database():
    """Set up database and run migrations"""
    try:
        # Import Flask app
        from __init__ import create_app
        from extensions import db
        
        # Create app
        app = create_app()
        
        with app.app_context():
            # Create all tables
            print("Creating database tables...")
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Run migrations if they exist
            try:
                from flask_migrate import upgrade
                print("Running database migrations...")
                upgrade()
                print("✅ Database migrations completed!")
            except Exception as e:
                print(f"⚠️  Migration warning: {e}")
                print("This is normal if no migrations exist yet.")
            
            print("\n🎉 Database setup completed successfully!")
            print("Database file: cyber_backend.db")
            print("You can now run your Flask application.")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed")
        print("2. Check your .env file has correct configuration")
        sys.exit(1)

def create_sample_data():
    """Create sample data for testing"""
    try:
        from __init__ import create_app
        from extensions import db
        from models.source import Source
        from models.content import Content
        from datetime import datetime
        
        app = create_app()
        
        with app.app_context():
            # Check if we already have data
            if Source.query.count() > 0:
                print("⚠️  Sample data already exists. Skipping...")
                return
            
            print("Creating sample data...")
            
            # Create sample sources
            sources = [
                Source(
                    name="Dark Web Monitor",
                    url="https://example-dark-web.com",
                    type="dark_web",
                    is_active=True
                ),
                Source(
                    name="Social Media Scanner",
                    url="https://example-social.com",
                    type="social_media",
                    is_active=True
                ),
                Source(
                    name="News Aggregator",
                    url="https://example-news.com",
                    type="news",
                    is_active=True
                )
            ]
            
            for source in sources:
                db.session.add(source)
            
            db.session.commit()
            print("✅ Sample sources created!")
            
            # Create sample content
            contents = [
                Content(
                    source_id=1,
                    title="Suspicious Activity Detected",
                    text="Analysis of potential threat indicators in dark web forums",
                    risk_level="high",
                    keywords=["threat", "suspicious", "dark web"],
                    analysis_summary="High-risk content detected with multiple threat indicators"
                ),
                Content(
                    source_id=2,
                    title="Social Media Threat Analysis",
                    text="Monitoring social media for potential security threats",
                    risk_level="medium",
                    keywords=["social", "threat", "monitoring"],
                    analysis_summary="Medium-risk content with potential security implications"
                ),
                Content(
                    source_id=3,
                    title="News Security Update",
                    text="Latest security news and threat intelligence",
                    risk_level="low",
                    keywords=["news", "security", "update"],
                    analysis_summary="Low-risk content with general security information"
                )
            ]
            
            for content in contents:
                db.session.add(content)
            
            db.session.commit()
            print("✅ Sample content created!")
            print("🎉 Sample data setup completed!")
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    print("🚀 Setting up database for Flask backend...")
    print("=" * 50)
    
    # Set up database
    setup_database()
    
    # Ask if user wants sample data
    print("\n" + "=" * 50)
    response = input("Do you want to create sample data for testing? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        create_sample_data()
    else:
        print("Skipping sample data creation.")
    
    print("\n🎉 Setup completed! You can now run your Flask application.")
    print("Database file: cyber_backend.db") 