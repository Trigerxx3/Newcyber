#!/usr/bin/env python3
"""
Quick Data Viewer - Immediate access to all database data
"""

import sqlite3
import os
from datetime import datetime

def quick_view_all_data():
    """Quickly view all important data from the database"""
    
    # Connect to database
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("🔍 CYBER INTELLIGENCE PLATFORM - QUICK DATA VIEW")
    print("="*80)
    
    # 1. Database Overview
    print("\n📊 DATABASE OVERVIEW")
    print("-"*50)
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
    print("\n👥 USERS DATA")
    print("-"*50)
    try:
        cursor.execute("""
            SELECT id, username, email, role, is_active, created_at 
            FROM system_users 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        users = cursor.fetchall()
        
        print(f"Total Users: {len(users)}")
        for user in users:
            status = "✅ Active" if user[4] else "❌ Inactive"
            print(f"  ID: {user[0]:2} | {user[1]:15} | {user[2]:25} | {user[3]:8} | {status}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Cases Data
    print("\n📁 CASES DATA")
    print("-"*50)
    try:
        cursor.execute("""
            SELECT id, title, case_number, status, priority, created_at 
            FROM cases 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        cases = cursor.fetchall()
        
        print(f"Total Cases: {len(cases)}")
        for case in cases:
            print(f"  ID: {case[0]:2} | {case[2]:15} | {case[1]:20} | {case[3]:8} | {case[4]:8}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Content Data
    print("\n📄 CONTENT DATA")
    print("-"*50)
    try:
        cursor.execute("""
            SELECT id, text, author, created_at 
            FROM content 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        content = cursor.fetchall()
        
        print(f"Total Content: {len(content)}")
        for item in content:
            text_preview = item[1][:50] + "..." if len(item[1]) > 50 else item[1]
            print(f"  ID: {item[0]:3} | {item[2]:15} | {text_preview}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Sources Data
    print("\n🔗 SOURCES DATA")
    print("-"*50)
    try:
        cursor.execute("""
            SELECT id, name, platform, is_active, created_at 
            FROM sources 
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        sources = cursor.fetchall()
        
        print(f"Total Sources: {len(sources)}")
        for source in sources:
            status = "✅ Active" if source[3] else "❌ Inactive"
            print(f"  ID: {source[0]:2} | {source[1]:20} | {source[2]:10} | {status}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Case Activities
    print("\n📋 CASE ACTIVITIES")
    print("-"*50)
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
        for activity in activities:
            case_title = activity[4] if activity[4] else "Unknown"
            print(f"  ID: {activity[0]:2} | {activity[1]:20} | {activity[2]:10} | {activity[3]:8} | Case: {case_title}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Recent Data Summary
    print("\n📈 RECENT ACTIVITY SUMMARY")
    print("-"*50)
    
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
    
    # 8. Quick Queries
    print("\n🔍 QUICK QUERIES")
    print("-"*50)
    
    # Open cases
    try:
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'OPEN'")
        open_cases = cursor.fetchone()[0]
        print(f"Open cases: {open_cases}")
    except:
        print("Open cases: Error")
    
    # Active users
    try:
        cursor.execute("SELECT COUNT(*) FROM system_users WHERE is_active = 1")
        active_users = cursor.fetchone()[0]
        print(f"Active users: {active_users}")
    except:
        print("Active users: Error")
    
    # High priority cases
    try:
        cursor.execute("SELECT COUNT(*) FROM cases WHERE priority = 'HIGH' OR priority = 'CRITICAL'")
        high_priority = cursor.fetchone()[0]
        print(f"High/Critical priority cases: {high_priority}")
    except:
        print("High priority cases: Error")
    
    conn.close()
    print("\n✅ Data view complete!")

if __name__ == "__main__":
    quick_view_all_data()



