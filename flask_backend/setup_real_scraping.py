#!/usr/bin/env python3
"""
Interactive Real Scraping Setup
This script guides you through setting up real API credentials for scraping
"""

import os
import shutil
from dotenv import load_dotenv, set_key

def print_header():
    """Print setup header"""
    print("🚀 Real Data Scraping Setup")
    print("=" * 60)
    print("This setup will help you configure real API credentials")
    print("for Telegram, Instagram, and WhatsApp scraping.")
    print("=" * 60)

def setup_env_file():
    """Setup .env file"""
    env_path = '.env'
    template_path = 'env_template.txt'
    
    if not os.path.exists(env_path):
        if os.path.exists(template_path):
            shutil.copy(template_path, env_path)
            print(f"✅ Created .env file from template")
        else:
            print("❌ env_template.txt not found!")
            return False
    else:
        print(f"✅ .env file already exists")
    
    return True

def get_user_input(prompt, default=None, required=True):
    """Get user input with validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                return default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        
        if required:
            print("❌ This field is required. Please enter a value.")

def setup_telegram():
    """Setup Telegram API credentials"""
    print("\n📱 Telegram API Setup")
    print("-" * 30)
    print("To get Telegram API credentials:")
    print("1. Go to https://my.telegram.org/auth")
    print("2. Login with your phone number")
    print("3. Go to 'API Development Tools'")
    print("4. Create a new application")
    print("5. Copy the api_id and api_hash")
    print()
    
    setup_telegram = get_user_input("Do you want to setup Telegram API? (y/n)", "n", False).lower()
    
    if setup_telegram in ['y', 'yes']:
        api_id = get_user_input("Enter your Telegram API ID")
        api_hash = get_user_input("Enter your Telegram API Hash")
        phone = get_user_input("Enter your phone number (with country code, e.g., +1234567890)")
        
        # Update .env file
        set_key('.env', 'TELEGRAM_API_ID', api_id)
        set_key('.env', 'TELEGRAM_API_HASH', api_hash)
        set_key('.env', 'TELEGRAM_PHONE_NUMBER', phone)
        
        print("✅ Telegram credentials saved to .env")
        return True
    else:
        print("⏭️ Skipping Telegram setup")
        return False

def setup_instagram():
    """Setup Instagram API credentials"""
    print("\n📸 Instagram API Setup")
    print("-" * 30)
    print("Instagram Setup Options:")
    print("1. Account Login (Simpler, but more restrictive)")
    print("2. Instagram Basic Display API (Recommended, more stable)")
    print("3. Skip Instagram setup")
    print()
    
    choice = get_user_input("Choose option (1/2/3)", "3")
    
    if choice == "1":
        print("\n🔶 Account Login Setup")
        print("⚠️ IMPORTANT: Use a dedicated account, NOT your personal one!")
        print("Instagram may restrict accounts that scrape heavily.")
        print()
        
        username = get_user_input("Enter Instagram username (dedicated account)")
        password = get_user_input("Enter Instagram password")
        
        set_key('.env', 'INSTAGRAM_USERNAME', username)
        set_key('.env', 'INSTAGRAM_PASSWORD', password)
        
        print("✅ Instagram account credentials saved to .env")
        return True
        
    elif choice == "2":
        print("\n🔶 Instagram Basic Display API Setup")
        print("To get API credentials:")
        print("1. Go to https://developers.facebook.com/")
        print("2. Create a new app")
        print("3. Add 'Instagram Basic Display API'")
        print("4. Get your Client ID, Client Secret, and Access Token")
        print()
        
        client_id = get_user_input("Enter Instagram Client ID")
        client_secret = get_user_input("Enter Instagram Client Secret")
        access_token = get_user_input("Enter Instagram Access Token")
        
        set_key('.env', 'INSTAGRAM_CLIENT_ID', client_id)
        set_key('.env', 'INSTAGRAM_CLIENT_SECRET', client_secret)
        set_key('.env', 'INSTAGRAM_ACCESS_TOKEN', access_token)
        
        print("✅ Instagram API credentials saved to .env")
        return True
        
    else:
        print("⏭️ Skipping Instagram setup")
        return False

def setup_whatsapp():
    """Setup WhatsApp Business API credentials"""
    print("\n💬 WhatsApp Business API Setup")
    print("-" * 30)
    print("⚠️ Note: WhatsApp requires Business API setup through Facebook")
    print("This is more complex and requires business verification.")
    print()
    print("To get WhatsApp Business API:")
    print("1. Go to https://developers.facebook.com/")
    print("2. Create a WhatsApp Business app")
    print("3. Complete business verification")
    print("4. Get your Business Account ID and Access Token")
    print()
    
    setup_whatsapp = get_user_input("Do you want to setup WhatsApp Business API? (y/n)", "n", False).lower()
    
    if setup_whatsapp in ['y', 'yes']:
        business_id = get_user_input("Enter WhatsApp Business Account ID")
        access_token = get_user_input("Enter WhatsApp Access Token")
        phone_id = get_user_input("Enter WhatsApp Phone Number ID")
        verify_token = get_user_input("Enter Webhook Verify Token", "cyber_intel_webhook_2024")
        
        set_key('.env', 'WHATSAPP_BUSINESS_ACCOUNT_ID', business_id)
        set_key('.env', 'WHATSAPP_ACCESS_TOKEN', access_token)
        set_key('.env', 'WHATSAPP_PHONE_NUMBER_ID', phone_id)
        set_key('.env', 'WHATSAPP_WEBHOOK_VERIFY_TOKEN', verify_token)
        
        print("✅ WhatsApp Business API credentials saved to .env")
        return True
    else:
        print("⏭️ Skipping WhatsApp setup")
        return False

def test_credentials():
    """Test the configured credentials"""
    print("\n🧪 Testing API Credentials")
    print("-" * 30)
    
    test_apis = get_user_input("Do you want to test your API credentials? (y/n)", "y", False).lower()
    
    if test_apis in ['y', 'yes']:
        print("\n🔄 Testing Telegram...")
        try:
            os.system("python telegram_setup_helper.py")
        except:
            print("⚠️ Could not run Telegram test")
        
        print("\n🔄 Testing Instagram...")
        try:
            os.system("python instagram_setup_helper.py")
        except:
            print("⚠️ Could not run Instagram test")
        
        return True
    else:
        print("⏭️ Skipping API tests")
        return False

def show_next_steps():
    """Show next steps after setup"""
    print("\n🎉 Setup Complete!")
    print("=" * 60)
    print("✅ Your .env file has been configured with API credentials")
    print()
    print("🚀 Next Steps:")
    print("1. Start the Flask backend:")
    print("   python app.py")
    print()
    print("2. Start the Next.js frontend:")
    print("   cd ../cyber")
    print("   npm run dev")
    print()
    print("3. Access the scraping dashboard:")
    print("   http://localhost:3000/admin/scraping")
    print()
    print("4. Test the scraping health check:")
    print("   http://localhost:5000/api/scraping/health-check")
    print()
    print("📚 For detailed setup instructions, see:")
    print("   - SCRAPING_SETUP.md")
    print("   - telegram_setup_helper.py")
    print("   - instagram_setup_helper.py")
    print()
    print("⚠️ Important Reminders:")
    print("- Only scrape public content")
    print("- Respect platform rate limits")
    print("- Follow Terms of Service")
    print("- Use dedicated accounts for testing")
    print("=" * 60)

def main():
    """Main setup function"""
    try:
        print_header()
        
        # Setup .env file
        if not setup_env_file():
            return
        
        # Setup each platform
        telegram_setup = setup_telegram()
        instagram_setup = setup_instagram()
        whatsapp_setup = setup_whatsapp()
        
        # Test credentials if any were set up
        if telegram_setup or instagram_setup or whatsapp_setup:
            test_credentials()
        
        # Show next steps
        show_next_steps()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Setup cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("Please check the error and try again")

if __name__ == '__main__':
    main()
