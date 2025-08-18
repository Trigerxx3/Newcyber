#!/usr/bin/env python3
"""
Script to examine SQLAlchemy database contents
"""
import sqlite3
import os

def check_database():
    db_path = 'local.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    print(f"📍 SQLAlchemy Database Location:")
    print(f"   File: {os.path.abspath(db_path)}")
    print(f"   Size: {os.path.getsize(db_path):,} bytes")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📊 Tables in SQLAlchemy Database:")
        for table in tables:
            table_name = table[0]
            
            # Get row count for each table
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"   ✓ {table_name:<20} ({count} rows)")
        
        print()
        
        # Check system_users table specifically
        print("👤 System Users (Admins/Analysts):")
        cursor.execute("SELECT username, email, role, is_active FROM system_users")
        users = cursor.fetchall()
        for user in users:
            print(f"   - {user[0]} ({user[1]}) - Role: {user[2]} - Active: {user[3]}")
        
        print()
        
        # Check if there are any platform users
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            platform_user_count = cursor.fetchone()[0]
            print(f"🕵️ Platform Users (Suspects): {platform_user_count} records")
        except:
            print("🕵️ Platform Users table: Not yet populated")
        
        print()
        
        # Check content table
        try:
            cursor.execute("SELECT COUNT(*) FROM content")
            content_count = cursor.fetchone()[0]
            print(f"📄 Content Analysis Records: {content_count} records")
        except:
            print("📄 Content table: Not yet populated")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error examining database: {e}")

if __name__ == '__main__':
    check_database()