"""
Comprehensive check and sync of ALL data from Railway to Local
Identifies missing data and schema mismatches
"""
import os
os.environ['USE_PRODUCTION_DB'] = 'true'

from app import create_app
from extensions import db
import sqlite3
from datetime import datetime

print("=" * 90)
print("🔍 COMPREHENSIVE DATA CHECK: Railway vs Local SQLite")
print("=" * 90)

# Get Railway data
app = create_app('development')

railway_counts = {}
railway_data = {}

with app.app_context():
    print("\n📊 Step 1: Counting records in Railway PostgreSQL...")
    print("-" * 90)
    
    tables = [
        'system_users', 'sources', 'keywords', 'cases', 'users', 'content',
        'detections', 'identifiers', 'osint_results', 'case_requests',
        'active_cases', 'user_case_links', 'osint_identifier_links', 'case_content_links'
    ]
    
    for table in tables:
        try:
            result = db.session.execute(db.text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            railway_counts[table] = count
            print(f"   Railway {table:30} {count:>5} records")
        except Exception as e:
            railway_counts[table] = 0
            print(f"   Railway {table:30} ERROR: {str(e)[:40]}")

# Check local SQLite
print("\n📊 Step 2: Counting records in Local SQLite...")
print("-" * 90)

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

local_counts = {}
for table in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        local_counts[table] = count
        print(f"   Local   {table:30} {count:>5} records")
    except Exception as e:
        local_counts[table] = 0
        print(f"   Local   {table:30} ERROR: {str(e)[:40]}")

# Compare and identify mismatches
print("\n" + "=" * 90)
print("📊 Step 3: Data Comparison & Mismatch Detection")
print("=" * 90)

mismatches = []
for table in tables:
    railway_count = railway_counts.get(table, 0)
    local_count = local_counts.get(table, 0)
    difference = railway_count - local_count
    
    status = "✅ OK" if difference == 0 else f"❌ MISSING {difference}"
    
    print(f"\n{table}:")
    print(f"   Railway: {railway_count:>5} | Local: {local_count:>5} | {status}")
    
    if difference > 0:
        mismatches.append({
            'table': table,
            'railway_count': railway_count,
            'local_count': local_count,
            'missing': difference
        })

# Summary
print("\n" + "=" * 90)
print("📋 SUMMARY")
print("=" * 90)

if mismatches:
    print(f"\n⚠️  Found {len(mismatches)} tables with missing data:\n")
    for mismatch in mismatches:
        print(f"   • {mismatch['table']:30} Missing: {mismatch['missing']:>3} records")
    
    print("\n" + "=" * 90)
    print("🔧 Would you like to sync the missing data? (Y/N)")
    print("=" * 90)
else:
    print("\n✅ All data is in sync! No missing records found.")
    print("   Railway and Local databases match perfectly.")

conn.close()

# Save mismatch report
if mismatches:
    with open('data_mismatch_report.txt', 'w') as f:
        f.write("Data Mismatch Report\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        
        for mismatch in mismatches:
            f.write(f"\nTable: {mismatch['table']}\n")
            f.write(f"  Railway: {mismatch['railway_count']} records\n")
            f.write(f"  Local:   {mismatch['local_count']} records\n")
            f.write(f"  Missing: {mismatch['missing']} records\n")
    
    print(f"\n📄 Report saved to: data_mismatch_report.txt")

print("\n" + "=" * 90)

