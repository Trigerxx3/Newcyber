#!/usr/bin/env python3
"""
Instagram API Setup Helper
This script helps you configure Instagram API credentials and test the connection
"""

import os
import time
from dotenv import load_dotenv

def setup_instagram():
    """Setup and test Instagram API connection"""
    print("📸 Instagram API Setup Helper")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    username = os.environ.get('INSTAGRAM_USERNAME')
    password = os.environ.get('INSTAGRAM_PASSWORD')
    
    if not username or not password:
        print("❌ Missing Instagram credentials!")
        print("\n📋 Instagram Setup Options:")
        print("\n🔶 Option 1: Account Login (Simpler)")
        print("1. Create a dedicated Instagram account (NOT your personal one)")
        print("2. Add to .env file:")
        print("   INSTAGRAM_USERNAME=your_dedicated_account")
        print("   INSTAGRAM_PASSWORD=your_password")
        print("\n🔶 Option 2: Instagram Basic Display API (Recommended)")
        print("1. Go to https://developers.facebook.com/")
        print("2. Create a new app")
        print("3. Add Instagram Basic Display API")
        print("4. Get your credentials and add to .env:")
        print("   INSTAGRAM_CLIENT_ID=your_client_id")
        print("   INSTAGRAM_CLIENT_SECRET=your_client_secret")
        print("   INSTAGRAM_ACCESS_TOKEN=your_access_token")
        print("\n⚠️ Warning: Instagram heavily rate limits and may restrict accounts")
        return False
    
    try:
        # Try to import and initialize Instagram client
        from instagrapi import Client
        
        print(f"✅ Found Instagram credentials")
        print(f"👤 Username: {username}")
        print(f"🔑 Password: {'*' * len(password)}")
        
        # Create client
        cl = Client()
        
        print("\n🔄 Testing Instagram connection...")
        
        # Test login
        try:
            cl.login(username, password)
            print("✅ Instagram login successful!")
            
            # Get account info
            user_info = cl.user_info_by_username(username)
            print(f"👤 Account: @{user_info.username}")
            print(f"📝 Full name: {user_info.full_name}")
            print(f"👥 Followers: {user_info.follower_count}")
            print(f"📸 Posts: {user_info.media_count}")
            
            # Test searching for a public account
            print("\n🔍 Testing public account access...")
            try:
                # Search for Instagram's official account
                search_results = cl.search_users("instagram")
                if search_results:
                    print(f"✅ Can search users: Found {len(search_results)} results")
                    first_result = search_results[0]
                    print(f"📺 Test result: @{first_result.username}")
                else:
                    print("⚠️ Search returned no results")
                
            except Exception as search_error:
                print(f"⚠️ User search test failed: {search_error}")
            
            # Test getting posts from a public account
            print("\n📸 Testing post scraping...")
            try:
                # Get a few posts from Instagram's official account
                instagram_user = cl.user_info_by_username("instagram")
                posts = cl.user_medias(instagram_user.pk, amount=3)
                print(f"✅ Can scrape posts: Retrieved {len(posts)} posts")
                
                if posts:
                    latest_post = posts[0]
                    print(f"📝 Latest post: {latest_post.caption_text[:100] if latest_post.caption_text else 'No caption'}...")
                    print(f"❤️ Likes: {latest_post.like_count}")
                    print(f"💬 Comments: {latest_post.comment_count}")
                
            except Exception as post_error:
                print(f"⚠️ Post scraping test failed: {post_error}")
            
            return True
            
        except Exception as login_error:
            print(f"❌ Instagram login failed: {login_error}")
            print("\n💡 Common issues:")
            print("- Incorrect username/password")
            print("- Account suspended or restricted")
            print("- Two-factor authentication enabled")
            print("- Too many login attempts")
            print("\n🔧 Solutions:")
            print("- Use a fresh, dedicated account")
            print("- Disable 2FA temporarily")
            print("- Wait a few hours if rate limited")
            print("- Consider using Instagram Basic Display API instead")
            return False
            
    except ImportError:
        print("❌ instagrapi not installed!")
        print("Run: pip install instagrapi")
        return False
    except Exception as e:
        print(f"❌ Instagram setup failed: {e}")
        return False

def test_instagram_basic_display_api():
    """Test Instagram Basic Display API if configured"""
    load_dotenv()
    
    client_id = os.environ.get('INSTAGRAM_CLIENT_ID')
    access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
    
    if not client_id or not access_token:
        return False
    
    print("\n🔶 Testing Instagram Basic Display API...")
    
    try:
        import requests
        
        # Test API call
        url = f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Instagram Basic Display API works!")
            print(f"👤 User ID: {data.get('id')}")
            print(f"📝 Username: {data.get('username')}")
            return True
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as api_error:
        print(f"❌ API test failed: {api_error}")
        return False

def main():
    """Main setup function"""
    print("🚀 Starting Instagram API setup...")
    
    try:
        # Try account login first
        result = setup_instagram()
        
        if not result:
            # Try Basic Display API
            api_result = test_instagram_basic_display_api()
            if api_result:
                print("\n🎉 Instagram Basic Display API setup completed!")
                result = True
        
        if result:
            print("\n🎉 Instagram API setup completed successfully!")
            print("✅ You can now use real Instagram scraping")
            print("\n⚠️ Important reminders:")
            print("- Use responsibly and respect rate limits")
            print("- Only scrape public content")
            print("- Follow Instagram's Terms of Service")
        else:
            print("\n❌ Instagram API setup failed")
            print("💡 Please check the instructions above and try again")
            
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")

if __name__ == '__main__':
    main()
