"""
Create case_activities table if it doesn't exist
This is a fallback script to ensure the table exists
"""
from extensions import db
from models.case_activity import CaseActivity
import logging

logger = logging.getLogger(__name__)

def create_case_activities_table():
    """Create the case_activities table if it doesn't exist"""
    try:
        # Check if table exists
        inspector = db.inspect(db.engine)
        if 'case_activities' not in inspector.get_table_names():
            logger.info("Creating case_activities table...")
            CaseActivity.__table__.create(db.engine)
            logger.info("case_activities table created successfully")
        else:
            logger.info("case_activities table already exists")
        return True
    except Exception as e:
        logger.error(f"Error creating case_activities table: {str(e)}")
        return False

if __name__ == "__main__":
    from app import create_app
    app = create_app()
    with app.app_context():
        create_case_activities_table()
