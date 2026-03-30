#!/usr/bin/env python3
"""
Comprehensive Database Viewer for Cyber Intelligence Platform
Access, view, and analyze all database data
"""

import sqlite3
import os
import csv
import json
from datetime import datetime
from typing import List, Dict, Any

class DatabaseViewer:
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
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table"""
        cursor = self.conn.cursor()
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample_data = cursor.fetchall()
        
        return {
            'name': table_name,
            'columns': [dict(col) for col in columns],
            'row_count': count,
            'sample_data': [dict(row) for row in sample_data]
        }
    
    def show_all_tables(self):
        """Display all tables with their information"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        print("\n" + "="*80)
        print("📊 DATABASE TABLES OVERVIEW")
        print("="*80)
        
        total_rows = 0
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_rows += count
                print(f"  {table_name:30} {count:>8} rows")
            except Exception as e:
                print(f"  {table_name:30} ERROR: {str(e)[:30]}")
        
        print(f"\n  {'TOTAL':30} {total_rows:>8} rows")
        return [table[0] for table in tables]
    
    def view_table_data(self, table_name: str, limit: int = 10):
        """View data from a specific table"""
        cursor = self.conn.cursor()
        
        try:
            # Get table info
            info = self.get_table_info(table_name)
            
            print(f"\n📋 TABLE: {table_name.upper()}")
            print("="*80)
            print(f"Rows: {info['row_count']}")
            print(f"Columns: {len(info['columns'])}")
            
            # Show column names
            print(f"\nColumns:")
            for col in info['columns']:
                nullable = "NULL" if col['notnull'] == 0 else "NOT NULL"
                print(f"  • {col['name']:20} {col['type']:15} {nullable}")
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = cursor.fetchall()
            
            if rows:
                print(f"\nData (showing {len(rows)} of {info['row_count']} rows):")
                print("-"*80)
                
                for i, row in enumerate(rows, 1):
                    print(f"\nRow {i}:")
                    for key, value in dict(row).items():
                        if value is not None and len(str(value)) > 100:
                            value = str(value)[:100] + "..."
                        print(f"  {key:20}: {value}")
            else:
                print(f"\nNo data found in {table_name}")
                
        except Exception as e:
            print(f"❌ Error viewing table {table_name}: {e}")
    
    def search_data(self, table_name: str, search_term: str, columns: List[str] = None):
        """Search for data in a table"""
        cursor = self.conn.cursor()
        
        try:
            # Get all columns if not specified
            if not columns:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [col[1] for col in cursor.fetchall()]
            
            # Build search query
            search_conditions = []
            for col in columns:
                search_conditions.append(f"{col} LIKE '%{search_term}%'")
            
            query = f"SELECT * FROM {table_name} WHERE {' OR '.join(search_conditions)}"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print(f"\n🔍 SEARCH RESULTS in {table_name}")
            print("="*80)
            print(f"Search term: '{search_term}'")
            print(f"Found: {len(rows)} results")
            
            if rows:
                for i, row in enumerate(rows, 1):
                    print(f"\nResult {i}:")
                    for key, value in dict(row).items():
                        if value is not None and len(str(value)) > 100:
                            value = str(value)[:100] + "..."
                        print(f"  {key:20}: {value}")
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
            print("="*80)
            print(f"Query: {query}")
            print(f"Results: {len(rows)} rows")
            
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
    
    def show_database_summary(self):
        """Show comprehensive database summary"""
        print("\n" + "="*80)
        print("📊 CYBER INTELLIGENCE PLATFORM - DATABASE SUMMARY")
        print("="*80)
        
        # Get all tables
        tables = self.show_all_tables()
        
        # Show key statistics
        print(f"\n📈 KEY STATISTICS:")
        print("-"*50)
        
        # Users
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM system_users WHERE is_active = 1")
            active_users = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM system_users")
            total_users = cursor.fetchone()[0]
            print(f"Active Users: {active_users}/{total_users}")
        except:
            print("Users: Error accessing data")
        
        # Cases
        try:
            cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'OPEN'")
            open_cases = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM cases")
            total_cases = cursor.fetchone()[0]
            print(f"Open Cases: {open_cases}/{total_cases}")
        except:
            print("Cases: Error accessing data")
        
        # Content
        try:
            cursor.execute("SELECT COUNT(*) FROM content")
            content_count = cursor.fetchone()[0]
            print(f"Content Items: {content_count}")
        except:
            print("Content: Error accessing data")
        
        # Sources
        try:
            cursor.execute("SELECT COUNT(*) FROM sources")
            sources_count = cursor.fetchone()[0]
            print(f"Data Sources: {sources_count}")
        except:
            print("Sources: Error accessing data")
    
    def interactive_menu(self):
        """Interactive database viewer menu"""
        while True:
            print("\n" + "="*80)
            print("🔍 DATABASE VIEWER - INTERACTIVE MENU")
            print("="*80)
            print("1. Show all tables")
            print("2. View table data")
            print("3. Search in table")
            print("4. Run custom query")
            print("5. Export table to CSV")
            print("6. Export table to JSON")
            print("7. Show database summary")
            print("8. Show recent data")
            print("0. Exit")
            
            choice = input("\nEnter your choice (0-8): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                self.show_all_tables()
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
                table_name = input("Enter table name: ").strip()
                filename = input("Enter filename (or press Enter for auto): ").strip()
                filename = filename if filename else None
                self.export_table_to_csv(table_name, filename)
            elif choice == '6':
                table_name = input("Enter table name: ").strip()
                filename = input("Enter filename (or press Enter for auto): ").strip()
                filename = filename if filename else None
                self.export_table_to_json(table_name, filename)
            elif choice == '7':
                self.show_database_summary()
            elif choice == '8':
                self.show_recent_data()
            else:
                print("❌ Invalid choice")
    
    def show_recent_data(self):
        """Show recent data from key tables"""
        print("\n📅 RECENT DATA")
        print("="*80)
        
        # Recent cases
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, title, case_number, status, priority, created_at 
                FROM cases 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            cases = cursor.fetchall()
            
            if cases:
                print("\nRecent Cases:")
                for case in cases:
                    print(f"  ID: {case[0]} | {case[2]} | {case[1]}")
                    print(f"       Status: {case[3]} | Priority: {case[4]} | Created: {case[5]}")
                    print()
        except Exception as e:
            print(f"Cases error: {e}")
        
        # Recent users
        try:
            cursor.execute("""
                SELECT id, username, email, role, created_at 
                FROM system_users 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            users = cursor.fetchall()
            
            if users:
                print("\nRecent Users:")
                for user in users:
                    print(f"  ID: {user[0]} | {user[1]} ({user[2]})")
                    print(f"       Role: {user[3]} | Created: {user[4]}")
                    print()
        except Exception as e:
            print(f"Users error: {e}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")

def main():
    """Main function"""
    print("🔍 Cyber Intelligence Platform - Database Viewer")
    print("="*60)
    
    # Initialize viewer
    viewer = DatabaseViewer()
    
    if not viewer.conn:
        print("❌ Failed to connect to database")
        return
    
    try:
        # Show initial summary
        viewer.show_database_summary()
        
        # Start interactive menu
        viewer.interactive_menu()
        
    finally:
        viewer.close()

if __name__ == "__main__":
    main()



