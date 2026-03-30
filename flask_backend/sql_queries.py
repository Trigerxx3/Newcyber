#!/usr/bin/env python3
"""
SQL Queries for Cyber Intelligence Platform Database
Pre-built queries for common data access needs
"""

import sqlite3
import os
from datetime import datetime

class DatabaseQueries:
    def __init__(self, db_path='cyber_intel.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to database"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def execute_query(self, query, description=""):
        """Execute a query and display results"""
        if not self.conn:
            print("❌ No database connection")
            return
        
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print(f"\n🔍 {description}")
            print("="*60)
            print(f"Query: {query}")
            print(f"Results: {len(rows)} rows")
            print("-"*60)
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"\nRow {i}:")
                    for key, value in dict(row).items():
                        if value is not None and len(str(value)) > 100:
                            value = str(value)[:100] + "..."
                        print(f"  {key:20}: {value}")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"❌ Query error: {e}")
    
    def show_all_users(self):
        """Show all users"""
        query = """
            SELECT id, username, email, role, is_active, created_at 
            FROM system_users 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "ALL USERS")
    
    def show_active_users(self):
        """Show active users only"""
        query = """
            SELECT id, username, email, role, created_at 
            FROM system_users 
            WHERE is_active = 1 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "ACTIVE USERS")
    
    def show_all_cases(self):
        """Show all cases"""
        query = """
            SELECT id, title, case_number, status, priority, created_at 
            FROM cases 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "ALL CASES")
    
    def show_open_cases(self):
        """Show open cases only"""
        query = """
            SELECT id, title, case_number, status, priority, created_at 
            FROM cases 
            WHERE status = 'OPEN' 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "OPEN CASES")
    
    def show_high_priority_cases(self):
        """Show high priority cases"""
        query = """
            SELECT id, title, case_number, status, priority, created_at 
            FROM cases 
            WHERE priority IN ('HIGH', 'CRITICAL') 
            ORDER BY priority DESC, created_at DESC
        """
        self.execute_query(query, "HIGH PRIORITY CASES")
    
    def show_all_content(self):
        """Show all content"""
        query = """
            SELECT id, text, author, created_at 
            FROM content 
            ORDER BY created_at DESC 
            LIMIT 20
        """
        self.execute_query(query, "ALL CONTENT (Last 20)")
    
    def show_recent_content(self):
        """Show recent content"""
        query = """
            SELECT id, text, author, created_at 
            FROM content 
            WHERE created_at > datetime('now', '-7 days') 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "RECENT CONTENT (Last 7 days)")
    
    def show_all_sources(self):
        """Show all sources"""
        query = """
            SELECT id, name, platform, is_active, created_at 
            FROM sources 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "ALL SOURCES")
    
    def show_active_sources(self):
        """Show active sources only"""
        query = """
            SELECT id, name, platform, created_at 
            FROM sources 
            WHERE is_active = 1 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "ACTIVE SOURCES")
    
    def show_case_activities(self):
        """Show case activities"""
        query = """
            SELECT ca.id, ca.title, ca.activity_type, ca.status, c.title as case_title, ca.created_at
            FROM case_activities ca
            LEFT JOIN cases c ON ca.case_id = c.id
            ORDER BY ca.created_at DESC
        """
        self.execute_query(query, "CASE ACTIVITIES")
    
    def show_user_case_links(self):
        """Show user-case assignments"""
        query = """
            SELECT ucl.id, u.username, c.title as case_title, c.case_number, ucl.created_at
            FROM user_case_links ucl
            LEFT JOIN system_users u ON ucl.user_id = u.id
            LEFT JOIN cases c ON ucl.case_id = c.id
            ORDER BY ucl.created_at DESC
        """
        self.execute_query(query, "USER-CASE ASSIGNMENTS")
    
    def show_case_content_links(self):
        """Show content linked to cases"""
        query = """
            SELECT ccl.id, c.title as case_title, c.case_number, co.text, co.author, ccl.created_at
            FROM case_content_links ccl
            LEFT JOIN cases c ON ccl.case_id = c.id
            LEFT JOIN content co ON ccl.content_id = co.id
            ORDER BY ccl.created_at DESC
        """
        self.execute_query(query, "CASE-CONTENT LINKS")
    
    def show_database_stats(self):
        """Show database statistics"""
        queries = [
            ("Total Users", "SELECT COUNT(*) as count FROM system_users"),
            ("Active Users", "SELECT COUNT(*) as count FROM system_users WHERE is_active = 1"),
            ("Total Cases", "SELECT COUNT(*) as count FROM cases"),
            ("Open Cases", "SELECT COUNT(*) as count FROM cases WHERE status = 'OPEN'"),
            ("High Priority Cases", "SELECT COUNT(*) as count FROM cases WHERE priority IN ('HIGH', 'CRITICAL')"),
            ("Total Content", "SELECT COUNT(*) as count FROM content"),
            ("Total Sources", "SELECT COUNT(*) as count FROM sources"),
            ("Active Sources", "SELECT COUNT(*) as count FROM sources WHERE is_active = 1"),
            ("Case Activities", "SELECT COUNT(*) as count FROM case_activities"),
            ("User-Case Links", "SELECT COUNT(*) as count FROM user_case_links"),
            ("Case-Content Links", "SELECT COUNT(*) as count FROM case_content_links")
        ]
        
        print("\n📊 DATABASE STATISTICS")
        print("="*60)
        
        for description, query in queries:
            try:
                cursor = self.conn.cursor()
                cursor.execute(query)
                result = cursor.fetchone()
                count = result[0] if result else 0
                print(f"  {description:25} {count:>8}")
            except Exception as e:
                print(f"  {description:25} ERROR: {str(e)[:30]}")
    
    def show_recent_activity(self):
        """Show recent activity"""
        print("\n🕒 RECENT ACTIVITY (Last 7 days)")
        print("="*60)
        
        # Recent cases
        query = """
            SELECT title, case_number, status, priority, created_at 
            FROM cases 
            WHERE created_at > datetime('now', '-7 days') 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "Recent Cases")
        
        # Recent users
        query = """
            SELECT username, email, role, created_at 
            FROM system_users 
            WHERE created_at > datetime('now', '-7 days') 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "Recent Users")
        
        # Recent content
        query = """
            SELECT id, text, author, created_at 
            FROM content 
            WHERE created_at > datetime('now', '-7 days') 
            ORDER BY created_at DESC
        """
        self.execute_query(query, "Recent Content")
    
    def run_custom_query(self, query):
        """Run a custom SQL query"""
        self.execute_query(query, "CUSTOM QUERY")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

def main():
    """Main function with menu"""
    queries = DatabaseQueries()
    
    if not queries.conn:
        print("❌ Failed to connect to database")
        return
    
    while True:
        print("\n" + "="*80)
        print("🔍 DATABASE QUERIES - CYBER INTELLIGENCE PLATFORM")
        print("="*80)
        print("1. Show all users")
        print("2. Show active users")
        print("3. Show all cases")
        print("4. Show open cases")
        print("5. Show high priority cases")
        print("6. Show all content")
        print("7. Show recent content")
        print("8. Show all sources")
        print("9. Show active sources")
        print("10. Show case activities")
        print("11. Show user-case assignments")
        print("12. Show case-content links")
        print("13. Show database statistics")
        print("14. Show recent activity")
        print("15. Run custom query")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-15): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            queries.show_all_users()
        elif choice == '2':
            queries.show_active_users()
        elif choice == '3':
            queries.show_all_cases()
        elif choice == '4':
            queries.show_open_cases()
        elif choice == '5':
            queries.show_high_priority_cases()
        elif choice == '6':
            queries.show_all_content()
        elif choice == '7':
            queries.show_recent_content()
        elif choice == '8':
            queries.show_all_sources()
        elif choice == '9':
            queries.show_active_sources()
        elif choice == '10':
            queries.show_case_activities()
        elif choice == '11':
            queries.show_user_case_links()
        elif choice == '12':
            queries.show_case_content_links()
        elif choice == '13':
            queries.show_database_stats()
        elif choice == '14':
            queries.show_recent_activity()
        elif choice == '15':
            query = input("Enter SQL query: ").strip()
            queries.run_custom_query(query)
        else:
            print("❌ Invalid choice")
    
    queries.close()
    print("\n✅ Database queries complete!")

if __name__ == "__main__":
    main()



