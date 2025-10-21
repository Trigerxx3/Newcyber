"""
Seed admin user in production database
"""
import os
import sys

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://postgres:GWexlGlzyawuhOotbpSviKOuraoLYmFb@maglev.proxy.rlwy.net:26614/railway'
os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production-2024'
os.environ['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production-2024'
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from extensions import db
from models.user import SystemUser, SystemUserRole

# Create app
app = create_app('production')

with app.app_context():
    email = "admin@cyber.com"
    print(f"🔍 Checking for admin user: {email}")
    
    user = SystemUser.get_by_email(email)
    
    if not user:
        print(f"👤 Creating new admin user...")
        user = SystemUser(
            email=email,
            username="admin",
            role=SystemUserRole.ADMIN,
            password_hash=""
        )
        user.set_password("admin123456")
        db.session.add(user)
        db.session.commit()
        print(f"✅ Admin user created successfully!")
    else:
        print(f"👤 Admin user exists, resetting password...")
        user.set_password("admin123456")
        db.session.commit()
        print(f"✅ Admin password reset successfully!")
    
    print(f"\n🎉 Admin credentials:")
    print(f"   Email: admin@cyber.com")
    print(f"   Password: admin123456")
    print(f"\n⚠️  Please change this password after your first login!")

