"""
Complete sync of ALL data from Railway to Local SQLite
Copies every table with all records
"""
import os
import sqlite3
from datetime import datetime

# Connect to Railway
os.environ['USE_PRODUCTION_DB'] = 'true'

from app import create_app
from models.user import SystemUser, User
from models.source import Source
from models.content import Content
from models.keyword import Keyword
from models.case import Case
from models.detection import Detection
from models.identifier import Identifier
from models.osint_result import OSINTResult
from models.case_request import CaseRequest
from models.active_case import ActiveCase
from models.user_case_link import UserCaseLink
from models.osint_identifier_link import OSINTIdentifierLink
from models.case_content_link import CaseContentLink

print("=" * 80)
print("🔄 COMPLETE DATA SYNC: Railway → Local SQLite")
print("=" * 80)

# Step 1: Export ALL data from Railway
print("\n📦 STEP 1: Exporting ALL data from Railway PostgreSQL...")
print("-" * 80)

app = create_app('development')

all_data = {}

with app.app_context():
    print("✅ Connected to Railway\n")
    
    # 1. System Users
    system_users = SystemUser.query.all()
    all_data['system_users'] = [{
        'id': u.id,
        'email': u.email,
        'username': u.username,
        'password_hash': u.password_hash,
        'role': u.role.value,
        'is_active': 1 if u.is_active else 0,
        'last_login': u.last_login.isoformat() if u.last_login else None,
        'created_at': u.created_at.isoformat() if u.created_at else datetime.now().isoformat(),
        'updated_at': u.updated_at.isoformat() if u.updated_at else datetime.now().isoformat()
    } for u in system_users]
    print(f"   ✅ System Users: {len(all_data['system_users'])}")
    
    # 2. Sources
    sources = Source.query.all()
    all_data['sources'] = [{
        'id': s.id,
        'platform': s.platform.value,
        'source_handle': s.source_handle,
        'source_name': s.source_name,
        'source_type': s.source_type.value,
        'description': s.description,
        'is_active': 1 if s.is_active else 0,
        'scraping_enabled': 1 if s.scraping_enabled else 0,
        'follower_count': s.follower_count,
        'last_scraped_at': s.last_scraped_at.isoformat() if s.last_scraped_at else None,
        'created_at': s.created_at.isoformat() if s.created_at else datetime.now().isoformat(),
        'updated_at': s.updated_at.isoformat() if s.updated_at else datetime.now().isoformat()
    } for s in sources]
    print(f"   ✅ Sources: {len(all_data['sources'])}")
    
    # 3. Keywords
    keywords = Keyword.query.all()
    all_data['keywords'] = [{
        'id': k.id,
        'keyword': k.keyword,
        'category': k.category.value if k.category else 'GENERAL',
        'severity': k.severity.value if k.severity else 'MEDIUM',
        'is_regex': 1 if k.is_regex else 0,
        'is_active': 1 if k.is_active else 0,
        'created_at': k.created_at.isoformat() if k.created_at else datetime.now().isoformat(),
        'updated_at': k.updated_at.isoformat() if k.updated_at else datetime.now().isoformat()
    } for k in keywords]
    print(f"   ✅ Keywords: {len(all_data['keywords'])}")
    
    # 4. Cases
    cases = Case.query.all()
    all_data['cases'] = [{
        'id': c.id,
        'case_number': c.case_number,
        'title': c.title,
        'description': c.description,
        'status': c.status.value,
        'priority': c.priority.value,
        'created_by_id': c.created_by_id,
        'assigned_to_id': c.assigned_to_id,
        'owner_id': c.owner_id,
        'created_at': c.created_at.isoformat() if c.created_at else datetime.now().isoformat(),
        'updated_at': c.updated_at.isoformat() if c.updated_at else datetime.now().isoformat()
    } for c in cases]
    print(f"   ✅ Cases: {len(all_data['cases'])}")
    
    # 5. Users (platform users)
    users = User.query.all()
    all_data['users'] = [{
        'id': u.id,
        'source_id': u.source_id,
        'platform_user_id': u.platform_user_id,
        'username': u.username,
        'full_name': u.full_name,
        'bio': u.bio,
        'is_flagged': 1 if u.is_flagged else 0,
        'created_at': u.created_at.isoformat() if u.created_at else datetime.now().isoformat(),
        'updated_at': u.updated_at.isoformat() if u.updated_at else datetime.now().isoformat()
    } for u in users]
    print(f"   ✅ Platform Users: {len(all_data['users'])}")
    
    # 6. Content
    content = Content.query.all()
    all_data['content'] = [{
        'id': c.id,
        'source_id': c.source_id,
        'text': c.text,
        'content_type': c.content_type.value if c.content_type else 'TEXT',
        'url': c.url,
        'media_urls': c.media_urls,
        'posted_at': c.posted_at.isoformat() if c.posted_at else None,
        'author': c.author,
        'is_flagged': 1 if c.is_flagged else 0,
        'risk_level': c.risk_level.value if c.risk_level else 'LOW',
        'suspicion_score': c.suspicion_score,
        'analysis_result': c.analysis_result,
        'metadata': c.metadata,
        'created_by_id': c.created_by_id,
        'created_at': c.created_at.isoformat() if c.created_at else datetime.now().isoformat(),
        'updated_at': c.updated_at.isoformat() if c.updated_at else datetime.now().isoformat()
    } for c in content]
    print(f"   ✅ Content: {len(all_data['content'])}")
    
    # 7. Detections
    detections = Detection.query.all()
    all_data['detections'] = [{
        'id': d.id,
        'keyword_id': d.keyword_id,
        'content_id': d.content_id,
        'source_id': d.source_id,
        'detected_text': d.detected_text,
        'context': d.context,
        'severity': d.severity.value if d.severity else 'MEDIUM',
        'detected_by_id': d.detected_by_id,
        'created_at': d.created_at.isoformat() if d.created_at else datetime.now().isoformat()
    } for d in detections]
    print(f"   ✅ Detections: {len(all_data['detections'])}")
    
    # 8. Identifiers
    identifiers = Identifier.query.all()
    all_data['identifiers'] = [{
        'id': i.id,
        'identifier_type': i.identifier_type.value,
        'value': i.value,
        'source': i.source,
        'confidence_score': i.confidence_score,
        'metadata': i.metadata,
        'created_at': i.created_at.isoformat() if i.created_at else datetime.now().isoformat(),
        'updated_at': i.updated_at.isoformat() if i.updated_at else datetime.now().isoformat()
    } for i in identifiers]
    print(f"   ✅ Identifiers: {len(all_data['identifiers'])}")
    
    # 9. OSINT Results
    osint_results = OSINTResult.query.all()
    all_data['osint_results'] = [{
        'id': o.id,
        'user_id': o.user_id,
        'query': o.query,
        'result_type': o.result_type.value if o.result_type else 'GENERAL',
        'data': o.data,
        'confidence_score': o.confidence_score,
        'created_by_id': o.created_by_id,
        'created_at': o.created_at.isoformat() if o.created_at else datetime.now().isoformat()
    } for o in osint_results]
    print(f"   ✅ OSINT Results: {len(all_data['osint_results'])}")
    
    # 10. Case Requests
    case_requests = CaseRequest.query.all()
    all_data['case_requests'] = [{
        'id': cr.id,
        'requested_by_id': cr.requested_by_id,
        'assigned_to_id': cr.assigned_to_id,
        'title': cr.title,
        'description': cr.description,
        'priority': cr.priority.value if cr.priority else 'MEDIUM',
        'status': cr.status.value if cr.status else 'PENDING',
        'created_at': cr.created_at.isoformat() if cr.created_at else datetime.now().isoformat(),
        'updated_at': cr.updated_at.isoformat() if cr.updated_at else datetime.now().isoformat()
    } for cr in case_requests]
    print(f"   ✅ Case Requests: {len(all_data['case_requests'])}")
    
    # 11. Active Cases
    active_cases = ActiveCase.query.all()
    all_data['active_cases'] = [{
        'id': ac.id,
        'system_user_id': ac.system_user_id,
        'case_id': ac.case_id,
        'created_at': ac.created_at.isoformat() if ac.created_at else datetime.now().isoformat(),
        'updated_at': ac.updated_at.isoformat() if ac.updated_at else datetime.now().isoformat()
    } for ac in active_cases]
    print(f"   ✅ Active Cases: {len(all_data['active_cases'])}")
    
    # 12. User Case Links
    user_case_links = UserCaseLink.query.all()
    all_data['user_case_links'] = [{
        'id': ucl.id,
        'user_id': ucl.user_id,
        'case_id': ucl.case_id,
        'role': ucl.role,
        'created_at': ucl.created_at.isoformat() if ucl.created_at else datetime.now().isoformat(),
        'updated_at': ucl.updated_at.isoformat() if ucl.updated_at else datetime.now().isoformat()
    } for ucl in user_case_links]
    print(f"   ✅ User-Case Links: {len(all_data['user_case_links'])}")
    
    # 13. OSINT Identifier Links
    osint_links = OSINTIdentifierLink.query.all()
    all_data['osint_identifier_links'] = [{
        'id': ol.id,
        'osint_result_id': ol.osint_result_id,
        'identifier_id': ol.identifier_id,
        'created_at': ol.created_at.isoformat() if ol.created_at else datetime.now().isoformat()
    } for ol in osint_links]
    print(f"   ✅ OSINT-Identifier Links: {len(all_data['osint_identifier_links'])}")
    
    # 14. Case Content Links
    case_content_links = CaseContentLink.query.all()
    all_data['case_content_links'] = [{
        'id': ccl.id,
        'case_id': ccl.case_id,
        'content_id': ccl.content_id,
        'created_at': ccl.created_at.isoformat() if ccl.created_at else datetime.now().isoformat(),
        'updated_at': ccl.updated_at.isoformat() if ccl.updated_at else datetime.now().isoformat()
    } for ccl in case_content_links]
    print(f"   ✅ Case-Content Links: {len(all_data['case_content_links'])}")

total_records = sum(len(v) for v in all_data.values())
print(f"\n📊 Total records exported: {total_records}")

# Step 2: Import to Local SQLite
print("\n" + "=" * 80)
print("💾 STEP 2: Importing ALL data to Local SQLite...")
print("-" * 80)

db_path = os.path.join(os.path.dirname(__file__), 'cyber_intel.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"✅ Connected to: {db_path}\n")

# Helper function to safely insert
def safe_insert(table_name, columns, values_list):
    count = 0
    skipped = 0
    for values in values_list:
        try:
            placeholders = ','.join(['?' for _ in columns])
            sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(values.get(col) for col in columns))
            count += 1
        except Exception as e:
            skipped += 1
            # print(f"   ⚠️  Skipped {table_name} record: {e}")
    conn.commit()
    return count, skipped

# Import all tables
print("Importing tables...")

# 1. System Users
cols = ['id', 'email', 'username', 'password_hash', 'role', 'is_active', 'last_login', 'created_at', 'updated_at']
count, skipped = safe_insert('system_users', cols, all_data['system_users'])
print(f"   ✅ System Users: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 2. Sources
cols = ['id', 'platform', 'source_handle', 'source_name', 'source_type', 'description', 'is_active', 
        'scraping_enabled', 'follower_count', 'last_scraped_at', 'created_at', 'updated_at']
count, skipped = safe_insert('sources', cols, all_data['sources'])
print(f"   ✅ Sources: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 3. Keywords
cols = ['id', 'keyword', 'category', 'severity', 'is_regex', 'is_active', 'created_at', 'updated_at']
count, skipped = safe_insert('keywords', cols, all_data['keywords'])
print(f"   ✅ Keywords: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 4. Cases
cols = ['id', 'case_number', 'title', 'description', 'status', 'priority', 'created_by_id', 
        'assigned_to_id', 'owner_id', 'created_at', 'updated_at']
count, skipped = safe_insert('cases', cols, all_data['cases'])
print(f"   ✅ Cases: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 5. Platform Users
cols = ['id', 'source_id', 'platform_user_id', 'username', 'full_name', 'bio', 'is_flagged', 
        'created_at', 'updated_at']
count, skipped = safe_insert('users', cols, all_data['users'])
print(f"   ✅ Platform Users: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 6. Content
cols = ['id', 'source_id', 'text', 'content_type', 'url', 'media_urls', 'posted_at', 'author', 
        'is_flagged', 'risk_level', 'suspicion_score', 'analysis_result', 'metadata', 
        'created_by_id', 'created_at', 'updated_at']
count, skipped = safe_insert('content', cols, all_data['content'])
print(f"   ✅ Content: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 7. Detections
cols = ['id', 'keyword_id', 'content_id', 'source_id', 'detected_text', 'context', 
        'severity', 'detected_by_id', 'created_at']
count, skipped = safe_insert('detections', cols, all_data['detections'])
print(f"   ✅ Detections: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 8. Identifiers
cols = ['id', 'identifier_type', 'value', 'source', 'confidence_score', 'metadata', 
        'created_at', 'updated_at']
count, skipped = safe_insert('identifiers', cols, all_data['identifiers'])
print(f"   ✅ Identifiers: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 9. OSINT Results
cols = ['id', 'user_id', 'query', 'result_type', 'data', 'confidence_score', 
        'created_by_id', 'created_at']
count, skipped = safe_insert('osint_results', cols, all_data['osint_results'])
print(f"   ✅ OSINT Results: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 10. Case Requests
cols = ['id', 'requested_by_id', 'assigned_to_id', 'title', 'description', 'priority', 
        'status', 'created_at', 'updated_at']
count, skipped = safe_insert('case_requests', cols, all_data['case_requests'])
print(f"   ✅ Case Requests: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 11. Active Cases
cols = ['id', 'system_user_id', 'case_id', 'created_at', 'updated_at']
count, skipped = safe_insert('active_cases', cols, all_data['active_cases'])
print(f"   ✅ Active Cases: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 12. User Case Links
cols = ['id', 'user_id', 'case_id', 'role', 'created_at', 'updated_at']
count, skipped = safe_insert('user_case_links', cols, all_data['user_case_links'])
print(f"   ✅ User-Case Links: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 13. OSINT Identifier Links
cols = ['id', 'osint_result_id', 'identifier_id', 'created_at']
count, skipped = safe_insert('osint_identifier_links', cols, all_data['osint_identifier_links'])
print(f"   ✅ OSINT-Identifier Links: {count} imported{f', {skipped} skipped' if skipped else ''}")

# 14. Case Content Links
cols = ['id', 'case_id', 'content_id', 'created_at', 'updated_at']
count, skipped = safe_insert('case_content_links', cols, all_data['case_content_links'])
print(f"   ✅ Case-Content Links: {count} imported{f', {skipped} skipped' if skipped else ''}")

conn.close()

print("\n" + "=" * 80)
print("✅ COMPLETE SYNC FINISHED!")
print("=" * 80)
print(f"\n📊 Summary:")
print(f"   • System Users: {len(all_data['system_users'])}")
print(f"   • Sources: {len(all_data['sources'])}")
print(f"   • Keywords: {len(all_data['keywords'])}")
print(f"   • Cases: {len(all_data['cases'])}")
print(f"   • Platform Users: {len(all_data['users'])}")
print(f"   • Content: {len(all_data['content'])}")
print(f"   • Detections: {len(all_data['detections'])}")
print(f"   • Identifiers: {len(all_data['identifiers'])}")
print(f"   • OSINT Results: {len(all_data['osint_results'])}")
print(f"   • Case Requests: {len(all_data['case_requests'])}")
print(f"   • Active Cases: {len(all_data['active_cases'])}")
print(f"   • User-Case Links: {len(all_data['user_case_links'])}")
print(f"   • OSINT-Identifier Links: {len(all_data['osint_identifier_links'])}")
print(f"   • Case-Content Links: {len(all_data['case_content_links'])}")
print(f"\n   TOTAL: {total_records} records")
print(f"\n💾 Local database: {db_path}")
print(f"🌐 Railway database: Unchanged\n")
print("=" * 80)

