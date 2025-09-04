#!/usr/bin/env python3
"""
Migration Helper Script
Manages database schema changes and migrations
"""

import os
import sys
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade, downgrade, current, history
from extensions import db, init_extensions
from config import config
from models import *

def create_app():
    """Create Flask application"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    return app

def init_migrations():
    """Initialize migration repository"""
    print("🚀 Initializing migration repository...")
    try:
        init(directory='migrations')
        print("✅ Migration repository initialized!")
    except Exception as e:
        print(f"❌ Error initializing migrations: {e}")

def create_migration(message=None):
    """Create a new migration"""
    if not message:
        message = input("Enter migration message: ").strip()
    
    print(f"🔄 Creating migration: {message}")
    try:
        migrate(message=message)
        print("✅ Migration created successfully!")
        print("📝 Remember to review the generated migration file before applying it.")
    except Exception as e:
        print(f"❌ Error creating migration: {e}")

def apply_migrations():
    """Apply pending migrations"""
    print("🔼 Applying migrations...")
    try:
        upgrade()
        print("✅ Migrations applied successfully!")
    except Exception as e:
        print(f"❌ Error applying migrations: {e}")

def rollback_migration():
    """Rollback last migration"""
    print("🔽 Rolling back last migration...")
    try:
        downgrade()
        print("✅ Migration rolled back successfully!")
    except Exception as e:
        print(f"❌ Error rolling back migration: {e}")

def show_migration_status():
    """Show current migration status"""
    print("📊 Migration Status:")
    print("=" * 30)
    try:
        current_rev = current()
        print(f"Current revision: {current_rev}")
        
        print("\n📜 Migration History:")
        hist = history()
        for revision in hist:
            print(f"  • {revision}")
            
    except Exception as e:
        print(f"❌ Error getting migration status: {e}")

def add_new_table_example():
    """Example of how to add a new table"""
    print("\n📝 Example: Adding a New Table")
    print("=" * 40)
    
    example_code = '''
# 1. Create a new model file: models/new_table.py
from extensions import db
from models.base import BaseModel
import enum

class NewTableStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class NewTable(BaseModel):
    """Example new table"""
    __tablename__ = 'new_table'
    
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(NewTableStatus), default=NewTableStatus.ACTIVE)
    
    def __repr__(self):
        return f'<NewTable {self.name}>'

# 2. Add import to models/__init__.py
from .new_table import NewTable, NewTableStatus

# 3. Create migration
python migration_helper.py

# 4. Select option 2 (Create migration)
# 5. Enter message: "Add new_table"
# 6. Review generated migration file
# 7. Apply migration with option 3
'''
    print(example_code)

def migration_menu():
    """Migration management menu"""
    app = create_app()
    
    with app.app_context():
        while True:
            print("\n" + "=" * 50)
            print("🔄 DATABASE MIGRATION MANAGER")
            print("=" * 50)
            print("1. 🚀 Initialize migrations")
            print("2. ➕ Create new migration")
            print("3. 🔼 Apply pending migrations")
            print("4. 🔽 Rollback last migration")
            print("5. 📊 Show migration status")
            print("6. 📝 Show how to add new table")
            print("7. 🚪 Exit")
            print("=" * 50)
            
            choice = input("Select option (1-7): ").strip()
            
            if choice == '1':
                init_migrations()
            elif choice == '2':
                create_migration()
            elif choice == '3':
                apply_migrations()
            elif choice == '4':
                rollback_migration()
            elif choice == '5':
                show_migration_status()
            elif choice == '6':
                add_new_table_example()
            elif choice == '7':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")

if __name__ == '__main__':
    migration_menu()