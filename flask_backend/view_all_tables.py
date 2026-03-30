#!/usr/bin/env python3
"""
View All Tables Data - Complete database table viewer
Shows all data from every table in the database
"""

import sqlite3
import os
from datetime import datetime

def view_all_tables_data():
    """View all data from every table in the database"""
    
    # Connect to database
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("CYBER INTELLIGENCE PLATFORM - ALL TABLES DATA VIEWER")
    print("="*80)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"Found {len(tables)} tables in database")
    print("="*80)
    
    for table in tables:
        table_name = table[0]
        print(f"\nTABLE: {table_name.upper()}")
        print("="*60)
        
        try:
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"Rows: {count}")
            print(f"Columns: {len(columns)}")
            
            # Show column names
            print("\nColumns:")
            for col in columns:
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                print(f"  {col[1]:20} {col[2]:15} {nullable}")
            
            # Get all data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if rows:
                print(f"\nData ({len(rows)} rows):")
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
                print("\nNo data found in this table")
                
        except Exception as e:
            print(f"Error accessing table {table_name}: {e}")
        
        print("\n" + "-"*60)
    
    conn.close()
    print("\nAll tables data view complete!")

def view_specific_table(table_name, limit=None):
    """View data from a specific table"""
    
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print(f"TABLE: {table_name.upper()}")
    print("="*60)
    
    try:
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        print(f"Rows: {count}")
        print(f"Columns: {len(columns)}")
        
        # Show column names
        print("\nColumns:")
        for col in columns:
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            print(f"  {col[1]:20} {col[2]:15} {nullable}")
        
        # Get data
        if limit:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        else:
            cursor.execute(f"SELECT * FROM {table_name}")
        
        rows = cursor.fetchall()
        
        if rows:
            print(f"\nData ({len(rows)} rows):")
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
            print("\nNo data found in this table")
            
    except Exception as e:
        print(f"Error accessing table {table_name}: {e}")
    
    conn.close()

def interactive_table_viewer():
    """Interactive table viewer"""
    
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    
    print("INTERACTIVE TABLE VIEWER")
    print("="*40)
    print("Available tables:")
    for i, table in enumerate(table_names, 1):
        print(f"  {i:2}. {table}")
    
    while True:
        print("\n" + "="*40)
        print("Options:")
        print("1. View all tables")
        print("2. View specific table")
        print("3. View table with limit")
        print("4. List all tables")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-4): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            view_all_tables_data()
        elif choice == '2':
            table_name = input("Enter table name: ").strip()
            if table_name in table_names:
                view_specific_table(table_name)
            else:
                print(f"Table '{table_name}' not found")
        elif choice == '3':
            table_name = input("Enter table name: ").strip()
            if table_name in table_names:
                limit = input("Enter row limit (or press Enter for all): ").strip()
                limit = int(limit) if limit.isdigit() else None
                view_specific_table(table_name, limit)
            else:
                print(f"Table '{table_name}' not found")
        elif choice == '4':
            print("\nAvailable tables:")
            for i, table in enumerate(table_names, 1):
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  {i:2}. {table:25} {count:>8} rows")
                except:
                    print(f"  {i:2}. {table:25} ERROR")
        else:
            print("Invalid choice")
    
    conn.close()

def export_table_to_file(table_name, filename=None):
    """Export table data to a text file"""
    
    if not filename:
        filename = f"{table_name}_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Get all data
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"TABLE: {table_name.upper()}\n")
            f.write("="*60 + "\n")
            f.write(f"Rows: {len(rows)}\n")
            f.write(f"Exported: {datetime.now()}\n\n")
            
            if rows:
                for i, row in enumerate(rows, 1):
                    f.write(f"Row {i}:\n")
                    for key, value in dict(row).items():
                        if value is not None:
                            # Handle long text
                            if len(str(value)) > 200:
                                value = str(value)[:200] + "..."
                            f.write(f"  {key:20}: {value}\n")
                        else:
                            f.write(f"  {key:20}: NULL\n")
                    f.write("\n")
            else:
                f.write("No data found in this table\n")
        
        print(f"Table data exported to {filename}")
        
    except Exception as e:
        print(f"Error exporting table {table_name}: {e}")
    
    conn.close()

def main():
    """Main function"""
    print("DATABASE TABLE VIEWER")
    print("="*40)
    print("1. View all tables data")
    print("2. Interactive table viewer")
    print("3. Export specific table")
    print("0. Exit")
    
    choice = input("\nEnter your choice (0-3): ").strip()
    
    if choice == '1':
        view_all_tables_data()
    elif choice == '2':
        interactive_table_viewer()
    elif choice == '3':
        table_name = input("Enter table name to export: ").strip()
        export_table_to_file(table_name)
    elif choice == '0':
        print("Goodbye!")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()



