"""
Debug content table structure
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("🔍 Content Table Structure Debug")
print("=" * 80)

# Get table schema
cursor.execute("PRAGMA table_info(content)")
columns = cursor.fetchall()

print("\n📋 Content Table Columns:")
for col in columns:
    col_id, name, col_type, notnull, default, pk = col
    required = "REQUIRED" if notnull and default is None and not pk else "optional"
    print(f"   {name:30} {col_type:15} {required}")

# Check for foreign key constraints
cursor.execute("PRAGMA foreign_key_list(content)")
fks = cursor.fetchall()

if fks:
    print("\n🔗 Foreign Key Constraints:")
    for fk in fks:
        print(f"   {fk[3]} → {fk[2]}.{fk[4]}")

# Try a simple test insert
print("\n🧪 Testing simple insert...")
try:
    cursor.execute("""
        INSERT INTO content (source_id, text, content_type, risk_level, is_flagged, suspicion_score)
        VALUES (1, 'Test content', 'TEXT', 'LOW', 0, 0)
    """)
    conn.commit()
    print("   ✅ Test insert successful!")
    
    # Delete test record
    cursor.execute("DELETE FROM content WHERE text = 'Test content'")
    conn.commit()
except Exception as e:
    print(f"   ❌ Test insert failed: {e}")
    conn.rollback()

conn.close()

print("\n" + "=" * 80)

