#!/usr/bin/env python3
"""
Instagram Scraping Demo Setup
This demonstrates how to set up real Instagram credentials safely.
"""
import os
from dotenv import load_dotenv, set_key

def demo_setup_guide():
    """Show exactly how to set up Instagram credentials"""
    print("🎯 How to Enable Real Instagram Scraping")
    print("="*50)
    print()
    
    print("📋 Step-by-Step Instructions:")
    print()
    
    print("1️⃣ CREATE A DEDICATED INSTAGRAM ACCOUNT")
    print("   • Go to instagram.com")
    print("   • Create a NEW account (NOT your personal one!)")
    print("   • Use a throwaway email like: scraper123@tempmail.com")
    print("   • Choose username like: cyberscraper2024")
    print("   • Use a strong password")
    print("   • Complete the profile with picture and bio")
    print()
    
    print("2️⃣ UPDATE YOUR .ENV FILE")
    print("   Open your .env file and replace these lines:")
    print("   ")
    print("   FROM:")
    print("   INSTAGRAM_USERNAME=your_instagram_username")
    print("   INSTAGRAM_PASSWORD=your_instagram_password")
    print("   ")
    print("   TO:")
    print("   INSTAGRAM_USERNAME=cyberscraper2024")  
    print("   INSTAGRAM_PASSWORD=your_actual_password")
    print()
    
    print("3️⃣ RESTART THE FLASK SERVER")
    print("   • Stop the current server (Ctrl+C)")
    print("   • Run: python run.py")
    print("   • The system will auto-detect real credentials")
    print()
    
    print("4️⃣ TEST REAL SCRAPING")
    print("   • Check status: GET /api/instagram/status")
    print("   • Should show: 'status': 'configured'")
    print("   • Try scraping: GET /api/instagram/profile/instagram")
    print("   • Should return real Instagram data!")
    print()
    
    print("⚡ INSTANT TEST (What You'll See):")
    print("   Mock Data Response:")
    print("   {")
    print('     "scraping_status": {')
    print('       "data_type": "mock",')
    print('       "message": "Using mock data - Instagram credentials not configured"')
    print("     }")
    print("   }")
    print()
    print("   Real Data Response:")
    print("   {")
    print('     "scraping_status": {')
    print('       "data_type": "real",')
    print('       "message": "Connected to Instagram API",')
    print('       "source": "Instagram API"')
    print("     },")
    print('     "posts": [/* Real Instagram posts */]')
    print("   }")
    print()
    
    print("🔒 SECURITY REMINDERS:")
    print("   • NEVER use your personal Instagram account")
    print("   • Keep scraping volumes reasonable")
    print("   • Let new accounts 'age' before heavy use")
    print("   • Monitor account for restrictions")
    print()
    
    print("🚀 ADVANCED TIPS:")
    print("   • Use residential proxies for better results")
    print("   • Rotate between multiple scraping accounts")
    print("   • Add random delays between requests")
    print("   • Scrape during Instagram's off-peak hours")

def show_current_status():
    """Show what happens with current mock setup"""
    print()
    print("📊 CURRENT STATUS (Mock Data Mode)")
    print("="*40)
    print()
    print("Right now, your Instagram scraping returns mock data like:")
    print()
    print("🔍 Profile Scraping:")
    print("   • Realistic-looking posts with random data")
    print("   • Sample captions and hashtags")
    print("   • Fake engagement metrics")
    print("   • Placeholder image URLs")
    print()
    print("✅ This is GOOD for:")
    print("   • Testing your frontend interface")
    print("   • Developing without Instagram restrictions")
    print("   • Demonstrating the app functionality")
    print()
    print("🎯 With Real Credentials:")
    print("   • Actual Instagram posts and captions")
    print("   • Real images, videos, and media")
    print("   • True engagement numbers")
    print("   • Current timestamps and real users")

def test_current_setup():
    """Test what the current setup returns"""
    load_dotenv()
    
    username = os.getenv('INSTAGRAM_USERNAME', '')
    password = os.getenv('INSTAGRAM_PASSWORD', '')
    
    print()
    print("🧪 TESTING CURRENT SETUP")
    print("="*30)
    
    is_configured = (username and password and 
                    username != 'your_instagram_username' and 
                    password != 'your_instagram_password')
    
    if is_configured:
        print(f"✅ Username: {username}")
        print("✅ Password: [CONFIGURED]")
        print()
        print("🎉 Real Instagram scraping is ENABLED!")
        print("   Your scraping will return actual Instagram data.")
    else:
        print("❌ Username: Not configured")
        print("❌ Password: Not configured")  
        print()
        print("📋 Mock Instagram scraping is ACTIVE")
        print("   Your scraping will return sample/demo data.")

def main():
    demo_setup_guide()
    show_current_status()
    test_current_setup()

if __name__ == '__main__':
    main()