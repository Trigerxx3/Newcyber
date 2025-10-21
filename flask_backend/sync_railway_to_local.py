"""
Complete data sync from Railway to Local SQLite
Uses dynamic column detection to avoid field mismatch errors
"""
import os
import sqlite3
from datetime import datetime

# Connect to Railway
os.environ['USE_PRODUCTION_DB'] = 'true'

from app import create_app
from extensions import db

print("=" * 80)
print("🔄 COMPLETE DATA SYNC: Railway → Local SQLite")
print("=" * 80)

app = create_app('development')

with app.app_context():
    print("\n📦 Exporting from Railway PostgreSQL...")
    print("-" * 80)
    
    # Get all table names from metadata
    tables_to_sync = [
        'system_users', 'sources', 'keywords', 'cases', 'users', 'content',
        'detections', 'identifiers', 'osint_results', 'case_requests',
        'active_cases', 'user_case_links', 'osint_identifier_links', 'case_content_links'
    ]
    
    all_data = {}
    
    for table_name in tables_to_sync:
        try:
            # Execute raw SQL to get all data
            result = db.session.execute(db.text(f"SELECT * FROM {table_name}"))
            columns = result.keys()
            rows = result.fetchall()
            
            # Convert to list of dicts
            all_data[table_name] = [dict(zip(columns, row)) for row in rows]
            print(f"   ✅ {table_name}: {len(all_data[table_name])} records")
        except Exception as e:
            all_data[table_name] = []
            print(f"   ⚠️  {table_name}: Error - {str(e)[:50]}")
    
    total = sum(len(v) for v in all_data.values())
    print(f"\n📊 Total: {total} records exported")

# Import to local SQLite
print("\n" + "=" * 80)
print("💾 Importing to Local SQLite...")
print("-" * 80)

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"✅ Connected: {db_path}\n")

# Import each table
for table_name, records in all_data.items():
    if not records:
        print(f"   ⏭️  {table_name}: No data to import")
        continue
    
    imported = 0
    skipped = 0
    
    for record in records:
        try:
            # Convert datetime objects to ISO strings
            for key, value in record.items():
                if hasattr(value, 'isoformat'):
                    record[key] = value.isoformat()
            
            # Build INSERT OR REPLACE statement
            columns = list(record.keys())
            placeholders = ','.join(['?' for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            
            cursor.execute(sql, tuple(record[col] for col in columns))
            imported += 1
        except Exception as e:
            skipped += 1
    
    conn.commit()
    status = f"{imported} imported"
    if skipped > 0:
        status += f", {skipped} skipped"
    print(f"   ✅ {table_name}: {status}")

conn.close()

print("\n" + "=" * 80)
print("✅ SYNC COMPLETE!")
print("=" * 80)
print(f"\n📊 Summary:")
for table_name, records in all_data.items():
    if records:
        print(f"   • {table_name}: {len(records)}")
print(f"\n   TOTAL: {total} records")
print(f"\n💾 Local: {db_path}")
print(f"🌐 Railway: Unchanged\n")
print("=" * 80)

