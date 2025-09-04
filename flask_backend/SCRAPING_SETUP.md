# Real Data Scraping Setup Guide

This guide explains how to set up real API integrations for scraping Telegram, Instagram, and WhatsApp data.

## 🔧 Prerequisites

### Install Required Dependencies

```bash
cd flask_backend
pip install -r requirements.txt
```

Key packages installed:
- `telethon`: Telegram API client
- `instagrapi`: Instagram API client  
- `requests`: HTTP client for WhatsApp Business API

## 📱 Telegram Setup

### 1. Get Telegram API Credentials

1. Go to [https://my.telegram.org/auth](https://my.telegram.org/auth)
2. Log in with your phone number
3. Go to "API Development Tools"
4. Create a new application
5. Get your `api_id` and `api_hash`

### 2. Set Environment Variables

```bash
# Telegram API Configuration
TELEGRAM_API_ID=your_api_id_here
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890
TELEGRAM_BOT_TOKEN=optional_bot_token
```

### 3. First Time Setup

When you first run the scraper, it will ask for phone verification:
- Enter your phone number
- Enter the verification code sent to your phone
- Session will be saved for future use

### 4. Available Features

- ✅ Scrape public channels
- ✅ Search for channels
- ✅ Get channel information
- ✅ Filter by keywords
- ✅ Download media files

## 📸 Instagram Setup

### Option 1: Instagram Basic Display API (Recommended)

1. Go to [Facebook Developer Console](https://developers.facebook.com/)
2. Create a new app
3. Add Instagram Basic Display API
4. Get your credentials

```bash
# Instagram API Configuration
INSTAGRAM_CLIENT_ID=your_client_id
INSTAGRAM_CLIENT_SECRET=your_client_secret
INSTAGRAM_ACCESS_TOKEN=your_access_token
```

### Option 2: Account Login (Use Carefully)

```bash
# Instagram Login Configuration
INSTAGRAM_USERNAME=your_dedicated_account
INSTAGRAM_PASSWORD=your_password
```

**⚠️ Warning:** Use a dedicated account, not your personal one. Instagram may restrict accounts that scrape heavily.

### 3. Rate Limits

- Instagram Basic Display API: 200 requests/hour
- Account scraping: ~200 requests/hour (unofficial)

### 4. Available Features

- ✅ Scrape public profiles
- ✅ Get post information
- ✅ Search users
- ✅ Extract hashtags and mentions
- ✅ Download media
- ❌ Cannot scrape private accounts

## 💬 WhatsApp Setup

**Note:** WhatsApp doesn't allow traditional scraping. Only official Business API is supported.

### 1. WhatsApp Business API Setup

1. Go to [Facebook Developer Console](https://developers.facebook.com/)
2. Create a WhatsApp Business app
3. Get Business Account ID and Access Token
4. Set up phone number

```bash
# WhatsApp Business API Configuration
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
WHATSAPP_ACCESS_TOKEN=your_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your_verify_token
```

### 2. Webhook Setup

Configure webhook URL in Facebook Developer Console:
- URL: `https://your-domain.com/api/scraping/whatsapp/webhook`
- Verify Token: Use `WHATSAPP_WEBHOOK_VERIFY_TOKEN`

### 3. Available Features

- ✅ Send messages
- ✅ Receive webhooks
- ✅ Get business profile
- ✅ Handle message status updates
- ❌ Cannot scrape group messages without explicit consent

## 🔒 Security Best Practices

### 1. Environment Variables

Create a `.env` file:

```bash
cp env_template.txt .env
# Edit .env with your real credentials
```

### 2. Rate Limiting

All scrapers implement rate limiting:
- Telegram: 30 requests/minute
- Instagram: 200 requests/hour
- WhatsApp: Business API limits

### 3. Error Handling

- Graceful fallbacks to mock data when APIs fail
- Detailed error logging
- Session persistence for Telegram

### 4. Legal Compliance

- Only scrape public content
- Respect platform Terms of Service
- Implement proper attribution
- Consider user privacy

## 🚀 Usage Examples

### Start Scraping Services

```python
# In your Flask app
from services.telegram_scraper import get_telegram_scraper
from services.instagram_scraper import get_instagram_scraper
from services.whatsapp_scraper import get_whatsapp_scraper

# Initialize scrapers
telegram = await get_telegram_scraper()
instagram = get_instagram_scraper()
whatsapp = get_whatsapp_scraper()
```

### Scrape Telegram Channel

```python
# Scrape recent messages
result = await telegram.scrape_channel('@channel_name', max_messages=50)
```

### Scrape Instagram Profile

```python
# Scrape user posts
result = instagram.scrape_user_posts('username', max_posts=20)
```

### Handle WhatsApp Messages

```python
# Process webhook data
processed = whatsapp.handle_webhook(webhook_data)
```

## 🛠️ Troubleshooting

### Common Issues

1. **Telegram "Phone number required"**
   - Set `TELEGRAM_PHONE_NUMBER` in environment
   - Run initial setup with phone verification

2. **Instagram "Login failed"**
   - Check username/password
   - Try using Instagram Basic Display API instead
   - Account may be rate limited

3. **WhatsApp "No access token"**
   - Verify Business API setup
   - Check Facebook Developer Console permissions

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Check

Check scraper status:

```bash
curl http://localhost:5000/api/scraping/health-check
```

## 📊 Monitoring

### Track Scraping Jobs

- View active jobs in admin dashboard
- Monitor success/failure rates
- Set up alerts for errors

### Database Storage

All scraped content is stored in the database:
- `Content` table for posts/messages
- `Source` table for channels/profiles
- Automatic deduplication

## 🔄 Automation

### Scheduled Scraping

Jobs can be scheduled:
- Hourly updates
- Daily summaries
- Weekly reports

### Queue Management

Use Redis for job queuing:

```bash
# Install Redis
redis-server

# Set Redis URL
REDIS_URL=redis://localhost:6379/0
```

## 📈 Scaling

### Production Deployment

1. Use PostgreSQL instead of SQLite
2. Set up Redis for job queuing
3. Use Celery for background tasks
4. Implement proper logging and monitoring

### Multiple Accounts

For heavy scraping:
- Rotate multiple Telegram accounts
- Use multiple Instagram developer apps
- Set up multiple WhatsApp Business numbers

## 📞 Support

### Getting Help

1. Check the logs for detailed error messages
2. Verify API credentials and permissions
3. Test with health check endpoint
4. Review platform-specific documentation

### API Documentation

- [Telegram API Docs](https://core.telegram.org/api)
- [Instagram Basic Display API](https://developers.facebook.com/docs/instagram-basic-display-api)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

Remember to always respect platform terms of service and user privacy when scraping data!
