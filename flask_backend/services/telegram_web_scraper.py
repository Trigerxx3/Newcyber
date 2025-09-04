"""
Telegram Web Scraper - Alternative method without API requirements
Scrapes public Telegram channels using web interface
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

class TelegramWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        self.base_url = "https://t.me"
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

    def initialize(self):
        """Initialize the web scraper"""
        try:
            # Test connection
            response = self.session.get(self.base_url, timeout=10)
            if response.status_code == 200:
                logger.info("✅ Telegram web scraper initialized successfully")
                return True
            else:
                logger.error(f"❌ Failed to connect to Telegram: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Telegram web scraper initialization failed: {str(e)}")
            return False

    def get_public_channels(self, search_query: str = "") -> List[Dict]:
        """
        Get popular public channels or search for channels
        """
        try:
            channels = []
            
            # Popular channels (you can expand this list)
            popular_channels = [
                {"username": "durov", "title": "Pavel Durov", "description": "Telegram founder updates"},
                {"username": "telegram", "title": "Telegram", "description": "Official Telegram channel"},
                {"username": "breakingmash", "title": "Breaking Mash", "description": "Breaking news"},
                {"username": "rt_russian", "title": "RT Russian", "description": "RT News in Russian"},
                {"username": "bbcrussian", "title": "BBC Russian", "description": "BBC News in Russian"},
                {"username": "rianews", "title": "RIA News", "description": "Russian news agency"},
                {"username": "tass_agency", "title": "TASS", "description": "Russian news agency"},
                {"username": "meduzaproject", "title": "Meduza", "description": "Independent news"},
            ]
            
            if search_query:
                # Filter channels by search query
                channels = [
                    ch for ch in popular_channels 
                    if search_query.lower() in ch['title'].lower() or 
                       search_query.lower() in ch['description'].lower()
                ]
            else:
                channels = popular_channels
            
            # Add additional info by checking each channel
            for channel in channels:
                try:
                    channel_info = self._get_channel_info(channel['username'])
                    channel.update(channel_info)
                except Exception as e:
                    logger.warning(f"Failed to get info for {channel['username']}: {str(e)}")
                    continue
                
                time.sleep(1)  # Rate limiting
            
            return channels
            
        except Exception as e:
            logger.error(f"Failed to get public channels: {str(e)}")
            return []

    def _get_channel_info(self, username: str) -> Dict:
        """Get basic info about a channel"""
        try:
            url = f"{self.base_url}/{username}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract channel info from meta tags
                title = self._extract_meta_content(soup, 'og:title') or username
                description = self._extract_meta_content(soup, 'og:description') or ""
                image = self._extract_meta_content(soup, 'og:image') or ""
                
                # Try to extract member count from page
                members_text = soup.find('div', class_='tgme_page_extra')
                members = 0
                if members_text:
                    members_match = re.search(r'(\d+(?:\.\d+)?[KM]?)\s+(?:members|subscribers)', members_text.get_text())
                    if members_match:
                        members_str = members_match.group(1)
                        members = self._parse_count(members_str)
                
                return {
                    'title': title,
                    'description': description,
                    'image': image,
                    'members': members,
                    'url': url,
                    'active': True
                }
            else:
                return {'active': False}
                
        except Exception as e:
            logger.error(f"Failed to get channel info for {username}: {str(e)}")
            return {'active': False}

    def _extract_meta_content(self, soup, property_name: str) -> Optional[str]:
        """Extract content from meta tags"""
        meta_tag = soup.find('meta', property=property_name) or soup.find('meta', attrs={'name': property_name})
        return meta_tag.get('content') if meta_tag else None

    def _parse_count(self, count_str: str) -> int:
        """Parse count strings like '1.2K', '500K', '1M' to integers"""
        try:
            count_str = count_str.strip().upper()
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            else:
                return int(count_str)
        except:
            return 0

    def scrape_channel(self, username: str, limit: int = 20) -> List[Dict]:
        """
        Scrape messages from a public Telegram channel
        """
        try:
            messages = []
            url = f"{self.base_url}/{username}"
            
            logger.info(f"🔍 Scraping Telegram channel: {username}")
            
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                logger.error(f"Failed to access channel {username}: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find message containers
            message_elements = soup.find_all('div', class_='tgme_widget_message')
            
            for i, msg_elem in enumerate(message_elements[:limit]):
                try:
                    message_data = self._extract_message_data(msg_elem, username)
                    if message_data:
                        messages.append(message_data)
                except Exception as e:
                    logger.warning(f"Failed to extract message {i}: {str(e)}")
                    continue
            
            logger.info(f"✅ Scraped {len(messages)} messages from {username}")
            return messages
            
        except Exception as e:
            logger.error(f"Failed to scrape channel {username}: {str(e)}")
            return []

    def _extract_message_data(self, msg_elem, username: str) -> Optional[Dict]:
        """Extract data from a message element"""
        try:
            # Message ID
            msg_id = msg_elem.get('data-post', '').split('/')[-1] if msg_elem.get('data-post') else None
            
            # Message text
            text_elem = msg_elem.find('div', class_='tgme_widget_message_text')
            text = text_elem.get_text(strip=True) if text_elem else ""
            
            # Date
            date_elem = msg_elem.find('time')
            date = date_elem.get('datetime') if date_elem else ""
            
            # Views
            views_elem = msg_elem.find('span', class_='tgme_widget_message_views')
            views = 0
            if views_elem:
                views_text = views_elem.get_text(strip=True)
                views = self._parse_count(views_text)
            
            # Media info
            media_type = None
            media_url = None
            
            # Check for images
            img_elem = msg_elem.find('a', class_='tgme_widget_message_photo_wrap')
            if img_elem:
                media_type = 'photo'
                media_url = img_elem.get('href')
            
            # Check for videos
            video_elem = msg_elem.find('video') or msg_elem.find('a', class_='tgme_widget_message_video_wrap')
            if video_elem:
                media_type = 'video'
                if video_elem.name == 'video':
                    media_url = video_elem.get('src')
                else:
                    media_url = video_elem.get('href')
            
            # Check for links
            link_elem = msg_elem.find('a', class_='tgme_widget_message_link_preview')
            if link_elem and not media_type:
                media_type = 'link'
                media_url = link_elem.get('href')
            
            return {
                'id': msg_id,
                'text': text,
                'date': date,
                'views': views,
                'media_type': media_type,
                'media_url': media_url,
                'channel': username,
                'platform': 'telegram',
                'url': f"{self.base_url}/{username}/{msg_id}" if msg_id else None
            }
            
        except Exception as e:
            logger.error(f"Failed to extract message data: {str(e)}")
            return None

    def search_channels(self, query: str) -> List[Dict]:
        """
        Search for channels (simplified version)
        """
        try:
            # For now, search within known channels
            channels = self.get_public_channels(query)
            return channels
            
        except Exception as e:
            logger.error(f"Failed to search channels: {str(e)}")
            return []

    def get_health_status(self) -> Dict:
        """Check if the scraper is working"""
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'message': 'Telegram web access working',
                    'method': 'web_scraping'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'HTTP {response.status_code}',
                    'method': 'web_scraping'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'method': 'web_scraping'
            }
