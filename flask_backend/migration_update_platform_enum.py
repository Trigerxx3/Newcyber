#!/usr/bin/env python3
"""
Migration script to update PlatformType enum values
"""
import os
import sys
from datetime import datetime

# Add the flask_backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extensions import db
from app import create_app

def run_migration():
    """Update PlatformType enum values"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🔄 Updating PlatformType enum values...")
            
            # For SQLite, we need to recreate the table with new enum values
            # This is a simplified approach - in production, you'd want a more sophisticated migration
            
            # Check if we need to update existing data
            with db.engine.connect() as conn:
                # Check current enum values in the database
                result = conn.execute(db.text("SELECT DISTINCT platform FROM sources"))
                current_platforms = [row[0] for row in result.fetchall()]
                
                print(f"Current platforms in database: {current_platforms}")
                
                # Update any existing records that might have issues
                conn.execute(db.text("""
                    UPDATE sources 
                    SET platform = 'Unknown' 
                    WHERE platform NOT IN ('Telegram', 'Instagram', 'WhatsApp', 'Facebook', 'Twitter', 'TikTok', 'Unknown')
                """))
                conn.commit()
                
                print("✅ Updated any invalid platform values to 'Unknown'")
            
            print("\n🎉 Platform enum migration completed!")
            print("New platform types available:")
            print("  - Telegram")
            print("  - Instagram") 
            print("  - WhatsApp")
            print("  - Facebook")
            print("  - Twitter")
            print("  - TikTok")
            print("  - Unknown")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("🚀 Starting platform enum migration...")
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        print("You can now use all platform types in content analysis.")
    else:
        print("\n❌ Migration failed!")
        sys.exit(1)
