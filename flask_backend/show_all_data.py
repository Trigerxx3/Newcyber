#!/usr/bin/env python3
"""
Show All Database Data - Automatic viewer for all tables
Displays all data from every table without user input
"""

import sqlite3
import os
from datetime import datetime

def show_all_data():
    """Show all data from every table in the database"""
    
    # Connect to database
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("CYBER INTELLIGENCE PLATFORM - ALL DATABASE DATA")
    print("="*80)
    print(f"Database: {db_path}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\nFound {len(tables)} tables in database")
    print("="*80)
    
    for table in tables:
        table_name = table[0]
        print(f"\n\nTABLE: {table_name.upper()}")
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
                            if len(str(value)) > 150:
                                value = str(value)[:150] + "..."
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
    print(f"\n\nAll database data displayed successfully!")
    print(f"Total tables processed: {len(tables)}")

def show_table_summary():
    """Show a summary of all tables with row counts"""
    
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("DATABASE TABLES SUMMARY")
    print("="*50)
    
    # Get all tables
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
        except Exception as e:
            print(f"  {table_name:25} ERROR: {str(e)[:30]}")
    
    print(f"\n  {'TOTAL':25} {total_rows:>8} rows")
    conn.close()

def show_specific_tables():
    """Show data from specific important tables"""
    
    db_path = 'cyber_intel.db'
    if not os.path.exists(db_path):
        print(f"Database not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Important tables to show
    important_tables = [
        'system_users',
        'cases', 
        'content',
        'sources',
        'case_activities',
        'user_case_links',
        'case_content_links'
    ]
    
    print("IMPORTANT TABLES DATA")
    print("="*60)
    
    for table_name in important_tables:
        print(f"\n\nTABLE: {table_name.upper()}")
        print("="*50)
        
        try:
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            print(f"Rows: {count}")
            
            if count > 0:
                # Get all data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                print(f"\nData ({len(rows)} rows):")
                print("-"*50)
                
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
                print("No data found in this table")
                
        except Exception as e:
            print(f"Error accessing table {table_name}: {e}")
        
        print("\n" + "-"*50)
    
    conn.close()

if __name__ == "__main__":
    print("Starting database data viewer...")
    print("1. Showing table summary...")
    show_table_summary()
    
    print("\n2. Showing important tables data...")
    show_specific_tables()
    
    print("\n3. Showing all tables data...")
    show_all_data()
    
    print("\nDatabase viewing complete!")



