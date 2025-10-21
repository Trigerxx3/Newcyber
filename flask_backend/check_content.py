"""
Check content in the local database
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("📊 Database Content Summary")
print("=" * 70)
print()

# Count content
cursor.execute("SELECT COUNT(*) FROM content")
total_content = cursor.fetchone()[0]
print(f"📝 Total Content Records: {total_content}")

# Count sources
cursor.execute("SELECT COUNT(*) FROM sources")
total_sources = cursor.fetchone()[0]
print(f"📱 Total Sources: {total_sources}")

# Count users (platform users)
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]
print(f"👥 Total Platform Users: {total_users}")

print()
print("=" * 70)

if total_content > 0:
    print("📝 Sample Content (first 5):")
    print("=" * 70)
    cursor.execute("""
        SELECT c.id, c.source_id, SUBSTR(c.text, 1, 60) as preview, c.author, c.posted_at
        FROM content c
        LIMIT 5
    """)
    
    for i, row in enumerate(cursor.fetchall(), 1):
        content_id, source_id, preview, author, posted_at = row
        print(f"\n{i}. Content ID: {content_id}")
        print(f"   Source ID: {source_id}")
        print(f"   Author: {author or 'Unknown'}")
        print(f"   Preview: {preview}...")
        print(f"   Posted: {posted_at or 'Unknown'}")
else:
    print("\n⚠️  No content found in database!")
    print("\nPossible reasons:")
    print("  1. Content was not successfully synced from Railway")
    print("  2. Content table structure mismatch")
    print("  3. No scraping has been done yet")

print()
print("=" * 70)

# Check if content exists in Railway but wasn't synced
if total_content == 0:
    print("\n💡 To sync content from Railway:")
    print("   python sync_railway_to_local.py")

conn.close()

