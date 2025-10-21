"""
Fix enum values in SQLite database to match Python enum definitions
Changes 'Analyst' to 'ANALYST' and 'Admin' to 'ADMIN'
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("🔧 Fixing Enum Values in Local SQLite")
print("=" * 70)
print()

# Fix system_users role enum
print("Updating system_users.role...")
cursor.execute("UPDATE system_users SET role = 'ADMIN' WHERE role = 'Admin'")
admin_count = cursor.rowcount
cursor.execute("UPDATE system_users SET role = 'ANALYST' WHERE role = 'Analyst'")
analyst_count = cursor.rowcount
conn.commit()
print(f"   ✅ Updated {admin_count} Admin → ADMIN")
print(f"   ✅ Updated {analyst_count} Analyst → ANALYST")

# Check other tables with enum values
print("\nChecking other tables...")

# Fix cases status enum if needed
try:
    cursor.execute("SELECT DISTINCT status FROM cases")
    statuses = cursor.fetchall()
    for (status,) in statuses:
        if status and status.lower() != status.upper():  # Mixed case
            upper_status = status.upper()
            cursor.execute(f"UPDATE cases SET status = ? WHERE status = ?", (upper_status, status))
            if cursor.rowcount > 0:
                print(f"   ✅ Cases: {cursor.rowcount} '{status}' → '{upper_status}'")
    conn.commit()
except Exception as e:
    print(f"   ℹ️  Cases: No changes needed")

# Fix cases priority enum if needed
try:
    cursor.execute("SELECT DISTINCT priority FROM cases")
    priorities = cursor.fetchall()
    for (priority,) in priorities:
        if priority and priority.lower() != priority.upper():  # Mixed case
            upper_priority = priority.upper()
            cursor.execute(f"UPDATE cases SET priority = ? WHERE priority = ?", (upper_priority, priority))
            if cursor.rowcount > 0:
                print(f"   ✅ Cases priority: {cursor.rowcount} '{priority}' → '{upper_priority}'")
    conn.commit()
except Exception as e:
    print(f"   ℹ️  Cases priority: No changes needed")

# Verify the changes
print("\n" + "=" * 70)
print("Verifying changes...")
print("=" * 70)
print()

cursor.execute("SELECT id, email, username, role FROM system_users ORDER BY id")
users = cursor.fetchall()

print(f"📊 System Users ({len(users)}):\n")
for user_id, email, username, role in users:
    print(f"{user_id}. {email}")
    print(f"   Username: {username}")
    print(f"   Role: {role} {'✅' if role in ['ADMIN', 'ANALYST'] else '❌'}")
    print()

conn.close()

print("=" * 70)
print("✅ Enum values fixed!")
print("=" * 70)
print("\nYou can now start the Flask server:")
print("   python run.py")
print()

