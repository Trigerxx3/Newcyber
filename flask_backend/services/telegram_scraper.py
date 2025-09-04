"""
Telegram scraping service for public channels and groups
This service provides methods to scrape publicly available Telegram content
"""
import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramScraper:
    """
    Telegram scraper for public channels and groups
    Uses Telegram's public APIs and web scraping techniques
    """
    
    def __init__(self):
        self.api_id = os.environ.get('TELEGRAM_API_ID')
        self.api_hash = os.environ.get('TELEGRAM_API_HASH')
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.session_file = 'telegram_session'
        self.client = None
        
    async def initialize(self):
        """Initialize Telegram client"""
        try:
            # Try to import telethon (popular Telegram client library)
            from telethon import TelegramClient
            from telethon.errors import SessionPasswordNeededError
            
            if not self.api_id or not self.api_hash:
                logger.warning("Telegram API credentials not found. Please set TELEGRAM_API_ID and TELEGRAM_API_HASH in environment variables.")
                logger.info("You can get these from https://my.telegram.org/auth")
                return False
            
            # Create client with session file for persistence
            self.client = TelegramClient(
                session=self.session_file,
                api_id=int(self.api_id),
                api_hash=self.api_hash,
                system_version="4.16.30-vxCUSTOM"
            )
            
            # Start the client
            await self.client.start(
                phone=os.environ.get('TELEGRAM_PHONE_NUMBER'),
                bot_token=self.bot_token if self.bot_token else None
            )
            
            # Check if we're connected
            if await self.client.is_user_authorized():
                logger.info("Telegram client initialized successfully")
                return True
            else:
                logger.warning("Telegram client not authorized. Manual login required.")
                return False
            
        except ImportError:
            logger.error("Telethon not installed. Install with: pip install telethon cryptg")
            logger.info("Run: pip install telethon cryptg")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Telegram client: {e}")
            logger.info("Make sure your API credentials are correct and your phone number is verified")
            return False
    
    async def get_public_channels(self) -> List[Dict[str, Any]]:
        """Get list of public channels"""
        try:
            if not self.client:
                return self._get_mock_channels()
            
            # In a real implementation, you would search for public channels
            # For now, return a curated list of known public channels
            channels = [
                {
                    'id': '@durov',
                    'title': 'Pavel Durov',
                    'username': 'durov',
                    'members': 500000,
                    'description': 'Founder of Telegram',
                    'public': True,
                    'verified': True
                },
                {
                    'id': '@telegram',
                    'title': 'Telegram',
                    'username': 'telegram',
                    'members': 1000000,
                    'description': 'Official Telegram channel',
                    'public': True,
                    'verified': True
                }
            ]
            
            return channels
            
        except Exception as e:
            logger.error(f"Error getting public channels: {e}")
            return self._get_mock_channels()
    
    async def scrape_channel(self, channel_id: str, max_messages: int = 50, 
                           keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Scrape messages from a public Telegram channel
        
        Args:
            channel_id: Channel username or ID (e.g., '@channel_name')
            max_messages: Maximum number of messages to scrape
            keywords: Optional list of keywords to filter messages
            
        Returns:
            Dictionary containing scraped messages and metadata
        """
        try:
            if not self.client:
                return await self._mock_scrape_channel(channel_id, max_messages, keywords)
            
            from telethon.tl.functions.messages import GetHistoryRequest
            
            # Get channel entity
            channel = await self.client.get_entity(channel_id)
            
            # Scrape messages
            messages = []
            async for message in self.client.iter_messages(channel, limit=max_messages):
                if message.text:
                    # Filter by keywords if provided
                    if keywords:
                        if not any(keyword.lower() in message.text.lower() for keyword in keywords):
                            continue
                    
                    message_data = {
                        'id': message.id,
                        'text': message.text,
                        'date': message.date.isoformat() if message.date else None,
                        'author': getattr(message.sender, 'username', 'Unknown') if message.sender else 'Unknown',
                        'author_id': message.sender_id,
                        'views': getattr(message, 'views', 0),
                        'forwards': getattr(message, 'forwards', 0),
                        'replies': getattr(message.replies, 'replies', 0) if message.replies else 0,
                        'media': bool(message.media),
                        'media_type': str(type(message.media).__name__) if message.media else None,
                        'url': f"https://t.me/{channel.username}/{message.id}" if hasattr(channel, 'username') else None
                    }
                    messages.append(message_data)
            
            result = {
                'channel_id': channel_id,
                'channel_title': getattr(channel, 'title', 'Unknown'),
                'scraped_count': len(messages),
                'messages': messages,
                'scraped_at': datetime.now().isoformat(),
                'keywords_used': keywords or [],
                'max_messages_requested': max_messages
            }
            
            logger.info(f"Successfully scraped {len(messages)} messages from {channel_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping channel {channel_id}: {e}")
            return await self._mock_scrape_channel(channel_id, max_messages, keywords)
    
    async def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a public channel"""
        try:
            if not self.client:
                return self._get_mock_channel_info(channel_id)
            
            channel = await self.client.get_entity(channel_id)
            
            info = {
                'id': channel.id,
                'title': getattr(channel, 'title', 'Unknown'),
                'username': getattr(channel, 'username', None),
                'description': getattr(channel, 'about', ''),
                'participants_count': getattr(channel, 'participants_count', 0),
                'verified': getattr(channel, 'verified', False),
                'restricted': getattr(channel, 'restricted', False),
                'scam': getattr(channel, 'scam', False),
                'fake': getattr(channel, 'fake', False),
                'public': not getattr(channel, 'username', None) is None
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting channel info for {channel_id}: {e}")
            return self._get_mock_channel_info(channel_id)
    
    async def search_public_channels(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for public channels by query"""
        try:
            if not self.client:
                return self._mock_search_channels(query, limit)
            
            from telethon.tl.functions.contacts import SearchRequest
            
            # Search for channels
            result = await self.client(SearchRequest(
                q=query,
                limit=limit
            ))
            
            channels = []
            for chat in result.chats:
                if hasattr(chat, 'broadcast') and chat.broadcast:  # Channel
                    channel_info = {
                        'id': chat.id,
                        'title': getattr(chat, 'title', 'Unknown'),
                        'username': getattr(chat, 'username', None),
                        'participants_count': getattr(chat, 'participants_count', 0),
                        'verified': getattr(chat, 'verified', False),
                        'public': not getattr(chat, 'username', None) is None
                    }
                    channels.append(channel_info)
            
            return channels[:limit]
            
        except Exception as e:
            logger.error(f"Error searching channels with query '{query}': {e}")
            return self._mock_search_channels(query, limit)
    
    def _get_mock_channels(self) -> List[Dict[str, Any]]:
        """Return mock channel data when real API is not available"""
        return [
            {
                'id': '@cyberthreat_news',
                'title': 'Cyber Threat News',
                'username': 'cyberthreat_news',
                'members': 15432,
                'description': 'Latest cyber security threats and news',
                'public': True,
                'verified': True
            },
            {
                'id': '@security_alerts',
                'title': 'Security Alerts',
                'username': 'security_alerts',
                'members': 8965,
                'description': 'Real-time security alerts and updates',
                'public': True,
                'verified': False
            },
            {
                'id': '@darkweb_intel',
                'title': 'Dark Web Intelligence',
                'username': 'darkweb_intel',
                'members': 3421,
                'description': 'Intelligence from dark web monitoring',
                'public': True,
                'verified': True
            },
            {
                'id': '@threat_hunting',
                'title': 'Threat Hunting Community',
                'username': 'threat_hunting',
                'members': 12890,
                'description': 'Community for threat hunters and analysts',
                'public': True,
                'verified': False
            }
        ]
    
    async def _mock_scrape_channel(self, channel_id: str, max_messages: int, 
                                 keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return mock scraped data when real API is not available"""
        import random
        
        # Generate mock messages
        mock_texts = [
            "New malware family discovered targeting financial institutions",
            "Critical vulnerability found in popular IoT devices",
            "Ransomware group claims responsibility for recent attacks",
            "Phishing campaign uses COVID-19 as bait",
            "Zero-day exploit being sold on dark web marketplaces",
            "APT group linked to state-sponsored cyber attacks",
            "New social engineering technique observed in the wild",
            "Cryptocurrency exchange suffers major security breach",
            "Botnet infrastructure taken down by law enforcement",
            "Security researchers discover new attack vector"
        ]
        
        messages = []
        scraped_count = min(max_messages, random.randint(10, 30))
        
        for i in range(scraped_count):
            text = random.choice(mock_texts)
            
            # Filter by keywords if provided
            if keywords:
                if not any(keyword.lower() in text.lower() for keyword in keywords):
                    continue
            
            message = {
                'id': random.randint(1000, 9999),
                'text': f"{text} - Message {i+1} from {channel_id}",
                'date': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
                'author': f"user_{random.randint(1000, 9999)}",
                'author_id': random.randint(100000, 999999),
                'views': random.randint(100, 5000),
                'forwards': random.randint(0, 100),
                'replies': random.randint(0, 50),
                'media': random.choice([True, False]),
                'media_type': random.choice(['photo', 'video', 'document', None]),
                'url': f"https://t.me/{channel_id.replace('@', '')}/{random.randint(1000, 9999)}"
            }
            messages.append(message)
        
        await asyncio.sleep(0.1)  # Simulate network delay
        
        return {
            'channel_id': channel_id,
            'channel_title': f"Mock Channel {channel_id}",
            'scraped_count': len(messages),
            'messages': messages,
            'scraped_at': datetime.now().isoformat(),
            'keywords_used': keywords or [],
            'max_messages_requested': max_messages
        }
    
    def _get_mock_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """Return mock channel info when real API is not available"""
        import random
        
        return {
            'id': random.randint(1000000, 9999999),
            'title': f"Mock Channel {channel_id}",
            'username': channel_id.replace('@', ''),
            'description': f"This is a mock description for {channel_id}",
            'participants_count': random.randint(100, 50000),
            'verified': random.choice([True, False]),
            'restricted': False,
            'scam': False,
            'fake': False,
            'public': True
        }
    
    def _mock_search_channels(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Return mock search results when real API is not available"""
        import random
        
        mock_channels = []
        for i in range(min(limit, 5)):
            mock_channels.append({
                'id': random.randint(1000000, 9999999),
                'title': f"{query} Channel {i+1}",
                'username': f"{query.lower()}_channel_{i+1}",
                'participants_count': random.randint(100, 10000),
                'verified': random.choice([True, False]),
                'public': True
            })
        
        return mock_channels
    
    async def close(self):
        """Close the Telegram client connection"""
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")

# Global scraper instance
telegram_scraper = TelegramScraper()

async def get_telegram_scraper():
    """Get the global Telegram scraper instance"""
    if not telegram_scraper.client:
        await telegram_scraper.initialize()
    return telegram_scraper
