#!/usr/bin/env python3
"""
Environment Setup Script
Helps configure database and environment variables
"""

import os
import shutil

def create_env_file():
    """Create .env file from template"""
    template_file = 'env_template.txt'
    env_file = '.env'
    
    if os.path.exists(env_file):
        overwrite = input(f"{env_file} already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Cancelled.")
            return
    
    try:
        shutil.copy2(template_file, env_file)
        print(f"✅ {env_file} created from {template_file}")
        print("\n📝 Next steps:")
        print(f"1. Edit {env_file} to configure your settings")
        print("2. For PostgreSQL, uncomment and set DATABASE_URL")
        print("3. Change SECRET_KEY and JWT_SECRET_KEY for production")
    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")

def show_database_options():
    """Show database configuration options"""
    print("\n🗄️  Database Configuration Options:")
    print("=" * 50)
    
    print("\n1️⃣  SQLite (Development - Default)")
    print("   • File-based database")
    print("   • No installation required")
    print("   • Automatic setup")
    print("   • Location: flask_backend/local.db")
    
    print("\n2️⃣  PostgreSQL (Production)")
    print("   • Set DATABASE_URL in .env file")
    print("   • Format: postgresql://user:password@host:port/database")
    print("   • Example: postgresql://postgres:password@localhost:5432/cyber_db")
    
    print("\n3️⃣  Cloud PostgreSQL")
    print("   • Railway: Automatic DATABASE_URL")
    print("   • Heroku: Automatic DATABASE_URL")
    print("   • Supabase: Copy connection string")
    print("   • AWS RDS: Use connection details")

def setup_postgresql():
    """Interactive PostgreSQL setup"""
    print("\n🐘 PostgreSQL Setup:")
    print("=" * 30)
    
    host = input("Host (localhost): ").strip() or "localhost"
    port = input("Port (5432): ").strip() or "5432"
    database = input("Database name (cyber_db): ").strip() or "cyber_db"
    username = input("Username (postgres): ").strip() or "postgres"
    password = input("Password: ").strip()
    
    if not password:
        print("❌ Password is required!")
        return
    
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    print(f"\n📝 Add this to your .env file:")
    print(f"DATABASE_URL={database_url}")
    
    # Test connection
    test = input("\nTest connection? (y/N): ").strip().lower()
    if test == 'y':
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ Connection successful!")
        except ImportError:
            print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        except Exception as e:
            print(f"❌ Connection failed: {e}")

def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing requirements...")
    try:
        os.system("pip install -r requirements.txt")
        print("✅ Requirements installed!")
    except Exception as e:
        print(f"❌ Error installing requirements: {e}")

def check_setup():
    """Check current setup status"""
    print("\n🔍 Setup Status Check:")
    print("=" * 30)
    
    # Check .env file
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("❌ .env file missing")
    
    # Check database
    if os.path.exists('local.db'):
        size = os.path.getsize('local.db')
        print(f"✅ SQLite database exists ({size} bytes)")
    else:
        print("❌ SQLite database missing")
    
    # Check migrations
    if os.path.exists('migrations'):
        print("✅ Migrations directory exists")
    else:
        print("❌ Migrations directory missing")
    
    # Check requirements
    try:
        import flask_sqlalchemy
        import flask_migrate
        import flask_jwt_extended
        print("✅ Core requirements installed")
    except ImportError as e:
        print(f"❌ Missing requirement: {e}")

def main_menu():
    """Main setup menu"""
    while True:
        print("\n" + "=" * 60)
        print("⚙️  CYBER INTELLIGENCE PLATFORM - SETUP MANAGER")
        print("=" * 60)
        print("1. 📄 Create .env file from template")
        print("2. 🗄️  Show database options")
        print("3. 🐘 Setup PostgreSQL connection")
        print("4. 📦 Install requirements")
        print("5. 🔍 Check setup status")
        print("6. 🚪 Exit")
        print("=" * 60)
        
        choice = input("Select option (1-6): ").strip()
        
        if choice == '1':
            create_env_file()
        elif choice == '2':
            show_database_options()
        elif choice == '3':
            setup_postgresql()
        elif choice == '4':
            install_requirements()
        elif choice == '5':
            check_setup()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == '__main__':
    main_menu()