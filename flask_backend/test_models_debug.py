"""
Debug script to test database models and identify potential issues
"""
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_model_imports():
    """Test if all required models can be imported"""
    print("Testing model imports...")
    print("=" * 30)
    
    try:
        from models.case import Case
        print("✅ Case model imported successfully")
    except Exception as e:
        print(f"❌ Case model import failed: {str(e)}")
        return False
    
    try:
        from models.user import SystemUser, User
        print("✅ User models imported successfully")
    except Exception as e:
        print(f"❌ User models import failed: {str(e)}")
        return False
    
    try:
        from models.active_case import ActiveCase
        print("✅ ActiveCase model imported successfully")
    except Exception as e:
        print(f"❌ ActiveCase model import failed: {str(e)}")
        return False
    
    try:
        from models.content import Content
        print("✅ Content model imported successfully")
    except Exception as e:
        print(f"❌ Content model import failed: {str(e)}")
        return False
    
    try:
        from models.osint_result import OSINTResult
        print("✅ OSINTResult model imported successfully")
    except Exception as e:
        print(f"❌ OSINTResult model import failed: {str(e)}")
        return False
    
    try:
        from models.case_content_link import CaseContentLink
        print("✅ CaseContentLink model imported successfully")
    except Exception as e:
        print(f"❌ CaseContentLink model import failed: {str(e)}")
        return False
    
    try:
        from models.user_case_link import UserCaseLink
        print("✅ UserCaseLink model imported successfully")
    except Exception as e:
        print(f"❌ UserCaseLink model import failed: {str(e)}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and basic queries"""
    print("\nTesting database connection...")
    print("=" * 35)
    
    try:
        from app import app
        from extensions import db
        
        with app.app_context():
            # Test basic database connection
            result = db.session.execute("SELECT 1").fetchone()
            print("✅ Database connection successful")
            
            # Test Case model query
            try:
                cases = db.session.query(Case).limit(1).all()
                print(f"✅ Case model query successful (found {len(cases)} cases)")
            except Exception as e:
                print(f"❌ Case model query failed: {str(e)}")
                return False
            
            # Test SystemUser model query
            try:
                users = db.session.query(SystemUser).limit(1).all()
                print(f"✅ SystemUser model query successful (found {len(users)} users)")
            except Exception as e:
                print(f"❌ SystemUser model query failed: {str(e)}")
                return False
            
            # Test ActiveCase model query
            try:
                active_cases = db.session.query(ActiveCase).limit(1).all()
                print(f"✅ ActiveCase model query successful (found {len(active_cases)} active cases)")
            except Exception as e:
                print(f"❌ ActiveCase model query failed: {str(e)}")
                return False
            
            # Test Content model query
            try:
                content = db.session.query(Content).limit(1).all()
                print(f"✅ Content model query successful (found {len(content)} content items)")
            except Exception as e:
                print(f"❌ Content model query failed: {str(e)}")
                return False
            
            # Test OSINTResult model query
            try:
                osint_results = db.session.query(OSINTResult).limit(1).all()
                print(f"✅ OSINTResult model query successful (found {len(osint_results)} OSINT results)")
            except Exception as e:
                print(f"❌ OSINTResult model query failed: {str(e)}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_preview_logic():
    """Test the preview logic without the Flask context"""
    print("\nTesting preview logic...")
    print("=" * 25)
    
    try:
        from app import app
        from extensions import db
        from models.case import Case
        from models.user import SystemUser
        from models.active_case import ActiveCase
        from models.content import Content
        from models.osint_result import OSINTResult
        from models.case_content_link import CaseContentLink
        
        with app.app_context():
            # Test the preview logic step by step
            print("1. Testing user query...")
            users = db.session.query(SystemUser).limit(1).all()
            if not users:
                print("❌ No users found in database")
                return False
            print(f"✅ Found {len(users)} users")
            
            print("2. Testing active case query...")
            active_cases = db.session.query(ActiveCase).limit(1).all()
            print(f"✅ Found {len(active_cases)} active cases")
            
            if active_cases:
                active = active_cases[0]
                case_id = active.case_id
                print(f"3. Testing case query for ID {case_id}...")
                
                case = db.session.query(Case).get(case_id)
                if not case:
                    print(f"❌ Case with ID {case_id} not found")
                    return False
                print(f"✅ Found case: {case.title}")
                
                print("4. Testing content links query...")
                content_links = db.session.query(CaseContentLink).filter_by(case_id=case_id).all()
                print(f"✅ Found {len(content_links)} content links")
                
                print("5. Testing content query...")
                if content_links:
                    content_ids = [link.content_id for link in content_links]
                    content_items = db.session.query(Content).filter(Content.id.in_(content_ids)).all()
                    print(f"✅ Found {len(content_items)} content items")
                else:
                    content_items = []
                    print("✅ No content items (empty list)")
                
                print("6. Testing OSINT results query...")
                osint_results = db.session.query(OSINTResult).filter_by(case_id=case_id).all()
                print(f"✅ Found {len(osint_results)} OSINT results")
                
                print("7. Testing preview data creation...")
                preview_data = {
                    'case': {
                        'id': case.id,
                        'title': case.title,
                        'case_number': case.case_number,
                        'status': case.status.value if case.status else None,
                        'priority': case.priority.value if case.priority else None,
                        'created_at': case.created_at.isoformat(),
                        'updated_at': case.updated_at.isoformat()
                    },
                    'statistics': {
                        'platforms_analyzed': 'None',
                        'flagged_users': 0,
                        'flagged_posts': len(content_items),
                        'osint_results': len(osint_results)
                    }
                }
                print("✅ Preview data created successfully")
                print(f"Preview data: {preview_data}")
                
                return True
            else:
                print("✅ No active cases found (this is normal)")
                return True
                
    except Exception as e:
        print(f"❌ Preview logic test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Debugging Database Models and Preview Logic")
    print("=" * 50)
    
    # Test model imports
    imports_ok = test_model_imports()
    
    if imports_ok:
        # Test database connection
        db_ok = test_database_connection()
        
        if db_ok:
            # Test preview logic
            preview_ok = test_preview_logic()
            
            print("\n" + "=" * 50)
            print("SUMMARY:")
            print(f"Model Imports: {'✅ SUCCESS' if imports_ok else '❌ FAILED'}")
            print(f"Database Connection: {'✅ SUCCESS' if db_ok else '❌ FAILED'}")
            print(f"Preview Logic: {'✅ SUCCESS' if preview_ok else '❌ FAILED'}")
            
            if not preview_ok:
                print("\n🔍 The issue is likely in the preview logic or database queries")
            elif not db_ok:
                print("\n🔍 The issue is likely with database connection or model queries")
            elif not imports_ok:
                print("\n🔍 The issue is likely with model imports")
            else:
                print("\n✅ All tests passed - the issue might be elsewhere")
        else:
            print("\n❌ Database connection failed - check database setup")
    else:
        print("\n❌ Model imports failed - check model definitions")
