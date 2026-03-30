#!/usr/bin/env python3
"""
Simple Data Viewer - Access all database data without Unicode issues
"""

import sqlite3
import os
from datetime import datetime

def view_all_data():
    """View all important data from the database"""
    
    # Connect to database
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("CYBER INTELLIGENCE PLATFORM - DATA VIEWER")
    print("="*60)
    
    # 1. Database Overview
    print("\nDATABASE OVERVIEW")
    print("-"*40)
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    total_rows = 0
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            total_rows += count
            print(f"  {table_name:25} {count:>8} rows")
        except:
            print(f"  {table_name:25} ERROR")
    
    print(f"\n  {'TOTAL':25} {total_rows:>8} rows")
    
    # 2. Users Data
    print("\nUSERS DATA")
    print("-"*40)
    try:
        cursor.execute("""
            SELECT id, username, email, role, is_active, created_at 
            FROM system_users 
            ORDER BY created_at DESC 
            LIMIT 15
        """)
        users = cursor.fetchall()
        
        print(f"Total Users: {len(users)}")
        print("ID | Username         | Email                    | Role     | Status")
        print("-"*70)
        for user in users:
            status = "Active" if user[4] else "Inactive"
            print(f"{user[0]:2} | {user[1]:15} | {user[2]:25} | {user[3]:8} | {status}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Cases Data
    print("\nCASES DATA")
    print("-"*40)
    try:
        cursor.execute("""
            SELECT id, title, case_number, status, priority, created_at 
            FROM cases 
            ORDER BY created_at DESC 
            LIMIT 15
        """)
        cases = cursor.fetchall()
        
        print(f"Total Cases: {len(cases)}")
        print("ID | Case Number      | Title                   | Status   | Priority")
        print("-"*70)
        for case in cases:
            print(f"{case[0]:2} | {case[2]:15} | {case[1]:25} | {case[3]:8} | {case[4]}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Content Data
    print("\nCONTENT DATA")
    print("-"*40)
    try:
        cursor.execute("""
            SELECT id, text, author, created_at 
            FROM content 
            ORDER BY created_at DESC 
            LIMIT 15
        """)
        content = cursor.fetchall()
        
        print(f"Total Content: {len(content)}")
        print("ID | Author           | Text Preview")
        print("-"*60)
        for item in content:
            text_preview = item[1][:40] + "..." if len(item[1]) > 40 else item[1]
            print(f"{item[0]:3} | {item[2]:15} | {text_preview}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Sources Data
    print("\nSOURCES DATA")
    print("-"*40)
    try:
        cursor.execute("""
            SELECT id, name, platform, is_active, created_at 
            FROM sources 
            ORDER BY created_at DESC 
            LIMIT 15
        """)
        sources = cursor.fetchall()
        
        print(f"Total Sources: {len(sources)}")
        print("ID | Name                 | Platform   | Status")
        print("-"*50)
        for source in sources:
            status = "Active" if source[3] else "Inactive"
            print(f"{source[0]:2} | {source[1]:20} | {source[2]:10} | {status}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Case Activities
    print("\nCASE ACTIVITIES")
    print("-"*40)
    try:
        cursor.execute("""
            SELECT ca.id, ca.title, ca.activity_type, ca.status, c.title as case_title
            FROM case_activities ca
            LEFT JOIN cases c ON ca.case_id = c.id
            ORDER BY ca.created_at DESC 
            LIMIT 10
        """)
        activities = cursor.fetchall()
        
        print(f"Total Activities: {len(activities)}")
        print("ID | Title                | Type       | Status   | Case")
        print("-"*60)
        for activity in activities:
            case_title = activity[4] if activity[4] else "Unknown"
            print(f"{activity[0]:2} | {activity[1]:20} | {activity[2]:10} | {activity[3]:8} | {case_title}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Statistics
    print("\nDATABASE STATISTICS")
    print("-"*40)
    
    stats = [
        ("Total Users", "SELECT COUNT(*) FROM system_users"),
        ("Active Users", "SELECT COUNT(*) FROM system_users WHERE is_active = 1"),
        ("Total Cases", "SELECT COUNT(*) FROM cases"),
        ("Open Cases", "SELECT COUNT(*) FROM cases WHERE status = 'OPEN'"),
        ("High Priority Cases", "SELECT COUNT(*) FROM cases WHERE priority IN ('HIGH', 'CRITICAL')"),
        ("Total Content", "SELECT COUNT(*) FROM content"),
        ("Total Sources", "SELECT COUNT(*) FROM sources"),
        ("Active Sources", "SELECT COUNT(*) FROM sources WHERE is_active = 1"),
        ("Case Activities", "SELECT COUNT(*) FROM case_activities"),
        ("User-Case Links", "SELECT COUNT(*) FROM user_case_links"),
        ("Case-Content Links", "SELECT COUNT(*) FROM case_content_links")
    ]
    
    for description, query in stats:
        try:
            cursor.execute(query)
            result = cursor.fetchone()
            count = result[0] if result else 0
            print(f"  {description:25} {count:>8}")
        except Exception as e:
            print(f"  {description:25} ERROR: {str(e)[:30]}")
    
    # 8. Recent Activity
    print("\nRECENT ACTIVITY (Last 7 days)")
    print("-"*40)
    
    # Recent cases
    try:
        cursor.execute("SELECT COUNT(*) FROM cases WHERE created_at > datetime('now', '-7 days')")
        recent_cases = cursor.fetchone()[0]
        print(f"Cases created in last 7 days: {recent_cases}")
    except:
        print("Recent cases: Error")
    
    # Recent users
    try:
        cursor.execute("SELECT COUNT(*) FROM system_users WHERE created_at > datetime('now', '-7 days')")
        recent_users = cursor.fetchone()[0]
        print(f"Users created in last 7 days: {recent_users}")
    except:
        print("Recent users: Error")
    
    # Recent content
    try:
        cursor.execute("SELECT COUNT(*) FROM content WHERE created_at > datetime('now', '-7 days')")
        recent_content = cursor.fetchone()[0]
        print(f"Content created in last 7 days: {recent_content}")
    except:
        print("Recent content: Error")
    
    conn.close()
    print("\nData view complete!")

if __name__ == "__main__":
    view_all_data()



