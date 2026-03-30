#!/usr/bin/env python3
"""
Database Explorer for Cyber Intelligence Platform
Access and explore database data
"""

import sqlite3
import os
from datetime import datetime

def connect_to_database():
    """Connect to the SQLite database"""
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def show_tables(conn):
    """Show all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print("📊 Available Tables:")
    print("=" * 50)
    for table in tables:
        print(f"  • {table[0]}")
    return [table[0] for table in tables]

def get_table_info(conn, table_name):
    """Get information about a specific table"""
    cursor = conn.cursor()
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    print(f"\n📋 Table: {table_name}")
    print("=" * 50)
    print(f"Rows: {count}")
    print("\nColumns:")
    for col in columns:
        print(f"  • {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}")
    
    return count

def show_sample_data(conn, table_name, limit=5):
    """Show sample data from a table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    if rows:
        print(f"\n📄 Sample Data from {table_name}:")
        print("-" * 50)
        
        # Get column names
        columns = [description[0] for description in cursor.description]
        
        for i, row in enumerate(rows, 1):
            print(f"\nRow {i}:")
            for col_name, value in zip(columns, row):
                if value is not None and len(str(value)) > 100:
                    value = str(value)[:100] + "..."
                print(f"  {col_name}: {value}")
    else:
        print(f"\n📄 No data found in {table_name}")

def show_database_stats(conn):
    """Show overall database statistics"""
    cursor = conn.cursor()
    
    print("\n📊 Database Statistics:")
    print("=" * 50)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    total_rows = 0
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        total_rows += count
        print(f"  {table_name:20} {count:>8} rows")
    
    print(f"\n  {'TOTAL':20} {total_rows:>8} rows")

def show_recent_activity(conn):
    """Show recent activity across tables"""
    print("\n🕒 Recent Activity:")
    print("=" * 50)
    
    # Check for recent cases
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT title, case_number, status, created_at 
            FROM cases 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        cases = cursor.fetchall()
        if cases:
            print("\nRecent Cases:")
            for case in cases:
                print(f"  • {case[1]} - {case[0]} ({case[2]}) - {case[3]}")
    except Exception as e:
        print(f"  Cases table error: {e}")
    
    # Check for recent content
    try:
        cursor.execute("""
            SELECT id, author, platform, risk_level, created_at 
            FROM content 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        content = cursor.fetchall()
        if content:
            print("\nRecent Content:")
            for item in content:
                print(f"  • ID {item[0]} - {item[1]} ({item[2]}) - Risk: {item[3]} - {item[4]}")
    except Exception as e:
        print(f"  Content table error: {e}")

def interactive_explorer():
    """Interactive database explorer"""
    conn = connect_to_database()
    if not conn:
        return
    
    print("🔍 Cyber Intelligence Platform - Database Explorer")
    print("=" * 60)
    
    # Show database stats
    show_database_stats(conn)
    
    # Show tables
    tables = show_tables(conn)
    
    # Show recent activity
    show_recent_activity(conn)
    
    # Interactive menu
    while True:
        print("\n" + "=" * 60)
        print("📋 Database Explorer Menu:")
        print("1. Show table information")
        print("2. Show sample data")
        print("3. Run custom query")
        print("4. Show database statistics")
        print("5. Show recent activity")
        print("6. Export data to CSV")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            table_name = input("Enter table name: ").strip()
            if table_name in tables:
                get_table_info(conn, table_name)
            else:
                print(f"❌ Table '{table_name}' not found")
        elif choice == '2':
            table_name = input("Enter table name: ").strip()
            if table_name in tables:
                show_sample_data(conn, table_name)
            else:
                print(f"❌ Table '{table_name}' not found")
        elif choice == '3':
            query = input("Enter SQL query: ").strip()
            try:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()
                if rows:
                    print(f"\nQuery Results ({len(rows)} rows):")
                    print("-" * 40)
                    for i, row in enumerate(rows[:10], 1):  # Show first 10 rows
                        print(f"Row {i}: {dict(row)}")
                    if len(rows) > 10:
                        print(f"... and {len(rows) - 10} more rows")
                else:
                    print("No results found")
            except Exception as e:
                print(f"❌ Query error: {e}")
        elif choice == '4':
            show_database_stats(conn)
        elif choice == '5':
            show_recent_activity(conn)
        elif choice == '6':
            table_name = input("Enter table name to export: ").strip()
            if table_name in tables:
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    
                    filename = f"{table_name}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        # Write header
                        columns = [description[0] for description in cursor.description]
                        f.write(','.join(columns) + '\n')
                        
                        # Write data
                        for row in rows:
                            f.write(','.join(f'"{str(cell)}"' for cell in row) + '\n')
                    
                    print(f"✅ Data exported to {filename}")
                except Exception as e:
                    print(f"❌ Export error: {e}")
            else:
                print(f"❌ Table '{table_name}' not found")
        else:
            print("❌ Invalid choice")
    
    conn.close()
    print("\n👋 Database explorer closed")

if __name__ == "__main__":
    interactive_explorer()



