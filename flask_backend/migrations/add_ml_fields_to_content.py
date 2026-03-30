"""
Database migration script to add ML fields to Content table
Run this script to add the new ML-related columns to the content table
"""
import sys
from pathlib import Path
from sqlalchemy import text, inspect

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from extensions import db
from app import create_app

def add_ml_fields():
    """Add ML fields to Content table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = inspect(db.engine)
            existing_columns = [col['name'] for col in inspector.get_columns('content')]
            
            # Add columns if they don't exist
            if 'ml_prediction' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE content 
                    ADD COLUMN ml_prediction VARCHAR(50)
                """))
                print("✓ Added ml_prediction column")
            else:
                print("⚠ ml_prediction column already exists")
            
            if 'ml_confidence' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE content 
                    ADD COLUMN ml_confidence FLOAT
                """))
                print("✓ Added ml_confidence column")
            else:
                print("⚠ ml_confidence column already exists")
            
            if 'risk_score' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE content 
                    ADD COLUMN risk_score INTEGER
                """))
                print("✓ Added risk_score column")
            else:
                print("⚠ risk_score column already exists")
            
            if 'risk_level_ml' not in existing_columns:
                db.session.execute(text("""
                    ALTER TABLE content 
                    ADD COLUMN risk_level_ml VARCHAR(20)
                """))
                print("✓ Added risk_level_ml column")
            else:
                print("⚠ risk_level_ml column already exists")
            
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise

if __name__ == "__main__":
    print("Running migration: Add ML fields to Content table...")
    add_ml_fields()
