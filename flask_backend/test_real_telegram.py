#!/usr/bin/env python3
"""
Test real Telegram scraping with existing credentials
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_real_telegram():
    """Test real Telegram scraping"""
    print("Testing Real Telegram Scraping")
    print("=" * 40)
    print()
    
    try:
        from services.telegram_scraper import TelegramScraper
        
        # Create scraper
        scraper = TelegramScraper()
        
        # Check if we have credentials
        api_id = os.environ.get('TELEGRAM_API_ID')
        api_hash = os.environ.get('TELEGRAM_API_HASH')
        phone = os.environ.get('TELEGRAM_PHONE_NUMBER')
        
        print(f"API ID: {api_id}")
        print(f"Phone: {phone}")
        print()
        
        # Try to initialize (this will use existing session if available)
        print("Initializing Telegram client...")
        success = await scraper.initialize()
        
        if success:
            print("SUCCESS: Telegram client connected!")
            print()
            
            # Test scraping a simple channel
            print("Testing channel scraping...")
            result = await scraper.scrape_channel(
                channel_id="@durov",
                max_messages=3,
                keywords=["telegram", "security", "privacy"]
            )
            
            print(f"Channel: {result.get('channel_title', 'Unknown')}")
            print(f"Messages scraped: {result.get('scraped_count', 0)}")
            print(f"Keyword matches: {result.get('keyword_matches', 0)}")
            print(f"Data mode: {result.get('data_mode', 'unknown')}")
            print()
            
            if result.get('messages'):
                print("Sample messages:")
                for i, msg in enumerate(result['messages'][:2], 1):
                    text = msg.get('text', '')[:80] + "..." if len(msg.get('text', '')) > 80 else msg.get('text', '')
                    print(f"  {i}. {text}")
                    if msg.get('matched_keywords'):
                        print(f"     Keywords: {msg['matched_keywords']}")
                print()
            
            print("RESULT: Real Telegram scraping is working!")
            return True
        else:
            print("FAILED: Could not connect to Telegram")
            print("This might be due to:")
            print("1. Missing verification code")
            print("2. Network issues")
            print("3. API restrictions")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    finally:
        try:
            if 'scraper' in locals():
                await scraper.close()
        except:
            pass

if __name__ == "__main__":
    print("Starting Real Telegram Test...")
    success = asyncio.run(test_real_telegram())
    if success:
        print("\nSUCCESS: Real Telegram scraping is working!")
    else:
        print("\nFAILED: Real Telegram scraping is not working")
        print("You may need to complete phone verification first")



