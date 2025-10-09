#!/usr/bin/env python3
"""
Migration script to add content analysis fields to the Content table
Run this script to add the new columns: suspicion_score, intent, is_flagged
"""
import os
import sys
from datetime import datetime

# Add the flask_backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import create_app

def run_migration():
    """Run the migration to add content analysis fields"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('content')]
            
            print("Current content table columns:", columns)
            
            # Add new columns if they don't exist
            if 'suspicion_score' not in columns:
                print("Adding suspicion_score column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE content ADD COLUMN suspicion_score INTEGER DEFAULT 0"))
                    conn.commit()
                print("✅ Added suspicion_score column")
            else:
                print("✅ suspicion_score column already exists")
            
            if 'intent' not in columns:
                print("Adding intent column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE content ADD COLUMN intent VARCHAR(50) DEFAULT 'Unknown'"))
                    conn.commit()
                print("✅ Added intent column")
            else:
                print("✅ intent column already exists")
            
            if 'is_flagged' not in columns:
                print("Adding is_flagged column...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE content ADD COLUMN is_flagged BOOLEAN DEFAULT FALSE"))
                    conn.commit()
                print("✅ Added is_flagged column")
            else:
                print("✅ is_flagged column already exists")
            
            # Create indexes for better performance
            try:
                print("Creating indexes...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("CREATE INDEX IF NOT EXISTS idx_content_suspicion_score ON content(suspicion_score)"))
                    conn.execute(db.text("CREATE INDEX IF NOT EXISTS idx_content_intent ON content(intent)"))
                    conn.execute(db.text("CREATE INDEX IF NOT EXISTS idx_content_is_flagged ON content(is_flagged)"))
                    conn.commit()
                print("✅ Created indexes")
            except Exception as e:
                print(f"⚠️  Index creation failed (may already exist): {e}")
            
            print("\n🎉 Migration completed successfully!")
            print("New columns added to content table:")
            print("  - suspicion_score: INTEGER (0-100)")
            print("  - intent: VARCHAR(50) (Selling, Buying, Informational, Unknown)")
            print("  - is_flagged: BOOLEAN (True if suspicion_score >= 70)")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🚀 Starting content analysis migration...")
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now use the content analysis API endpoints.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
