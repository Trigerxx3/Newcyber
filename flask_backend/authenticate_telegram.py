#!/usr/bin/env python3
"""
Telegram authentication script
This script handles the initial authentication process
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def authenticate_telegram():
    """Authenticate with Telegram using phone number"""
    try:
        from services.telegram_scraper import TelegramScraper
        
        print("Telegram Authentication")
        print("=" * 30)
        print()
        
        # Create new scraper instance
        scraper = TelegramScraper()
        
        # Check credentials
        api_id = os.environ.get('TELEGRAM_API_ID')
        api_hash = os.environ.get('TELEGRAM_API_HASH')
        phone = os.environ.get('TELEGRAM_PHONE_NUMBER')
        
        if not api_id or not api_hash or not phone:
            print("ERROR: Missing Telegram credentials!")
            print("Make sure you have set:")
            print("- TELEGRAM_API_ID")
            print("- TELEGRAM_API_HASH") 
            print("- TELEGRAM_PHONE_NUMBER")
            return False
        
        print(f"Phone: {phone}")
        print(f"API ID: {api_id}")
        print()
        
        # Initialize client
        print("Connecting to Telegram...")
        success = await scraper.initialize()
        
        if success:
            print("✅ Authentication successful!")
            print("🚀 Real Telegram scraping is now enabled!")
            print()
            print("You can now use real Telegram scraping with keyword detection.")
            return True
        else:
            print("❌ Authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Close connection
        try:
            if 'scraper' in locals():
                await scraper.close()
        except:
            pass

if __name__ == "__main__":
    print("Starting Telegram Authentication...")
    success = asyncio.run(authenticate_telegram())
    if success:
        print("\n✅ Authentication completed successfully!")
        print("You can now run: python test_telegram_scraping.py")
    else:
        print("\n❌ Authentication failed!")
        print("Please check your credentials and try again.")



