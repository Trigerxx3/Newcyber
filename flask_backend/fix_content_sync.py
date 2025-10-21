"""
Fix content sync by manually copying only compatible columns
"""
import os
os.environ['USE_PRODUCTION_DB'] = 'true'

from app import create_app
from extensions import db
import sqlite3

print("=" * 80)
print("🔧 Fixing Content Sync from Railway to Local")
print("=" * 80)

# Connect to Railway
app = create_app('development')

with app.app_context():
    print("\n📦 Exporting content from Railway...")
    
    # Get content with ALL required fields
    result = db.session.execute(db.text("""
        SELECT id, source_id, text, author, content_type, risk_level, status,
               suspicion_score, is_flagged, created_at, updated_at
        FROM content
        LIMIT 100
    """))
    
    content_data = []
    for row in result:
        content_data.append({
            'id': row[0],
            'source_id': row[1],
            'text': row[2][:500] if row[2] else 'No content',  # Limit text length, provide default
            'author': row[3] or 'Unknown',
            'content_type': row[4] or 'TEXT',
            'risk_level': row[5] or 'LOW',
            'status': row[6] or 'PENDING',  # REQUIRED field!
            'suspicion_score': row[7] or 0,
            'is_flagged': 1 if row[8] else 0,
            'created_at': row[9].isoformat() if row[9] else None,
            'updated_at': row[10].isoformat() if row[10] else None
        })
    
    print(f"   ✅ Exported {len(content_data)} content records")

# Import to SQLite
db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"\n💾 Importing to Local SQLite...")

imported = 0
errors = 0

for content in content_data:
    try:
        # Try INSERT OR REPLACE with all required fields
        cursor.execute("""
            INSERT OR REPLACE INTO content 
            (id, source_id, text, author, content_type, risk_level, status,
             suspicion_score, is_flagged, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            content['id'],
            content['source_id'],
            content['text'],
            content['author'],
            content['content_type'],
            content['risk_level'],
            content['status'],  # Include status!
            content['suspicion_score'],
            content['is_flagged'],
            content['created_at'],
            content['updated_at']
        ))
        if cursor.rowcount > 0:
            imported += 1
    except Exception as e:
        errors += 1
        if errors <= 3:  # Show first 3 errors
            print(f"   ⚠️  Error importing content {content['id']}: {str(e)[:50]}")

conn.commit()
conn.close()

print(f"\n   ✅ Imported: {imported}")
print(f"   ⏭️  Skipped/Errors: {errors}")

print("\n" + "=" * 80)
print(f"✅ Content sync complete! {imported} records imported")
print("=" * 80)

