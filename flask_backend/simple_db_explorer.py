#!/usr/bin/env python3
"""
Simple Database Explorer for Cyber Intelligence Platform
"""

import sqlite3
import os
from datetime import datetime

def connect_to_database():
    """Connect to the SQLite database"""
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def show_database_overview(conn):
    """Show database overview"""
    cursor = conn.cursor()
    
    print("=" * 60)
    print("Cyber Intelligence Platform - Database Overview")
    print("=" * 60)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\nFound {len(tables)} tables:")
    print("-" * 40)
    
    total_rows = 0
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"  {table_name:25} {count:>8} rows")
        except Exception as e:
            print(f"  {table_name:25} ERROR: {str(e)[:30]}")
    
    print(f"\n  {'TOTAL':25} {total_rows:>8} rows")
    return tables

def show_recent_cases(conn):
    """Show recent cases"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, title, case_number, status, priority, created_at 
            FROM cases 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        cases = cursor.fetchall()
        
        if cases:
            print("\nRecent Cases:")
            print("-" * 60)
            for case in cases:
                print(f"ID: {case[0]} | {case[2]} | {case[1]}")
                print(f"     Status: {case[3]} | Priority: {case[4]} | Created: {case[5]}")
                print()
        else:
            print("\nNo cases found in database")
    except Exception as e:
        print(f"Error querying cases: {e}")

def show_recent_content(conn):
    """Show recent content"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, text, author, platform, risk_level, created_at 
            FROM content 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        content = cursor.fetchall()
        
        if content:
            print("\nRecent Content:")
            print("-" * 60)
            for item in content:
                text_preview = item[1][:50] + "..." if len(item[1]) > 50 else item[1]
                print(f"ID: {item[0]} | {item[2]} ({item[3]}) | Risk: {item[4]}")
                print(f"     Text: {text_preview}")
                print(f"     Created: {item[5]}")
                print()
        else:
            print("\nNo content found in database")
    except Exception as e:
        print(f"Error querying content: {e}")

def show_users(conn):
    """Show system users"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, username, email, role, is_active, created_at 
            FROM system_users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        if users:
            print("\nSystem Users:")
            print("-" * 60)
            for user in users:
                status = "Active" if user[4] else "Inactive"
                print(f"ID: {user[0]} | {user[1]} ({user[2]})")
                print(f"     Role: {user[3]} | Status: {status} | Created: {user[5]}")
                print()
        else:
            print("\nNo users found in database")
    except Exception as e:
        print(f"Error querying users: {e}")

def show_case_activities(conn):
    """Show recent case activities"""
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ca.id, ca.title, ca.activity_type, ca.status, c.title as case_title, ca.created_at
            FROM case_activities ca
            LEFT JOIN cases c ON ca.case_id = c.id
            ORDER BY ca.created_at DESC 
            LIMIT 10
        """)
        activities = cursor.fetchall()
        
        if activities:
            print("\nRecent Case Activities:")
            print("-" * 60)
            for activity in activities:
                case_title = activity[4] if activity[4] else "Unknown Case"
                print(f"ID: {activity[0]} | {activity[1]}")
                print(f"     Type: {activity[2]} | Status: {activity[3]} | Case: {case_title}")
                print(f"     Created: {activity[5]}")
                print()
        else:
            print("\nNo case activities found in database")
    except Exception as e:
        print(f"Error querying case activities: {e}")

def run_custom_query(conn, query):
    """Run a custom SQL query"""
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if rows:
            print(f"\nQuery Results ({len(rows)} rows):")
            print("-" * 40)
            for i, row in enumerate(rows[:20], 1):  # Show first 20 rows
                print(f"Row {i}: {dict(row)}")
            if len(rows) > 20:
                print(f"... and {len(rows) - 20} more rows")
        else:
            print("No results found")
    except Exception as e:
        print(f"Query error: {e}")

def main():
    """Main function"""
    conn = connect_to_database()
    if not conn:
        return
    
    # Show database overview
    tables = show_database_overview(conn)
    
    # Show recent data
    show_recent_cases(conn)
    show_recent_content(conn)
    show_users(conn)
    show_case_activities(conn)
    
    # Example queries
    print("\nExample Queries:")
    print("-" * 40)
    print("1. SELECT * FROM cases WHERE status = 'open';")
    print("2. SELECT * FROM content WHERE risk_level = 'high';")
    print("3. SELECT * FROM system_users WHERE is_active = 1;")
    print("4. SELECT * FROM case_activities ORDER BY created_at DESC LIMIT 5;")
    
    # Run some example queries
    print("\nRunning Example Queries:")
    print("-" * 40)
    
    # Query 1: Open cases
    print("\n1. Open Cases:")
    run_custom_query(conn, "SELECT id, title, case_number, status FROM cases WHERE status = 'open'")
    
    # Query 2: High risk content
    print("\n2. High Risk Content:")
    run_custom_query(conn, "SELECT id, author, platform, risk_level FROM content WHERE risk_level = 'high'")
    
    # Query 3: Active users
    print("\n3. Active Users:")
    run_custom_query(conn, "SELECT id, username, email, role FROM system_users WHERE is_active = 1")
    
    conn.close()
    print("\nDatabase exploration complete!")

if __name__ == "__main__":
    main()



