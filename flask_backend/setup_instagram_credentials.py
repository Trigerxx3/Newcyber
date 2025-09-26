#!/usr/bin/env python3
"""
Instagram Credentials Setup Helper
This script helps you securely configure Instagram credentials for real scraping.
"""
import os
import getpass
from dotenv import load_dotenv, set_key

def setup_instagram_credentials():
    """Interactive setup for Instagram credentials"""
    print("🔐 Instagram Scraping Setup")
    print("="*50)
    print()
    print("⚠️  IMPORTANT SECURITY WARNING:")
    print("   • NEVER use your personal Instagram account for scraping!")
    print("   • Create a dedicated Instagram account specifically for this purpose")
    print("   • Instagram may restrict or ban accounts used for automated scraping")
    print("   • Use throwaway email/phone for the dedicated account")
    print()
    
    # Get user confirmation
    confirm = input("Do you understand these risks and want to continue? (yes/no): ").lower().strip()
    if confirm not in ['yes', 'y']:
        print("Setup cancelled for your safety.")
        return False
    
    print()
    print("📝 Enter your DEDICATED Instagram account credentials:")
    print("   (These will be saved securely in your .env file)")
    print()
    
    # Get credentials
    username = input("Instagram Username (dedicated account): ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return False
    
    password = getpass.getpass("Instagram Password (dedicated account): ").strip()
    if not password:
        print("❌ Password cannot be empty!")
        return False
    
    # Validate inputs
    if username == 'your_instagram_username' or password == 'your_instagram_password':
        print("❌ Please use real credentials, not placeholder values!")
        return False
    
    # Update .env file
    env_file = '.env'
    if not os.path.exists(env_file):
        print(f"❌ .env file not found at {env_file}")
        return False
    
    try:
        # Update credentials in .env file
        set_key(env_file, 'INSTAGRAM_USERNAME', username)
        set_key(env_file, 'INSTAGRAM_PASSWORD', password)
        
        print()
        print("✅ Instagram credentials saved successfully!")
        print()
        print("🚀 Next steps:")
        print("   1. Restart your Flask server (python run.py)")
        print("   2. Test the connection with: GET /api/instagram/status")
        print("   3. Try scraping a public profile: GET /api/instagram/profile/username")
        print()
        print("💡 Tips for success:")
        print("   • Let your new Instagram account age for a few days before heavy use")
        print("   • Add a profile picture and bio to make it look legitimate")
        print("   • Follow a few accounts and post occasionally")
        print("   • Start with small scraping requests and gradually increase")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save credentials: {e}")
        return False

def check_current_setup():
    """Check current Instagram configuration"""
    load_dotenv()
    
    username = os.getenv('INSTAGRAM_USERNAME', '')
    password = os.getenv('INSTAGRAM_PASSWORD', '')
    
    print("🔍 Current Instagram Configuration:")
    print("="*40)
    
    if username and username != 'your_instagram_username':
        print(f"✅ Username: {username}")
    else:
        print("❌ Username: Not configured")
    
    if password and password != 'your_instagram_password':
        print("✅ Password: Configured")
    else:
        print("❌ Password: Not configured")
    
    print()
    
    if username and password and username != 'your_instagram_username' and password != 'your_instagram_password':
        print("🎉 Instagram credentials are configured!")
        print("   Restart your Flask server to activate real scraping.")
    else:
        print("⚠️  Instagram credentials need to be configured for real scraping.")
    
    return username and password and username != 'your_instagram_username' and password != 'your_instagram_password'

def main():
    """Main function"""
    print("Instagram Scraping Configuration Tool")
    print("="*50)
    print()
    
    # Check current setup
    if check_current_setup():
        print()
        choice = input("Credentials are already configured. Update them? (yes/no): ").lower().strip()
        if choice not in ['yes', 'y']:
            print("Configuration unchanged.")
            return
    
    print()
    setup_instagram_credentials()

if __name__ == '__main__':
    main()