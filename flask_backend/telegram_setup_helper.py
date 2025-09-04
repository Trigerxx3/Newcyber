#!/usr/bin/env python3
"""
Telegram API Setup Helper
This script helps you configure Telegram API credentials and test the connection
"""

import os
import asyncio
from dotenv import load_dotenv

async def setup_telegram():
    """Setup and test Telegram API connection"""
    print("🔧 Telegram API Setup Helper")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    phone = os.environ.get('TELEGRAM_PHONE_NUMBER')
    
    if not api_id or not api_hash:
        print("❌ Missing Telegram API credentials!")
        print("\n📋 Please follow these steps:")
        print("1. Go to https://my.telegram.org/auth")
        print("2. Enter your phone number and verify")
        print("3. Go to 'API Development Tools'")
        print("4. Create a new application")
        print("5. Copy the api_id and api_hash")
        print("\n📝 Then update your .env file with:")
        print("TELEGRAM_API_ID=your_api_id_here")
        print("TELEGRAM_API_HASH=your_api_hash_here")
        print("TELEGRAM_PHONE_NUMBER=+1234567890")
        return False
    
    try:
        # Try to import and initialize Telegram client
        from telethon import TelegramClient
        
        print(f"✅ Found API credentials")
        print(f"📱 API ID: {api_id}")
        print(f"🔑 API Hash: {api_hash[:8]}...")
        print(f"📞 Phone: {phone}")
        
        # Create client
        client = TelegramClient('telegram_session', int(api_id), api_hash)
        
        print("\n🔄 Testing Telegram connection...")
        
        # Start client and login
        await client.start(phone=phone)
        
        if await client.is_user_authorized():
            print("✅ Telegram API connection successful!")
            
            # Test getting some info
            me = await client.get_me()
            print(f"👤 Logged in as: {me.first_name} {me.last_name or ''}")
            print(f"📞 Phone: {me.phone}")
            
            # Test getting public channels
            print("\n🔍 Testing public channel access...")
            try:
                # Try to get info about Telegram's official channel
                telegram_channel = await client.get_entity('@telegram')
                print(f"✅ Can access public channels")
                print(f"📺 Test channel: {telegram_channel.title}")
                print(f"👥 Subscribers: {telegram_channel.participants_count}")
                
            except Exception as channel_error:
                print(f"⚠️ Channel access test failed: {channel_error}")
            
            await client.disconnect()
            return True
        else:
            print("❌ Telegram authorization failed!")
            print("💡 Make sure your phone number is correct and try again")
            await client.disconnect()
            return False
            
    except ImportError:
        print("❌ Telethon not installed!")
        print("Run: pip install telethon")
        return False
    except Exception as e:
        print(f"❌ Telegram setup failed: {e}")
        print("\n💡 Common issues:")
        print("- Invalid API credentials")
        print("- Phone number not verified")
        print("- Network connectivity issues")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Telegram API setup...")
    
    try:
        result = asyncio.run(setup_telegram())
        if result:
            print("\n🎉 Telegram API setup completed successfully!")
            print("✅ You can now use real Telegram scraping")
        else:
            print("\n❌ Telegram API setup failed")
            print("💡 Please check the instructions above and try again")
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == '__main__':
    main()
