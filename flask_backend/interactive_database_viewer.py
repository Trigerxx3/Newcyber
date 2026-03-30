#!/usr/bin/env python3
"""
Interactive Database Viewer for Cyber Intelligence Platform
User-friendly interface to access and view all database data
"""

import sqlite3
import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

class InteractiveDatabaseViewer:
    def __init__(self, db_path: str = 'cyber_intel.db'):
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to the database"""
        if not os.path.exists(self.db_path):
            print(f"❌ Database file not found: {self.db_path}")
            return False
        
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            print(f"✅ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return False
    
    def show_welcome(self):
        """Show welcome message"""
        print("\n" + "="*80)
        print("🔍 CYBER INTELLIGENCE PLATFORM - INTERACTIVE DATABASE VIEWER")
        print("="*80)
        print("Welcome to the interactive database viewer!")
        print("You can explore all tables, search data, and export information.")
        print("="*80)
    
    def show_database_overview(self):
        """Show database overview"""
        cursor = self.conn.cursor()
        
        print("\n📊 DATABASE OVERVIEW")
        print("-"*50)
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        total_rows = 0
        print(f"Found {len(tables)} tables:")
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
        return [table[0] for table in tables]
    
    def view_table_data(self, table_name: str, limit: int = 10):
        """View data from a specific table"""
        cursor = self.conn.cursor()
        
        try:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"\n📋 TABLE: {table_name.upper()}")
            print("="*60)
            print(f"Rows: {count}")
            print(f"Columns: {len(columns)}")
            
            # Show column names
            print("\nColumns:")
            for col in columns:
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                print(f"  {col[1]:20} {col[2]:15} {nullable}")
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()
            
            if rows:
                print(f"\nData (showing {len(rows)} of {count} rows):")
                print("-"*60)
                
                for i, row in enumerate(rows, 1):
                    print(f"\nRow {i}:")
                    for key, value in dict(row).items():
                        if value is not None:
                            # Handle long text
                            if len(str(value)) > 100:
                                value = str(value)[:100] + "..."
                            # Handle special characters
                            try:
                                print(f"  {key:20}: {value}")
                            except UnicodeEncodeError:
                                # Remove problematic characters
                                clean_value = str(value).encode('ascii', 'ignore').decode('ascii')
                                print(f"  {key:20}: {clean_value}")
                        else:
                            print(f"  {key:20}: NULL")
            else:
                print(f"\nNo data found in {table_name}")
                
        except Exception as e:
            print(f"❌ Error viewing table {table_name}: {e}")
    
    def search_data(self, table_name: str, search_term: str):
        """Search for data in a table"""
        cursor = self.conn.cursor()
        
        try:
            # Get all columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Build search query
            search_conditions = []
            for col in column_names:
                search_conditions.append(f"{col} LIKE '%{search_term}%'")
            
            query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print(f"\n🔍 SEARCH RESULTS in {table_name}")
            print("="*60)
            print(f"Search term: '{search_term}'")
            print(f"Found: {len(rows)} results")
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"\nResult {i}:")
                    for key, value in dict(row).items():
                        if value is not None:
                            if len(str(value)) > 100:
                                value = str(value)[:100] + "..."
                            try:
                                print(f"  {key:20}: {value}")
                            except UnicodeEncodeError:
                                clean_value = str(value).encode('ascii', 'ignore').decode('ascii')
                                print(f"  {key:20}: {clean_value}")
                        else:
                            print(f"  {key:20}: NULL")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"❌ Error searching {table_name}: {e}")
    
    def run_custom_query(self, query: str):
        """Run a custom SQL query"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print(f"\n🔍 CUSTOM QUERY RESULTS")
            print("="*60)
            print(f"Query: {query}")
            print(f"Results: {len(rows)} rows")
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"\nRow {i}:")
                    for key, value in dict(row).items():
                        if value is not None:
                            if len(str(value)) > 100:
                                value = str(value)[:100] + "..."
                            try:
                                print(f"  {key:20}: {value}")
                            except UnicodeEncodeError:
                                clean_value = str(value).encode('ascii', 'ignore').decode('ascii')
                                print(f"  {key:20}: {clean_value}")
                        else:
                            print(f"  {key:20}: NULL")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"❌ Query error: {e}")
    
    def export_table_to_csv(self, table_name: str, filename: str = None):
        """Export table data to CSV"""
        if not filename:
            filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if rows:
                    # Write header
                    columns = [description[0] for description in cursor.description]
                    writer = csv.writer(f)
                    writer.writerow(columns)
                    
                    # Write data
                    for row in rows:
                        writer.writerow(row)
            
            print(f"✅ Exported {len(rows)} rows from {table_name} to {filename}")
            
        except Exception as e:
            print(f"❌ Export error: {e}")
    
    def export_table_to_json(self, table_name: str, filename: str = None):
        """Export table data to JSON"""
        if not filename:
            filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        cursor = self.conn.cursor()
        
        try:
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            data = [dict(row) for row in rows]
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"✅ Exported {len(rows)} rows from {table_name} to {filename}")
            
        except Exception as e:
            print(f"❌ Export error: {e}")
    
    def show_quick_stats(self):
        """Show quick statistics"""
        cursor = self.conn.cursor()
        
        print("\n📈 QUICK STATISTICS")
        print("-"*50)
        
        stats = [
            ("Total Users", "SELECT COUNT(*) FROM system_users"),
            ("Active Users", "SELECT COUNT(*) FROM system_users WHERE is_active = 1"),
            ("Total Cases", "SELECT COUNT(*) FROM cases"),
            ("Open Cases", "SELECT COUNT(*) FROM cases WHERE status = 'OPEN'"),
            ("High Priority Cases", "SELECT COUNT(*) FROM cases WHERE priority IN ('HIGH', 'CRITICAL')"),
            ("Total Content", "SELECT COUNT(*) FROM content"),
            ("Flagged Content", "SELECT COUNT(*) FROM content WHERE is_flagged = 1"),
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
    
    def show_recent_activity(self):
        """Show recent activity"""
        cursor = self.conn.cursor()
        
        print("\n🕒 RECENT ACTIVITY")
        print("-"*50)
        
        # Recent cases
        try:
            cursor.execute("""
                SELECT title, case_number, status, priority, created_at 
                FROM cases 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            cases = cursor.fetchall()
            
            if cases:
                print("\nRecent Cases:")
                for case in cases:
                    print(f"  {case[1]} - {case[0]} ({case[2]}) - {case[3]} - {case[4]}")
            else:
                print("\nNo recent cases found")
        except Exception as e:
            print(f"Recent cases error: {e}")
        
        # Recent users
        try:
            cursor.execute("""
                SELECT username, email, role, created_at 
                FROM system_users 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            users = cursor.fetchall()
            
            if users:
                print("\nRecent Users:")
                for user in users:
                    print(f"  {user[0]} ({user[1]}) - {user[2]} - {user[3]}")
            else:
                print("\nNo recent users found")
        except Exception as e:
            print(f"Recent users error: {e}")
    
    def show_main_menu(self):
        """Show main menu"""
        print("\n" + "="*80)
        print("📋 MAIN MENU")
        print("="*80)
        print("1.  Show database overview")
        print("2.  View specific table data")
        print("3.  Search in table")
        print("4.  Run custom SQL query")
        print("5.  Show quick statistics")
        print("6.  Show recent activity")
        print("7.  Export table to CSV")
        print("8.  Export table to JSON")
        print("9.  View all tables data")
        print("10. Show table list")
        print("0.  Exit")
        print("="*80)
    
    def show_table_list(self):
        """Show list of all tables"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\n📋 AVAILABLE TABLES")
        print("-"*50)
        for i, table in enumerate(tables, 1):
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  {i:2}. {table_name:25} {count:>8} rows")
            except Exception as e:
                print(f"  {i:2}. {table_name:25} ERROR: {str(e)[:30]}")
    
    def view_all_tables_data(self):
        """View all tables data"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\n📊 VIEWING ALL TABLES DATA")
        print("="*80)
        
        for table in tables:
            table_name = table[0]
            self.view_table_data(table_name, limit=5)  # Show first 5 rows of each table
            print("\n" + "-"*60)
    
    def run_interactive_menu(self):
        """Run the interactive menu"""
        if not self.conn:
            print("❌ No database connection available")
            return
        
        self.show_welcome()
        
        while True:
            self.show_main_menu()
            
            try:
                choice = input("\nEnter your choice (0-10): ").strip()
                
                if choice == '0':
                    print("\n👋 Goodbye! Thank you for using the database viewer.")
                    break
                elif choice == '1':
                    self.show_database_overview()
                elif choice == '2':
                    table_name = input("Enter table name: ").strip()
                    limit = input("Enter row limit (default 10): ").strip()
                    limit = int(limit) if limit.isdigit() else 10
                    self.view_table_data(table_name, limit)
                elif choice == '3':
                    table_name = input("Enter table name: ").strip()
                    search_term = input("Enter search term: ").strip()
                    self.search_data(table_name, search_term)
                elif choice == '4':
                    query = input("Enter SQL query: ").strip()
                    self.run_custom_query(query)
                elif choice == '5':
                    self.show_quick_stats()
                elif choice == '6':
                    self.show_recent_activity()
                elif choice == '7':
                    table_name = input("Enter table name to export: ").strip()
                    filename = input("Enter filename (or press Enter for auto): ").strip()
                    filename = filename if filename else None
                    self.export_table_to_csv(table_name, filename)
                elif choice == '8':
                    table_name = input("Enter table name to export: ").strip()
                    filename = input("Enter filename (or press Enter for auto): ").strip()
                    filename = filename if filename else None
                    self.export_table_to_json(table_name, filename)
                elif choice == '9':
                    self.view_all_tables_data()
                elif choice == '10':
                    self.show_table_list()
                else:
                    print("❌ Invalid choice. Please enter a number between 0-10.")
                
                # Pause before showing menu again
                if choice != '0':
                    input("\nPress Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thank you for using the database viewer.")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                input("\nPress Enter to continue...")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")

def main():
    """Main function"""
    viewer = InteractiveDatabaseViewer()
    
    if not viewer.conn:
        print("❌ Failed to connect to database")
        return
    
    try:
        viewer.run_interactive_menu()
    finally:
        viewer.close()

if __name__ == "__main__":
    main()



