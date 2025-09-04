#!/usr/bin/env python3
"""
Database Management Script
Provides interactive access to the database for CRUD operations
"""

import sys
import os
from flask import Flask
from extensions import db, init_extensions
from config import config
from models import *
from sqlalchemy import text, inspect
import json
from datetime import datetime

def create_app():
    """Create Flask application"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    return app

def list_tables():
    """List all database tables"""
    print("\n🗄️  Database Tables:")
    print("=" * 50)
    
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    for table in tables:
        columns = inspector.get_columns(table)
        print(f"\n📋 {table.upper()}")
        print("-" * 30)
        for col in columns:
            type_info = str(col['type'])
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            primary_key = " (PK)" if col.get('primary_key') else ""
            print(f"  • {col['name']}: {type_info} {nullable}{primary_key}")

def show_table_data(table_name):
    """Show data from a specific table"""
    try:
        result = db.session.execute(text(f"SELECT * FROM {table_name} LIMIT 10"))
        rows = result.fetchall()
        columns = result.keys()
        
        print(f"\n📊 Data from {table_name.upper()} (First 10 records):")
        print("=" * 80)
        
        if not rows:
            print("  No data found in this table.")
            return
            
        # Print headers
        header = " | ".join([f"{col:15}" for col in columns])
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in rows:
            row_data = " | ".join([f"{str(val)[:15]:15}" for val in row])
            print(row_data)
            
    except Exception as e:
        print(f"❌ Error accessing table {table_name}: {e}")

def count_records():
    """Count records in all tables"""
    print("\n📊 Record Counts:")
    print("=" * 30)
    
    tables = {
        'system_users': SystemUser,
        'users': User,
        'sources': Source,
        'content': Content,
        'keywords': Keyword,
        'detections': Detection,
        'identifiers': Identifier,
        'osint_results': OSINTResult,
        'cases': Case,
        'user_case_links': UserCaseLink,
        'osint_identifier_links': OSINTIdentifierLink
    }
    
    for table_name, model in tables.items():
        try:
            count = model.query.count()
            print(f"  {table_name}: {count}")
        except Exception as e:
            print(f"  {table_name}: Error - {e}")

def create_admin_user_interactive():
    """Interactive admin user creation"""
    print("\n👤 Create Admin User:")
    print("=" * 30)
    
    email = input("Email: ").strip()
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    if not all([email, username, password]):
        print("❌ All fields are required!")
        return
    
    try:
        from auth import Auth
        result = Auth.register_user(
            email=email,
            password=password,
            username=username,
            role='Admin'
        )
        
        if result['success']:
            print("✅ Admin user created successfully!")
        else:
            print(f"❌ Error: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

def add_sample_data():
    """Add sample data to the database"""
    print("\n🌱 Adding Sample Data...")
    print("=" * 30)
    
    try:
        # Add sample source
        if Source.query.count() == 0:
            source = Source(
                platform=PlatformType.TELEGRAM,
                source_handle='@sample_channel',
                source_name='Sample Channel',
                source_type=SourceType.CHANNEL,
                description='Sample Telegram channel for testing'
            )
            db.session.add(source)
        
        # Add sample keywords
        if Keyword.query.count() == 0:
            keywords = [
                Keyword(keyword='suspicious', type=KeywordType.THREAT, severity=KeywordSeverity.MEDIUM),
                Keyword(keyword='malware', type=KeywordType.MALWARE, severity=KeywordSeverity.HIGH),
                Keyword(keyword='breach', type=KeywordType.THREAT, severity=KeywordSeverity.HIGH)
            ]
            for kw in keywords:
                db.session.add(kw)
        
        db.session.commit()
        print("✅ Sample data added successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error adding sample data: {e}")

def execute_custom_query():
    """Execute custom SQL query"""
    print("\n💻 Custom Query Executor:")
    print("=" * 30)
    print("Enter SQL query (or 'exit' to return):")
    
    while True:
        query = input("SQL> ").strip()
        
        if query.lower() == 'exit':
            break
        
        if not query:
            continue
            
        try:
            result = db.session.execute(text(query))
            
            if query.lower().startswith('select'):
                rows = result.fetchall()
                if rows:
                    columns = result.keys()
                    print(f"\nColumns: {list(columns)}")
                    for i, row in enumerate(rows):
                        print(f"Row {i+1}: {dict(row._mapping)}")
                else:
                    print("No results found.")
            else:
                db.session.commit()
                print("✅ Query executed successfully!")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")

def backup_database():
    """Create a backup of the database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.db"
    
    try:
        import shutil
        shutil.copy2('local.db', backup_file)
        print(f"✅ Database backed up to: {backup_file}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

def main_menu():
    """Main interactive menu"""
    app = create_app()
    
    with app.app_context():
        while True:
            print("\n" + "=" * 60)
            print("🗄️  CYBER INTELLIGENCE PLATFORM - DATABASE MANAGER")
            print("=" * 60)
            print("1. 📋 List all tables and schema")
            print("2. 📊 Show record counts")
            print("3. 🔍 View table data")
            print("4. 👤 Create admin user")
            print("5. 🌱 Add sample data")
            print("6. 💻 Execute custom query")
            print("7. 💾 Backup database")
            print("8. 🚪 Exit")
            print("=" * 60)
            
            choice = input("Select option (1-8): ").strip()
            
            if choice == '1':
                list_tables()
            elif choice == '2':
                count_records()
            elif choice == '3':
                table_name = input("Enter table name: ").strip()
                show_table_data(table_name)
            elif choice == '4':
                create_admin_user_interactive()
            elif choice == '5':
                add_sample_data()
            elif choice == '6':
                execute_custom_query()
            elif choice == '7':
                backup_database()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please try again.")

if __name__ == '__main__':
    main_menu()