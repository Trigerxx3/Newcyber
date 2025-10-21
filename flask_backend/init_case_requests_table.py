"""
Initialize case_requests table if it doesn't exist
Run this script if you're getting database errors for case requests
"""
from app import create_app
from extensions import db
from models.case_request import CaseRequest

def init_case_requests_table():
    """Create case_requests table if it doesn't exist"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if table exists by querying it
            existing = CaseRequest.query.first()
            print(f"✓ case_requests table exists (found {CaseRequest.query.count()} requests)")
        except Exception as e:
            print(f"⚠ case_requests table doesn't exist or has issues: {e}")
            print("Creating table...")
            try:
                db.create_all()
                print("✓ Tables created successfully")
            except Exception as create_error:
                print(f"✗ Failed to create tables: {create_error}")
                return False
        
        return True

if __name__ == '__main__':
    print("Initializing case_requests table...")
    success = init_case_requests_table()
    if success:
        print("\n✓ Database initialization complete!")
    else:
        print("\n✗ Database initialization failed. Please check the error messages above.")

