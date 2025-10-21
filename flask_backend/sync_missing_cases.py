"""
Sync missing cases from Railway to Local SQLite
"""
import os
os.environ['USE_PRODUCTION_DB'] = 'true'

from app import create_app
from extensions import db
import sqlite3
from datetime import datetime

print("=" * 90)
print("🔄 Syncing Missing Cases from Railway to Local")
print("=" * 90)

# Connect to Railway
app = create_app('development')

with app.app_context():
    print("\n📦 Step 1: Exporting ALL cases from Railway...")
    print("-" * 90)
    
    # Get all cases with ALL required fields (matching actual schema)
    result = db.session.execute(db.text("""
        SELECT id, title, description, case_number, type, status, priority, 
               risk_score, risk_level, created_by_id, assigned_to_id, owner_id,
               start_date, created_at, updated_at
        FROM cases
        ORDER BY id
    """))
    
    cases_data = []
    for row in result:
        cases_data.append({
            'id': row[0],
            'title': row[1] or 'Untitled Case',
            'description': row[2] or '',
            'case_number': row[3] or f'CASE-{row[0]:05d}',
            'type': row[4] or 'drug_trafficking_investigation',
            'status': row[5] or 'open',
            'priority': row[6] or 'medium',
            'risk_score': row[7] or 0.0,
            'risk_level': row[8] or 'low',
            'created_by_id': row[9],
            'assigned_to_id': row[10],
            'owner_id': row[11],
            'start_date': row[12].isoformat() if row[12] else None,
            'created_at': row[13].isoformat() if row[13] else None,
            'updated_at': row[14].isoformat() if row[14] else None
        })
    
    print(f"   ✅ Exported {len(cases_data)} cases from Railway")

# Import to SQLite
print("\n💾 Step 2: Importing to Local SQLite...")
print("-" * 90)

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# First, get existing case IDs
cursor.execute("SELECT id FROM cases")
existing_ids = set(row[0] for row in cursor.fetchall())
print(f"   Existing cases in local: {existing_ids}")

imported = 0
updated = 0
errors = 0

for case in cases_data:
    try:
        if case['id'] in existing_ids:
            # Update existing case
            cursor.execute("""
                UPDATE cases 
                SET title = ?, description = ?, case_number = ?, type = ?, status = ?, 
                    priority = ?, risk_score = ?, risk_level = ?, assigned_to_id = ?, 
                    owner_id = ?, start_date = ?, updated_at = ?
                WHERE id = ?
            """, (
                case['title'],
                case['description'],
                case['case_number'],
                case['type'],
                case['status'],
                case['priority'],
                case['risk_score'],
                case['risk_level'],
                case['assigned_to_id'],
                case['owner_id'],
                case['start_date'],
                case['updated_at'],
                case['id']
            ))
            if cursor.rowcount > 0:
                updated += 1
                print(f"   ✅ Updated case {case['id']}: {case['title']}")
        else:
            # Insert new case
            cursor.execute("""
                INSERT INTO cases 
                (id, title, description, case_number, type, status, priority, 
                 risk_score, risk_level, created_by_id, assigned_to_id, owner_id,
                 start_date, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case['id'],
                case['title'],
                case['description'],
                case['case_number'],
                case['type'],
                case['status'],
                case['priority'],
                case['risk_score'],
                case['risk_level'],
                case['created_by_id'],
                case['assigned_to_id'],
                case['owner_id'],
                case['start_date'],
                case['created_at'],
                case['updated_at']
            ))
            imported += 1
            print(f"   ✅ Imported case {case['id']}: {case['title']}")
    
    except Exception as e:
        errors += 1
        print(f"   ❌ Error with case {case['id']}: {str(e)[:60]}")

conn.commit()

# Verify final count
cursor.execute("SELECT COUNT(*) FROM cases")
final_count = cursor.fetchone()[0]

conn.close()

print("\n" + "=" * 90)
print("📊 SYNC COMPLETE!")
print("=" * 90)
print(f"\n   ✅ New cases imported: {imported}")
print(f"   ✅ Cases updated: {updated}")
print(f"   ❌ Errors: {errors}")
print(f"\n   📊 Final local case count: {final_count}")
print("\n" + "=" * 90)

