import logging
import json
from datetime import datetime
from typing import Dict, List, Optional
import threading
import time
from .osint_tools import OSINTToolsService

logger = logging.getLogger(__name__)

class OSINTHandler:
    """Enhanced OSINT handler using real tools"""
    
    def __init__(self):
        self.available_sources = {
            'social_media': ['twitter', 'facebook', 'instagram', 'linkedin'],
            'search_engines': ['google', 'bing', 'duckduckgo'],
            'news_sources': ['reuters', 'ap', 'bbc', 'cnn'],
            'dark_web': ['tor', 'i2p', 'freenet'],
            'forums': ['reddit', '4chan', 'hackernews'],
            'databases': ['whois', 'dns', 'ssl_certificates']
        }
        
        # Active monitoring tasks
        self.monitoring_tasks = {}
        self.monitoring_lock = threading.Lock()
        
        # Initialize OSINT tools service
        self.osint_tools = OSINTToolsService()
    
    def search(self, query: str, search_type: str = 'general') -> Dict:
        """
        Perform OSINT search across multiple sources
        
        Args:
            query: Search query
            search_type: Type of search (general, threat, person, organization)
            
        Returns:
            Dictionary containing search results
        """
        try:
            logger.info(f"Starting OSINT search for query: {query}, type: {search_type}")
            
            results = {
                'query': query,
                'search_type': search_type,
                'timestamp': datetime.now().isoformat(),
                'sources_searched': [],
                'results': {},
                'summary': {}
            }
            
            # Determine which sources to search based on search type
            sources_to_search = self._get_sources_for_type(search_type)
            
            for source_category, sources in sources_to_search.items():
                for source in sources:
                    try:
                        source_results = self._search_source(source, query, search_type)
                        if source_results:
                            results['results'][source] = source_results
                            results['sources_searched'].append(source)
                    except Exception as e:
                        logger.error(f"Error searching {source}: {e}")
                        results['results'][source] = {
                            'error': str(e),
                            'status': 'failed'
                        }
            
            # Generate summary
            results['summary'] = self._generate_search_summary(results)
            
            logger.info(f"OSINT search completed. Found results from {len(results['sources_searched'])} sources")
            return results
            
        except Exception as e:
            logger.error(f"Error in OSINT search: {e}")
            return {
                'query': query,
                'search_type': search_type,
                'error': str(e),
                'status': 'failed'
            }
    
    def _get_sources_for_type(self, search_type: str) -> Dict:
        """Get appropriate sources for search type"""
        if search_type == 'threat':
            return {
                'social_media': ['twitter', 'reddit'],
                'forums': ['4chan', 'hackernews'],
                'dark_web': ['tor']
            }
        elif search_type == 'person':
            return {
                'social_media': ['twitter', 'facebook', 'linkedin'],
                'search_engines': ['google', 'bing'],
                'databases': ['whois']
            }
        elif search_type == 'organization':
            return {
                'search_engines': ['google', 'bing'],
                'news_sources': ['reuters', 'ap', 'bbc'],
                'databases': ['whois', 'ssl_certificates']
            }
        else:  # general
            return self.available_sources
    
    def _search_source(self, source: str, query: str, search_type: str) -> Optional[Dict]:
        """Search a specific source"""
        # This would typically integrate with actual APIs or scraping tools
        # For now, return mock data
        
        if source in ['twitter', 'facebook', 'instagram']:
            return self._mock_social_media_search(source, query)
        elif source in ['google', 'bing', 'duckduckgo']:
            return self._mock_search_engine_search(source, query)
        elif source in ['reuters', 'ap', 'bbc', 'cnn']:
            return self._mock_news_search(source, query)
        elif source in ['tor', 'i2p']:
            return self._mock_dark_web_search(source, query)
        elif source in ['reddit', '4chan', 'hackernews']:
            return self._mock_forum_search(source, query)
        elif source in ['whois', 'dns', 'ssl_certificates']:
            return self._mock_database_search(source, query)
        else:
            return {
                'status': 'not_implemented',
                'message': f'Search for {source} not implemented'
            }
    
    def _mock_social_media_search(self, platform: str, query: str) -> Dict:
        """Mock social media search results"""
        return {
            'platform': platform,
            'query': query,
            'posts': [
                {
                    'id': f'{platform}_post_1',
                    'content': f'Sample post about {query}',
                    'author': f'user_{platform}',
                    'timestamp': datetime.now().isoformat(),
                    'engagement': {'likes': 10, 'shares': 5}
                }
            ],
            'total_posts': 1,
            'status': 'completed'
        }
    
    def _mock_search_engine_search(self, engine: str, query: str) -> Dict:
        """Mock search engine results"""
        return {
            'engine': engine,
            'query': query,
            'results': [
                {
                    'title': f'Search result for {query}',
                    'url': f'https://example.com/{query}',
                    'snippet': f'This is a sample search result for {query}',
                    'rank': 1
                }
            ],
            'total_results': 1,
            'status': 'completed'
        }
    
    def _mock_news_search(self, source: str, query: str) -> Dict:
        """Mock news search results"""
        return {
            'source': source,
            'query': query,
            'articles': [
                {
                    'title': f'News article about {query}',
                    'url': f'https://{source}.com/article/{query}',
                    'summary': f'This is a sample news article about {query}',
                    'published_date': datetime.now().isoformat()
                }
            ],
            'total_articles': 1,
            'status': 'completed'
        }
    
    def _mock_dark_web_search(self, network: str, query: str) -> Dict:
        """Mock dark web search results"""
        return {
            'network': network,
            'query': query,
            'results': [
                {
                    'title': f'Dark web content about {query}',
                    'url': f'http://example.onion/{query}',
                    'content': f'Sample dark web content for {query}',
                    'found_date': datetime.now().isoformat()
                }
            ],
            'total_results': 1,
            'status': 'completed'
        }
    
    def _mock_forum_search(self, forum: str, query: str) -> Dict:
        """Mock forum search results"""
        return {
            'forum': forum,
            'query': query,
            'threads': [
                {
                    'title': f'Forum thread about {query}',
                    'url': f'https://{forum}.com/thread/{query}',
                    'author': f'user_{forum}',
                    'replies': 5,
                    'created_date': datetime.now().isoformat()
                }
            ],
            'total_threads': 1,
            'status': 'completed'
        }
    
    def _mock_database_search(self, database: str, query: str) -> Dict:
        """Mock database search results"""
        return {
            'database': database,
            'query': query,
            'records': [
                {
                    'record_type': 'domain',
                    'value': f'{query}.com',
                    'details': f'Sample {database} record for {query}',
                    'last_updated': datetime.now().isoformat()
                }
            ],
            'total_records': 1,
            'status': 'completed'
        }
    
    def _generate_search_summary(self, results: Dict) -> Dict:
        """Generate summary of search results"""
        total_sources = len(results['sources_searched'])
        successful_sources = len([r for r in results['results'].values() if r.get('status') == 'completed'])
        
        return {
            'total_sources_searched': total_sources,
            'successful_searches': successful_sources,
            'failed_searches': total_sources - successful_sources,
            'total_results_found': sum(len(r.get('results', [])) for r in results['results'].values() if isinstance(r.get('results'), list))
        }
    
    def analyze_threats(self, search_results: Dict) -> Dict:
        """
        Analyze OSINT results for threats
        
        Args:
            search_results: Results from OSINT search
            
        Returns:
            Dictionary containing threat analysis
        """
        try:
            analysis = {
                'threat_level': 'low',
                'findings': [],
                'recommendations': [],
                'risk_factors': []
            }
            
            # Analyze results for threat indicators
            threat_indicators = self._extract_threat_indicators(search_results)
            
            if threat_indicators:
                analysis['threat_level'] = self._assess_threat_level(threat_indicators)
                analysis['findings'] = threat_indicators
                analysis['recommendations'] = self._generate_recommendations(threat_indicators)
                analysis['risk_factors'] = self._identify_risk_factors(threat_indicators)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing threats: {e}")
            return {
                'threat_level': 'unknown',
                'error': str(e)
            }
    
    def _extract_threat_indicators(self, results: Dict) -> List[Dict]:
        """Extract threat indicators from search results"""
        indicators = []
        
        # This would implement actual threat detection logic
        # For now, return mock indicators
        if results.get('results'):
            indicators.append({
                'type': 'suspicious_activity',
                'source': 'social_media',
                'description': 'Potential suspicious activity detected',
                'confidence': 'medium'
            })
        
        return indicators
    
    def _assess_threat_level(self, indicators: List[Dict]) -> str:
        """Assess overall threat level based on indicators"""
        if not indicators:
            return 'low'
        
        # Simple assessment based on number of indicators
        if len(indicators) >= 5:
            return 'high'
        elif len(indicators) >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_recommendations(self, indicators: List[Dict]) -> List[str]:
        """Generate recommendations based on threat indicators"""
        recommendations = []
        
        for indicator in indicators:
            if indicator['type'] == 'suspicious_activity':
                recommendations.append('Monitor for additional suspicious activity')
                recommendations.append('Consider escalating to security team')
        
        return recommendations
    
    def _identify_risk_factors(self, indicators: List[Dict]) -> List[str]:
        """Identify risk factors from threat indicators"""
        risk_factors = []
        
        for indicator in indicators:
            risk_factors.append(f"{indicator['type']} from {indicator['source']}")
        
        return risk_factors
    
    def get_available_sources(self) -> Dict:
        """Get list of available OSINT sources"""
        return self.available_sources
    
    def start_monitoring(self, keywords: List[str], interval: int = 3600) -> str:
        """
        Start continuous monitoring for keywords
        
        Args:
            keywords: List of keywords to monitor
            interval: Monitoring interval in seconds
            
        Returns:
            Monitoring task ID
        """
        monitoring_id = str(uuid.uuid4())
        
        with self.monitoring_lock:
            self.monitoring_tasks[monitoring_id] = {
                'keywords': keywords,
                'interval': interval,
                'active': True,
                'last_run': None,
                'results': []
            }
        
        # Start monitoring thread
        thread = threading.Thread(
            target=self._monitoring_worker,
            args=(monitoring_id, keywords, interval),
            daemon=True
        )
        thread.start()
        
        logger.info(f"Started monitoring for keywords: {keywords}, ID: {monitoring_id}")
        return monitoring_id
    
    def stop_monitoring(self, monitoring_id: str):
        """Stop monitoring task"""
        with self.monitoring_lock:
            if monitoring_id in self.monitoring_tasks:
                self.monitoring_tasks[monitoring_id]['active'] = False
                logger.info(f"Stopped monitoring task: {monitoring_id}")
    
    def _monitoring_worker(self, monitoring_id: str, keywords: List[str], interval: int):
        """Background worker for continuous monitoring"""
        while True:
            with self.monitoring_lock:
                task = self.monitoring_tasks.get(monitoring_id)
                if not task or not task['active']:
                    break
            
            try:
                # Perform search for each keyword
                for keyword in keywords:
                    results = self.search(keyword, 'threat')
                    task['results'].append({
                        'keyword': keyword,
                        'timestamp': datetime.now().isoformat(),
                        'results': results
                    })
                
                task['last_run'] = datetime.now().isoformat()
                logger.info(f"Monitoring run completed for {monitoring_id}")
                
            except Exception as e:
                logger.error(f"Error in monitoring worker {monitoring_id}: {e}")
            
            # Wait for next interval
            time.sleep(interval)  # Wait for next interval
    
    def investigate_user(self, username: str, platform: str = None) -> Dict:
        """Investigate a user across multiple platforms"""
        try:
            # Use the OSINT tools service
            osint_tools = OSINTToolsService()
            results = osint_tools.comprehensive_username_investigation(username, platform)
            
            # Format results properly with actual URLs
            formatted_results = self._format_investigation_results(results, username)
            
            return {
                'status': 'success',
                'data': formatted_results
            }
        except Exception as e:
            logger.error(f"User investigation failed: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

    def _format_investigation_results(self, results: Dict, username: str) -> Dict:
        """Format investigation results with proper URLs"""
        linked_profiles = []
        
        # Parse Sherlock results if available
        if 'sherlock_output' in results:
            sherlock_profiles = self._parse_sherlock_results(results['sherlock_output'], username)
            linked_profiles.extend(sherlock_profiles)
        
        # Parse fallback results if available
        if 'fallback_results' in results:
            fallback_profiles = results['fallback_results'].get('profiles', [])
            linked_profiles.extend(fallback_profiles)
        
        # Parse profiles_found if available
        if 'profiles_found' in results:
            linked_profiles.extend(results['profiles_found'])
        
        # Parse SpiderFoot results if available
        if 'spiderfoot_results' in results:
            spiderfoot_profiles = self._parse_spiderfoot_results(results['spiderfoot_results'])
            linked_profiles.extend(spiderfoot_profiles)
        
        # Remove duplicates based on URL
        unique_profiles = []
        seen_urls = set()
        for profile in linked_profiles:
            url = profile.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_profiles.append(profile)
        
        return {
            'username': username,
            'platform': results.get('platform', 'Unknown'),
            'linkedProfiles': unique_profiles,
            'totalProfilesFound': len(unique_profiles),
            'toolsUsed': results.get('tools_used', []),
            'riskLevel': self._calculate_risk_level(unique_profiles),
            'confidenceLevel': self._calculate_confidence_level(unique_profiles),
            'summary': f"Found {len(unique_profiles)} potential profiles for username '{username}'",
            'timestamp': datetime.now().isoformat(),
            'rawResults': results
        }

    def _parse_sherlock_results(self, sherlock_output: str, username: str) -> List[Dict]:
        """Parse Sherlock output to extract actual URLs"""
        profiles = []
        
        lines = sherlock_output.split('\n')
        for line in lines:
            line = line.strip()
            
            # Look for successful matches in Sherlock output
            if '[+]' in line and 'http' in line:
                try:
                    # Extract platform and URL from line like: "[+] GitHub: https://github.com/username"
                    parts = line.split(': ', 1)
                    if len(parts) >= 2:
                        platform = parts[0].replace('[+]', '').strip()
                        url = parts[1].strip()
                        
                        if url.startswith(('http://', 'https://')):
                            profiles.append({
                                'platform': platform,
                                'url': url,
                                'status': 'found',
                                'source': 'sherlock'
                            })
                except Exception as e:
                    logger.warning(f"Failed to parse Sherlock line: {line} - {e}")
                    continue
        
        return profiles

    def _parse_spiderfoot_results(self, spiderfoot_results: Dict) -> List[Dict]:
        """Parse SpiderFoot results to extract profile information"""
        profiles = []
        
        try:
            if isinstance(spiderfoot_results, dict):
                findings = spiderfoot_results.get('findings', [])
                
                for finding in findings:
                    if finding.get('type') == 'account':
                        # Extract platform and URL from SpiderFoot data
                        data = finding.get('data', '')
                        if 'http' in data:
                            # Try to extract URL from the finding data
                            import re
                            url_match = re.search(r'https?://[^\s]+', data)
                            if url_match:
                                url = url_match.group()
                                platform = self._extract_platform_from_url(url)
                                
                                profiles.append({
                                    'platform': platform,
                                    'url': url,
                                    'status': 'found',
                                    'source': 'spiderfoot',
                                    'confidence': finding.get('confidence', 'medium')
                                })
        except Exception as e:
            logger.warning(f"Failed to parse SpiderFoot results: {e}")
        
        return profiles

    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            # Extract main platform name
            if 'github.com' in domain:
                return 'GitHub'
            elif 'twitter.com' in domain or 'x.com' in domain:
                return 'Twitter/X'
            elif 'instagram.com' in domain:
                return 'Instagram'
            elif 'linkedin.com' in domain:
                return 'LinkedIn'
            elif 'facebook.com' in domain:
                return 'Facebook'
            elif 'reddit.com' in domain:
                return 'Reddit'
            else:
                # Capitalize first letter of domain name
                return domain.split('.')[0].capitalize()
        except:
            return 'Unknown Platform'

    def _calculate_risk_level(self, profiles: List[Dict]) -> str:
        """Calculate risk level based on found profiles"""
        profile_count = len(profiles)
        
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

    def _calculate_confidence_level(self, profiles: List[Dict]) -> str:
        """Calculate confidence level based on profile diversity and sources"""
        if not profiles:
            return 'low'
        
        profile_count = len(profiles)
        unique_sources = len(set(p.get('source', 'unknown') for p in profiles))
        
        if profile_count >= 5 and unique_sources >= 2:
            return 'high'
        elif profile_count >= 2:
            return 'medium'
        else:
            return 'low'
