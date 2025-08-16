import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

class WebScraper:
    """Web scraping service for collecting data from various sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.rate_limit_delay = 1  # seconds between requests
    
    def scrape_url(self, url: str, selectors: Optional[Dict] = None) -> Dict:
        """
        Scrape content from a URL
        
        Args:
            url: URL to scrape
            selectors: CSS selectors for specific content extraction
            
        Returns:
            Dictionary containing scraped data
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Add rate limiting
            time.sleep(self.rate_limit_delay)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Default selectors if none provided
            if not selectors:
                selectors = {
                    'title': 'title',
                    'content': 'body',
                    'links': 'a[href]'
                }
            
            scraped_data = {
                'url': url,
                'title': self._extract_text(soup, selectors.get('title')),
                'content': self._extract_text(soup, selectors.get('content')),
                'links': self._extract_links(soup, selectors.get('links')),
                'metadata': {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'content_length': len(response.content)
                }
            }
            
            logger.info(f"Successfully scraped {url}")
            return scraped_data
            
        except requests.RequestException as e:
            logger.error(f"Request error scraping {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'status': 'failed'
            }
        except Exception as e:
            logger.error(f"Unexpected error scraping {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'status': 'failed'
            }
    
    def scrape_multiple_urls(self, urls: List[str], selectors: Optional[Dict] = None) -> List[Dict]:
        """
        Scrape multiple URLs
        
        Args:
            urls: List of URLs to scrape
            selectors: CSS selectors for content extraction
            
        Returns:
            List of scraped data dictionaries
        """
        results = []
        for url in urls:
            result = self.scrape_url(url, selectors)
            results.append(result)
        return results
    
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract text content using CSS selector"""
        if not selector:
            return ""
        
        try:
            elements = soup.select(selector)
            if elements:
                return ' '.join([elem.get_text(strip=True) for elem in elements])
            return ""
        except Exception as e:
            logger.error(f"Error extracting text with selector {selector}: {e}")
            return ""
    
    def _extract_links(self, soup: BeautifulSoup, selector: str) -> List[str]:
        """Extract links using CSS selector"""
        if not selector:
            return []
        
        try:
            elements = soup.select(selector)
            links = []
            for element in elements:
                href = element.get('href')
                if href:
                    links.append(href)
            return links
        except Exception as e:
            logger.error(f"Error extracting links with selector {selector}: {e}")
            return []
    
    def scrape_social_media(self, platform: str, query: str) -> Dict:
        """
        Scrape social media content (placeholder for API integration)
        
        Args:
            platform: Social media platform (twitter, facebook, etc.)
            query: Search query
            
        Returns:
            Dictionary containing scraped social media data
        """
        # This would typically integrate with social media APIs
        # For now, return mock data
        return {
            'platform': platform,
            'query': query,
            'posts': [],
            'status': 'not_implemented',
            'message': f'Social media scraping for {platform} not implemented'
        }
    
    def scrape_dark_web(self, query: str) -> Dict:
        """
        Scrape dark web content (placeholder for specialized tools)
        
        Args:
            query: Search query
            
        Returns:
            Dictionary containing scraped dark web data
        """
        # This would typically use specialized dark web scraping tools
        # For now, return mock data
        return {
            'query': query,
            'results': [],
            'status': 'not_implemented',
            'message': 'Dark web scraping not implemented'
        }
    
    def validate_url(self, url: str) -> bool:
        """Validate if URL is accessible and valid"""
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except Exception:
            return False
    
    def set_rate_limit(self, delay: float):
        """Set rate limiting delay between requests"""
        self.rate_limit_delay = delay
        logger.info(f"Rate limit set to {delay} seconds")
    
    def close(self):
        """Close the session"""
        self.session.close() 