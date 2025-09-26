"""
Instagram Scraper Service Wrapper
This service provides a unified interface for Instagram scraping functionality
"""
from .instagram_scraper import InstagramScraper, get_instagram_scraper
from typing import Dict, Any, List


class InstagramScraperService:
    """
    Service wrapper for Instagram scraping operations
    """
    
    def __init__(self):
        self.scraper = get_instagram_scraper()
        self.is_using_real_api = hasattr(self.scraper, 'is_authenticated') and self.scraper.is_authenticated
        
    def _add_status_info(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Add status information to the result"""
        result['scraping_status'] = {
            'using_real_api': self.is_using_real_api,
            'data_type': 'real' if self.is_using_real_api else 'mock',
            'message': 'Connected to Instagram API' if self.is_using_real_api else 'Using mock data - Instagram credentials not configured',
            'timestamp': result.get('scraped_at', ''),
            'source': 'Instagram API' if self.is_using_real_api else 'Mock Generator'
        }
        return result
    
    def scrape_profile(self, username: str, max_posts: int = 20) -> Dict[str, Any]:
        """
        Scrape Instagram profile posts
        
        Args:
            username: Instagram username
            max_posts: Maximum number of posts to scrape
            
        Returns:
            Dictionary containing scraped posts and metadata
        """
        try:
            result = self.scraper.scrape_user_posts(username, max_posts=max_posts)
            return self._add_status_info(result)
        except Exception as e:
            error_result = {
                'error': f'Failed to scrape profile {username}: {str(e)}',
                'username': username,
                'scraped_count': 0,
                'posts': []
            }
            return self._add_status_info(error_result)
    
    def scrape_hashtag(self, hashtag: str, limit: int = 10) -> Dict[str, Any]:
        """
        Scrape posts from a hashtag
        
        Args:
            hashtag: Hashtag name (without #)
            limit: Maximum number of posts to scrape
            
        Returns:
            Dictionary containing scraped posts and metadata
        """
        try:
            result = self.scraper.scrape_hashtag_posts(hashtag, max_posts=limit)
            return self._add_status_info(result)
        except Exception as e:
            error_result = {
                'error': f'Failed to scrape hashtag #{hashtag}: {str(e)}',
                'hashtag': hashtag,
                'scraped_count': 0,
                'posts': []
            }
            return self._add_status_info(error_result)
    
    def scrape_post(self, post_url: str) -> Dict[str, Any]:
        """
        Scrape a specific Instagram post
        
        Args:
            post_url: Instagram post URL
            
        Returns:
            Dictionary containing post data and comments
        """
        try:
            # Extract shortcode from Instagram URL
            if '/p/' in post_url:
                shortcode = post_url.split('/p/')[1].split('/')[0]
            else:
                error_result = {'error': 'Invalid Instagram post URL'}
                return self._add_status_info(error_result)
            
            comments = self.scraper.get_post_comments(shortcode, max_comments=50)
            
            result = {
                'shortcode': shortcode,
                'url': post_url,
                'comments': comments,
                'comment_count': len(comments),
                'scraped_at': self.scraper._get_current_timestamp() if hasattr(self.scraper, '_get_current_timestamp') else ''
            }
            return self._add_status_info(result)
        except Exception as e:
            error_result = {
                'error': f'Failed to scrape post {post_url}: {str(e)}',
                'url': post_url,
                'comments': [],
                'comment_count': 0
            }
            return self._add_status_info(error_result)
    
    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for Instagram users
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of user data dictionaries
        """
        try:
            return self.scraper.search_users(query, limit=limit)
        except Exception as e:
            return []
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """
        Get information about a specific Instagram user
        
        Args:
            username: Instagram username
            
        Returns:
            Dictionary containing user information
        """
        try:
            result = self.scraper.get_user_info(username)
            return self._add_status_info(result)
        except Exception as e:
            error_result = {
                'error': f'Failed to get user info for {username}: {str(e)}',
                'username': username
            }
            return self._add_status_info(error_result)
    
    def get_scraping_status(self) -> Dict[str, Any]:
        """
        Get current Instagram scraping configuration and status
        
        Returns:
            Dictionary containing scraping status and configuration info
        """
        import os
        from datetime import datetime
        
        # Check environment variables
        has_username = bool(os.environ.get('INSTAGRAM_USERNAME')) and os.environ.get('INSTAGRAM_USERNAME') != 'your_instagram_username'
        has_password = bool(os.environ.get('INSTAGRAM_PASSWORD')) and os.environ.get('INSTAGRAM_PASSWORD') != 'your_instagram_password'
        has_client_id = bool(os.environ.get('INSTAGRAM_CLIENT_ID')) and os.environ.get('INSTAGRAM_CLIENT_ID') != 'your_instagram_client_id'
        has_access_token = bool(os.environ.get('INSTAGRAM_ACCESS_TOKEN')) and os.environ.get('INSTAGRAM_ACCESS_TOKEN') != 'your_instagram_access_token'
        
        return {
            'status': 'configured' if self.is_using_real_api else 'not_configured',
            'api_client_initialized': self.is_using_real_api,
            'credentials_configured': {
                'username': has_username,
                'password': has_password,
                'client_id': has_client_id,
                'access_token': has_access_token
            },
            'data_mode': 'real_api' if self.is_using_real_api else 'mock_data',
            'message': 'Instagram API ready for scraping' if self.is_using_real_api else 'Configure Instagram credentials in .env file to enable real scraping',
            'timestamp': datetime.now().isoformat(),
            'dependencies': {
                'instagrapi_installed': True  # We checked this earlier
            },
            'setup_instructions': {
                'step1': 'Set INSTAGRAM_USERNAME in .env file',
                'step2': 'Set INSTAGRAM_PASSWORD in .env file',
                'note': 'Use a dedicated Instagram account for scraping to avoid issues with your main account'
            } if not self.is_using_real_api else None
        }


# Global service instance
instagram_service = InstagramScraperService()

def get_instagram_service():
    """Get the global Instagram service instance"""
    return instagram_service