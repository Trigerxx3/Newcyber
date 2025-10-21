"""
Production-ready OSINT tools service
Works without requiring Spiderfoot web UI or subprocess calls
"""
import logging
import requests
import time
from typing import Dict, List
from pathlib import Path

logger = logging.getLogger(__name__)

class ProductionOSINTService:
    """
    Production-ready OSINT service that works in any deployment environment
    Uses only HTTP APIs and doesn't rely on local tools
    """
    
    def __init__(self):
        self.use_local_tools = self._check_local_tools_available()
        
    def _check_local_tools_available(self) -> bool:
        """Check if local tools are available (for local development)"""
        try:
            # Check if we're in a local environment with tools installed
            tools_dir = Path(__file__).parent.parent.parent / "osint_tools"
            sherlock_exists = (tools_dir / "sherlock" / "sherlock_project" / "sherlock.py").exists()
            
            if sherlock_exists:
                logger.info("Local OSINT tools detected - using enhanced mode")
                return True
            else:
                logger.info("Running in production mode - using API-only mode")
                return False
        except Exception as e:
            logger.warning(f"Could not detect local tools: {e}")
            return False
    
    def investigate_user(self, username: str, platform: str = None) -> Dict:
        """
        Investigate a user using production-safe methods
        Works in any deployment environment
        """
        try:
            if self.use_local_tools:
                # Local development - use full tools
                from .osint_tools import OSINTToolsService
                logger.info("Using local OSINT tools (Sherlock + Spiderfoot)")
                
                service = OSINTToolsService()
                results = service.comprehensive_username_investigation(username, platform)
                
                return {
                    'status': 'success',
                    'data': self._format_results(results, username)
                }
            else:
                # Production - use API-only methods
                logger.info("Using production API-only investigation")
                results = self._api_only_investigation(username, platform)
                
                return {
                    'status': 'success',
                    'data': results
                }
                
        except Exception as e:
            logger.error(f"Investigation failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _api_only_investigation(self, username: str, platform: str) -> Dict:
        """
        API-only investigation that works in any environment
        Uses only HTTP requests - no local tools required
        """
        profiles = []
        tools_used = []
        
        # Method 1: URL pattern checking (always works)
        url_check_profiles = self._check_common_platforms(username)
        profiles.extend(url_check_profiles)
        tools_used.append('url_checker')
        
        # Method 2: Public API checks (no auth required)
        api_profiles = self._check_public_apis(username)
        profiles.extend(api_profiles)
        tools_used.append('public_apis')
        
        # Remove duplicates
        unique_profiles = self._deduplicate_profiles(profiles)
        
        return {
            'username': username,
            'platform': platform or 'Unknown',
            'linkedProfiles': unique_profiles,
            'totalProfilesFound': len(unique_profiles),
            'toolsUsed': tools_used,
            'riskLevel': self._calculate_risk_level(len(unique_profiles)),
            'confidenceLevel': 'medium',
            'summary': f"Found {len(unique_profiles)} potential profiles for username '{username}' using production-safe methods",
            'timestamp': time.time(),
            'rawResults': {
                'url_check_results': {'profiles': url_check_profiles, 'status': 'success'},
                'api_check_results': {'profiles': api_profiles, 'status': 'success'}
            }
        }
    
    def _check_common_platforms(self, username: str) -> List[Dict]:
        """Check common platforms using URL patterns"""
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/@{username}',
            'TikTok': f'https://tiktok.com/@{username}',
            'Pinterest': f'https://pinterest.com/{username}',
            'Medium': f'https://medium.com/@{username}',
            'SoundCloud': f'https://soundcloud.com/{username}',
        }
        
        profiles = []
        
        for platform, url in platforms.items():
            try:
                # Quick HEAD request to check if URL exists
                response = requests.head(url, timeout=3, allow_redirects=True, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code in [200, 301, 302]:
                    profiles.append({
                        'platform': platform,
                        'url': url,
                        'status': 'found',
                        'source': 'url_check',
                        'verified': True
                    })
                    logger.info(f"Found: {platform} - {url}")
                    
            except Exception as e:
                logger.debug(f"Platform {platform} check failed: {e}")
                continue
            
            time.sleep(0.1)  # Rate limiting
        
        return profiles
    
    def _check_public_apis(self, username: str) -> List[Dict]:
        """Check public APIs that don't require authentication"""
        profiles = []
        
        # GitHub API (no auth required for basic info)
        try:
            response = requests.get(
                f'https://api.github.com/users/{username}',
                timeout=5,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                profiles.append({
                    'platform': 'GitHub',
                    'url': data.get('html_url', f'https://github.com/{username}'),
                    'status': 'found',
                    'source': 'github_api',
                    'verified': True,
                    'additional_info': {
                        'name': data.get('name'),
                        'bio': data.get('bio'),
                        'repos': data.get('public_repos'),
                        'followers': data.get('followers')
                    }
                })
                logger.info(f"GitHub API: Found user {username}")
                
        except Exception as e:
            logger.debug(f"GitHub API check failed: {e}")
        
        return profiles
    
    def _deduplicate_profiles(self, profiles: List[Dict]) -> List[Dict]:
        """Remove duplicate profiles based on URL"""
        seen_urls = set()
        unique_profiles = []
        
        for profile in profiles:
            url = profile.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_profiles.append(profile)
        
        return unique_profiles
    
    def _calculate_risk_level(self, profile_count: int) -> str:
        """Calculate risk level based on profile count"""
        if profile_count == 0:
            return 'Low'
        elif profile_count <= 3:
            return 'Low'
        elif profile_count <= 7:
            return 'Medium'
        elif profile_count <= 15:
            return 'High'
        else:
            return 'Critical'
    
    def _format_results(self, results: Dict, username: str) -> Dict:
        """Format results from local tools to match API format"""
        from .osint_handler import OSINTHandler
        
        # Log tool statuses for debugging
        logger.info(f"Tool statuses from investigation: {results.get('tool_statuses', {})}")
        logger.info(f"Sherlock results status: {results.get('sherlock_results', {}).get('status')}")
        logger.info(f"Spiderfoot results status: {results.get('spiderfoot_results', {}).get('status')}")
        logger.info(f"Fallback results status: {results.get('fallback_results', {}).get('status')}")
        
        handler = OSINTHandler()
        return handler._format_investigation_results(results, username)


# Singleton instance
_production_service = None

def get_production_osint_service():
    """Get or create the production OSINT service"""
    global _production_service
    if _production_service is None:
        _production_service = ProductionOSINTService()
    return _production_service
