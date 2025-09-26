# Instagram Scraping Setup Guide

## 🔧 Current Status
✅ **All components are working correctly!**
- Instaloader installed (v4.14.2)
- Database persistence working
- API endpoints ready
- Keyword analysis functional

## ⚠️ Instagram Authentication Issue

The 401/403 errors you're seeing are due to Instagram's anti-bot protection. For reliable scraping, you need:

### Option 1: Add Instagram Credentials (Recommended)

1. **Create a dedicated Instagram account** (don't use your personal account)
2. **Add credentials to your `.env` file:**
   ```bash
   # Instagram scraping credentials (use a dedicated account)
   INSTAGRAM_USERNAME=your_dedicated_account
   INSTAGRAM_PASSWORD=your_password
   ```

3. **Restart your Flask backend**

### Option 2: Use Without Authentication (Limited)

Without credentials, you can only scrape:
- Some public profiles (hit or miss)
- Limited content due to rate limits
- Subject to frequent 401/403 errors

## 🚀 Testing Your Setup

### Test with credentials:
```bash
python test_instagram_scraping.py
```

### Test API endpoints:
```bash
# Start your Flask server first, then:
python test_instagram_scraping.py --api-test --token YOUR_ADMIN_JWT_TOKEN
```

## 📱 Using the Web Interface

1. **Start your Flask backend:**
   ```bash
   python app.py
   ```

2. **Go to Admin → Scraping**

3. **Try these test accounts:**
   - `instagram` (official Instagram account)
   - `natgeo` (National Geographic)
   - `nasa` (NASA)
   - Any public celebrity/brand account

4. **Check results in "Scraped Content" tab**

## 🔍 Troubleshooting

### If you see "Nothing scraped":
- Check Flask console for error messages
- Verify the account is public
- Try a different username
- Check if Instagram is blocking your IP

### If you get 404 errors:
- Make sure Flask backend is running on port 5000
- Check that routes are registered (look for "✅ Registered routes.instagram")

### If you get authentication errors:
- Add Instagram credentials to `.env`
- Use a dedicated scraping account
- Wait a few minutes between scrape attempts

## 🎯 Expected Behavior

**With proper setup, you should see:**

1. **Successful scraping:** Posts appear in the results table
2. **Database persistence:** Content shows in "Scraped Content" tab
3. **Keyword analysis:** Suspicion scores calculated
4. **Error handling:** Clear messages for private/non-existent accounts

**Sample successful output:**
```json
{
  "source": {"platform": "Instagram", "source_handle": "username"},
  "user": {"username": "test", "bio": "User bio", "full_name": "Full Name"},
  "posts": [
    {
      "content_id": 123,
      "text_content": "Post content here...",
      "suspicion_score": 15,
      "posted_at": "2024-01-01T12:00:00",
      "analysis": "Low risk content"
    }
  ],
  "scraped_count": 10
}
```

## 🛡️ Important Notes

1. **Use responsibly** - Respect Instagram's terms of service
2. **Rate limits** - Don't scrape too frequently 
3. **Dedicated account** - Use a separate account for scraping
4. **Public content only** - Cannot scrape private profiles
5. **Legal compliance** - Only scrape public information for legitimate purposes

## 📞 Support

If you still have issues:
1. Check the Flask console logs
2. Verify all dependencies are installed
3. Try testing with a different public account
4. Consider adding Instagram credentials for better reliability