"""
Instagram scraping service using Instagram Basic Display API and web scraping
This service provides methods to scrape publicly available Instagram content
"""
import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramScraper:
    """
    Instagram scraper using official API and web scraping for public content
    """
    
    def __init__(self):
        self.client_id = os.environ.get('INSTAGRAM_CLIENT_ID')
        self.client_secret = os.environ.get('INSTAGRAM_CLIENT_SECRET')
        self.access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
        self.username = os.environ.get('INSTAGRAM_USERNAME')
        self.password = os.environ.get('INSTAGRAM_PASSWORD')
        self.api_client = None
        self.is_authenticated = False
        self.rate_limit_delay = 2  # Seconds between requests
        
        # Instagram Basic Display API endpoints
        self.base_url = "https://graph.instagram.com"
        self.auth_url = "https://api.instagram.com/oauth/authorize"
        self.token_url = "https://api.instagram.com/oauth/access_token"
        
    def initialize(self):
        """Initialize Instagram API client"""
        try:
            # Try to use instagrapi for more robust scraping
            from instagrapi import Client
            
            if not self.username or not self.password or self.username == 'your_instagram_username' or self.password == 'your_instagram_password':
                logger.warning("Instagram credentials not found. Please set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD")
                logger.info("Note: Use a dedicated account for scraping to avoid issues with your main account")
                logger.info("Currently using MOCK DATA for Instagram scraping")
                self.is_authenticated = False
                return False
            
            logger.info(f"Attempting to authenticate Instagram account: {self.username}")
            self.api_client = Client()
            
            # Login with credentials
            try:
                self.api_client.login(self.username, self.password)
                self.is_authenticated = True
                logger.info(f"✅ Instagram authentication successful for: {self.username}")
                logger.info("🔥 REAL INSTAGRAM SCRAPING IS NOW ACTIVE!")
                return True
            except Exception as login_error:
                logger.error(f"❌ Instagram login failed for {self.username}: {login_error}")
                logger.warning("Common issues:")
                logger.warning("  • Incorrect username/password")
                logger.warning("  • Account suspended or restricted")
                logger.warning("  • Two-factor authentication enabled")
                logger.warning("  • Instagram detected automation")
                logger.info("Falling back to MOCK DATA mode")
                self.api_client = None
                self.is_authenticated = False
                return False
            
        except ImportError:
            logger.error("instagrapi not installed. Install with: pip install instagrapi")
            logger.info("Run: pip install instagrapi")
            self.is_authenticated = False
            return False
        except Exception as e:
            logger.error(f"Failed to initialize Instagram client: {e}")
            self.is_authenticated = False
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict[str, Any]]:
        """Get information about a public Instagram user"""
        try:
            if not self.api_client or not self.is_authenticated:
                return self._get_mock_user_info(username)
            
            # Get user info
            user_info = self.api_client.user_info_by_username(username)
            
            return {
                'user_id': str(user_info.pk),
                'username': user_info.username,
                'full_name': user_info.full_name,
                'biography': user_info.biography,
                'follower_count': user_info.follower_count,
                'following_count': user_info.following_count,
                'media_count': user_info.media_count,
                'is_verified': user_info.is_verified,
                'is_private': user_info.is_private,
                'profile_pic_url': user_info.profile_pic_url,
                'external_url': user_info.external_url,
                'is_business': user_info.is_business,
                'category': user_info.category
            }
            
        except Exception as e:
            logger.error(f"Error getting user info for {username}: {e}")
            return self._get_mock_user_info(username)
    
    def scrape_user_posts(self, username: str, max_posts: int = 20) -> Dict[str, Any]:
        """
        Scrape posts from a public Instagram user
        
        Args:
            username: Instagram username
            max_posts: Maximum number of posts to scrape
            
        Returns:
            Dictionary containing scraped posts and metadata
        """
        try:
            if not self.api_client or not self.is_authenticated:
                logger.info(f"📄 Generating mock data for @{username} (Instagram API not configured)")
                return self._mock_scrape_posts(username, max_posts)
            
            logger.info(f"🔍 Scraping REAL Instagram data for @{username} (max: {max_posts} posts)...")
            
            # Get user ID first
            user_info = self.api_client.user_info_by_username(username)
            
            if user_info.is_private:
                logger.warning(f"User {username} has a private account. Cannot scrape posts.")
                return {
                    'username': username,
                    'error': 'Private account',
                    'scraped_count': 0,
                    'posts': []
                }
            
            # Get user's media
            medias = self.api_client.user_medias(user_info.pk, amount=max_posts)
            
            posts = []
            for media in medias:
                # Add rate limiting
                time.sleep(self.rate_limit_delay)
                
                try:
                    # Get detailed media info
                    media_info = self.api_client.media_info(media.pk)
                    
                    post_data = {
                        'id': str(media.pk),
                        'shortcode': media.code,
                        'caption': media.caption_text or '',
                        'timestamp': media.taken_at.isoformat() if media.taken_at else None,
                        'like_count': media.like_count,
                        'comment_count': media.comment_count,
                        'media_type': str(media.media_type),
                        'url': f"https://www.instagram.com/p/{media.code}/",
                        'display_url': media.thumbnail_url,
                        'is_video': media.media_type == 2,  # 1=photo, 2=video, 8=carousel
                        'video_url': media.video_url if hasattr(media, 'video_url') else None,
                        'hashtags': self._extract_hashtags(media.caption_text or ''),
                        'mentions': self._extract_mentions(media.caption_text or ''),
                        'location': media.location.name if media.location else None
                    }
                    
                    posts.append(post_data)
                    
                except Exception as post_error:
                    logger.error(f"Error processing post {media.pk}: {post_error}")
                    continue
            
            result = {
                'username': username,
                'user_id': str(user_info.pk),
                'scraped_count': len(posts),
                'posts': posts,
                'scraped_at': datetime.now().isoformat(),
                'max_posts_requested': max_posts,
                'user_info': {
                    'follower_count': user_info.follower_count,
                    'following_count': user_info.following_count,
                    'media_count': user_info.media_count,
                    'is_verified': user_info.is_verified
                }
            }
            
            logger.info(f"✅ Successfully scraped {len(posts)} REAL posts from @{username}!")
            logger.info(f"📊 Stats: {user_info.follower_count:,} followers, {user_info.media_count:,} total posts")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping posts from {username}: {e}")
            return self._mock_scrape_posts(username, max_posts)
    
    def scrape_hashtag_posts(self, hashtag: str, max_posts: int = 20) -> Dict[str, Any]:
        """
        Scrape posts from a hashtag
        
        Args:
            hashtag: Hashtag name (without #)
            max_posts: Maximum number of posts to scrape
            
        Returns:
            Dictionary containing scraped posts and metadata
        """
        try:
            if not self.api_client or not self.is_authenticated:
                return self._mock_scrape_hashtag(hashtag, max_posts)
            
            # Get hashtag media
            medias = self.api_client.hashtag_medias_recent(hashtag, amount=max_posts)
            
            posts = []
            for media in medias:
                # Add rate limiting
                time.sleep(self.rate_limit_delay)
                
                try:
                    post_data = {
                        'id': str(media.pk),
                        'shortcode': media.code,
                        'caption': media.caption_text or '',
                        'timestamp': media.taken_at.isoformat() if media.taken_at else None,
                        'like_count': media.like_count,
                        'comment_count': media.comment_count,
                        'author': media.user.username,
                        'author_id': str(media.user.pk),
                        'media_type': str(media.media_type),
                        'url': f"https://www.instagram.com/p/{media.code}/",
                        'display_url': media.thumbnail_url,
                        'is_video': media.media_type == 2,
                        'hashtags': self._extract_hashtags(media.caption_text or ''),
                        'mentions': self._extract_mentions(media.caption_text or '')
                    }
                    
                    posts.append(post_data)
                    
                except Exception as post_error:
                    logger.error(f"Error processing hashtag post {media.pk}: {post_error}")
                    continue
            
            result = {
                'hashtag': hashtag,
                'scraped_count': len(posts),
                'posts': posts,
                'scraped_at': datetime.now().isoformat(),
                'max_posts_requested': max_posts
            }
            
            logger.info(f"Successfully scraped {len(posts)} posts from #{hashtag}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping hashtag #{hashtag}: {e}")
            return self._mock_scrape_hashtag(hashtag, max_posts)
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for Instagram users"""
        try:
            if not self.api_client or not self.is_authenticated:
                return self._mock_search_users(query, limit)
            
            users = self.api_client.search_users(query)[:limit]
            
            result = []
            for user in users:
                user_data = {
                    'user_id': str(user.pk),
                    'username': user.username,
                    'full_name': user.full_name,
                    'is_verified': user.is_verified,
                    'is_private': user.is_private,
                    'follower_count': user.follower_count,
                    'profile_pic_url': user.profile_pic_url
                }
                result.append(user_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching users with query '{query}': {e}")
            return self._mock_search_users(query, limit)
    
    def get_post_comments(self, post_shortcode: str, max_comments: int = 50) -> List[Dict[str, Any]]:
        """Get comments from a specific post"""
        try:
            if not self.api_client or not self.is_authenticated:
                return []
            
            # Get media by shortcode
            media_pk = self.api_client.media_pk_from_code(post_shortcode)
            comments = self.api_client.media_comments(media_pk, amount=max_comments)
            
            result = []
            for comment in comments:
                comment_data = {
                    'id': str(comment.pk),
                    'text': comment.text,
                    'timestamp': comment.created_at.isoformat() if comment.created_at else None,
                    'like_count': comment.like_count,
                    'author': comment.user.username,
                    'author_id': str(comment.user.pk),
                    'is_verified': comment.user.is_verified
                }
                result.append(comment_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting comments for post {post_shortcode}: {e}")
            return []
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        return re.findall(r'#(\w+)', text)
    
    def _extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        import re
        return re.findall(r'@(\w+)', text)
    
    def _get_mock_user_info(self, username: str) -> Dict[str, Any]:
        """Return mock user info when real API is not available"""
        import random
        
        return {
            'user_id': str(random.randint(1000000, 9999999)),
            'username': username,
            'full_name': f"Mock User {username}",
            'biography': f"This is a mock biography for {username}",
            'follower_count': random.randint(100, 100000),
            'following_count': random.randint(50, 1000),
            'media_count': random.randint(10, 500),
            'is_verified': random.choice([True, False]),
            'is_private': False,
            'profile_pic_url': f"https://via.placeholder.com/150?text={username}",
            'external_url': None,
            'is_business': random.choice([True, False]),
            'category': 'Entertainment'
        }
    
    def _mock_scrape_posts(self, username: str, max_posts: int) -> Dict[str, Any]:
        """Return mock scraped posts when real API is not available"""
        import random
        
        mock_captions = [
            "Amazing view from the office today! #work #life",
            "New project launching soon. Stay tuned! #tech #innovation",
            "Coffee break thoughts ☕ #coffee #productivity",
            "Team meeting insights #collaboration #growth",
            "Weekend vibes starting early #weekend #relax"
        ]
        
        posts = []
        scraped_count = min(max_posts, random.randint(5, 15))
        
        for i in range(scraped_count):
            post = {
                'id': str(random.randint(1000000000, 9999999999)),
                'shortcode': f"mock_{random.randint(1000, 9999)}",
                'caption': random.choice(mock_captions),
                'timestamp': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                'like_count': random.randint(10, 1000),
                'comment_count': random.randint(0, 100),
                'media_type': str(random.choice([1, 2])),  # 1=photo, 2=video
                'url': f"https://www.instagram.com/p/mock_{random.randint(1000, 9999)}/",
                'display_url': f"https://via.placeholder.com/400?text=Post{i+1}",
                'is_video': random.choice([True, False]),
                'hashtags': ['work', 'life', 'tech'],
                'mentions': [],
                'location': random.choice(['New York', 'San Francisco', 'London', None])
            }
            posts.append(post)
        
        return {
            'username': username,
            'user_id': str(random.randint(1000000, 9999999)),
            'scraped_count': len(posts),
            'posts': posts,
            'scraped_at': datetime.now().isoformat(),
            'max_posts_requested': max_posts,
            'user_info': self._get_mock_user_info(username)
        }
    
    def _mock_scrape_hashtag(self, hashtag: str, max_posts: int) -> Dict[str, Any]:
        """Return mock hashtag posts when real API is not available"""
        import random
        
        posts = []
        scraped_count = min(max_posts, random.randint(10, 20))
        
        for i in range(scraped_count):
            post = {
                'id': str(random.randint(1000000000, 9999999999)),
                'shortcode': f"hashtag_{random.randint(1000, 9999)}",
                'caption': f"Post about #{hashtag} - {i+1}",
                'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 72))).isoformat(),
                'like_count': random.randint(5, 500),
                'comment_count': random.randint(0, 50),
                'author': f"user_{random.randint(1000, 9999)}",
                'author_id': str(random.randint(1000000, 9999999)),
                'media_type': str(random.choice([1, 2])),
                'url': f"https://www.instagram.com/p/hashtag_{random.randint(1000, 9999)}/",
                'display_url': f"https://via.placeholder.com/400?text={hashtag}{i+1}",
                'is_video': random.choice([True, False]),
                'hashtags': [hashtag, 'trending', 'viral'],
                'mentions': []
            }
            posts.append(post)
        
        return {
            'hashtag': hashtag,
            'scraped_count': len(posts),
            'posts': posts,
            'scraped_at': datetime.now().isoformat(),
            'max_posts_requested': max_posts
        }
    
    def _mock_search_users(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Return mock user search results when real API is not available"""
        import random
        
        users = []
        for i in range(min(limit, 5)):
            user = {
                'user_id': str(random.randint(1000000, 9999999)),
                'username': f"{query}_user_{i+1}",
                'full_name': f"{query.title()} User {i+1}",
                'is_verified': random.choice([True, False]),
                'is_private': random.choice([True, False]),
                'follower_count': random.randint(100, 10000),
                'profile_pic_url': f"https://via.placeholder.com/150?text={query}{i+1}"
            }
            users.append(user)
        
        return users

# Global scraper instance
instagram_scraper = InstagramScraper()

def get_instagram_scraper():
    """Get the global Instagram scraper instance"""
    if not instagram_scraper.api_client:
        instagram_scraper.initialize()
    return instagram_scraper
