#!/usr/bin/env python3
"""
Create a test analyst user for testing user isolation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from models.user import SystemUser, SystemUserRole

def create_test_analyst():
    app = create_app()
    with app.app_context():
        # Check if test analyst already exists
        existing_analyst = SystemUser.query.filter_by(username='test_analyst').first()
        if existing_analyst:
            print(f"✅ Test analyst already exists: {existing_analyst.username} (ID: {existing_analyst.id})")
            return existing_analyst.id
        
        # Create test analyst
        analyst = SystemUser(
            username='test_analyst',
            email='analyst@test.com',
            role=SystemUserRole.ANALYST,
            is_active=True
        )
        analyst.set_password('test123456')
        
        db.session.add(analyst)
        db.session.commit()
        
        print(f"✅ Created test analyst: {analyst.username} (ID: {analyst.id})")
        return analyst.id

if __name__ == '__main__':
    analyst_id = create_test_analyst()
    print(f"Test analyst ID: {analyst_id}")

