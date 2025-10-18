import subprocess
import json
import os
import tempfile
import logging
import time
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class OSINTToolsService:
    """Service for running real OSINT tools like Sherlock and Spiderfoot"""
    
    def __init__(self):
        self.tools_dir = Path(__file__).parent.parent.parent / "osint_tools"  # Go up one more level
        self.sherlock_path = self.tools_dir / "sherlock" / "sherlock_project" / "sherlock.py"
        self.spiderfoot_path = self.tools_dir / "spiderfoot" / "sf.py"
        
        # Alternative paths if installed globally
        if not self.sherlock_path.exists():
            # Check if sherlock is installed globally
            try:
                result = subprocess.run(['which', 'sherlock'], capture_output=True, text=True)
                if result.returncode == 0:
                    self.sherlock_path = Path(result.stdout.strip())
            except:
                pass
        
        logger.info(f"Sherlock path: {self.sherlock_path}")
        logger.info(f"Spiderfoot path: {self.spiderfoot_path}")
        
    def run_sherlock(self, username: str, timeout: int = 120) -> Dict:
        """Run Sherlock to find username across social networks"""
        try:
            if not self.sherlock_path.exists():
                # Try global sherlock command
                try:
                    cmd = ['sherlock', username, '--timeout', str(timeout), '--print-all']
                    logger.info(f"Running global Sherlock for username: {username}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
                    
                    return self._parse_sherlock_output(result.stdout, username)
                except:
                    return {
                        'error': 'Sherlock not found',
                        'message': 'Sherlock is not installed or not in PATH'
                    }
            
            # Use local sherlock installation
            cmd = ['python3', str(self.sherlock_path), username, '--timeout', str(timeout), '--print-all']
            
            logger.info(f"Running Sherlock for username: {username}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 30,
                cwd=self.sherlock_path.parent
            )
            
            return self._parse_sherlock_output(result.stdout, username)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Sherlock timeout for username: {username}")
            return {
                'error': 'timeout',
                'message': f'Sherlock timed out after {timeout} seconds'
            }
        except Exception as e:
            logger.error(f"Sherlock error: {e}")
            return {
                'error': str(e),
                'message': 'Failed to run Sherlock'
            }
    
    def _parse_sherlock_output(self, output: str, username: str) -> Dict:
        """Parse Sherlock output and extract valid profiles"""
        found_profiles = []
        
        lines = output.split('\n')
        for line in lines:
            line = line.strip()
            if '[+]' in line and 'http' in line:
                # Extract platform and URL from Sherlock output
                parts = line.split(': ')
                if len(parts) >= 2:
                    platform = parts[0].replace('[+]', '').strip()
                    url = parts[1].strip()
                    
                    # Validate URL format
                    if url.startswith(('http://', 'https://')):
                        found_profiles.append({
                            'platform': platform,
                            'url': url,
                            'status': 'found',
                            'verified': False  # Mark as unverified initially
                        })
        
        return {
            'found_profiles': found_profiles,
            'total_found': len(found_profiles),
            'status': 'success'
        }
    
    def run_spiderfoot(self, target: str, scan_type: str = 'USERNAME') -> Dict:
        """Run Spiderfoot for comprehensive OSINT gathering"""
        try:
            if not self.spiderfoot_path.exists():
                return {
                    'error': 'Spiderfoot not installed',
                    'message': 'Spiderfoot not found at expected path'
                }
            
            # Create unique scan name
            scan_name = f"investigation_{target}_{int(time.time())}"
            
            # Run Spiderfoot with basic modules for username investigation
            cmd = [
                'python', str(self.spiderfoot_path),
                '-s', target,
                '-t', scan_type,
                '-m', 'sfp_accounts,sfp_social,sfp_github',
                '-q'  # Quiet mode
            ]
            
            logger.info(f"Running Spiderfoot for target: {target}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,  # 1 minute timeout
                cwd=str(self.spiderfoot_path.parent)
            )
            
            return {
                'tool': 'spiderfoot',
                'target': target,
                'status': 'completed',
                'findings': self._parse_spiderfoot_output(result.stdout),
                'raw_output': result.stdout,
                'scan_name': scan_name
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Spiderfoot timeout for target: {target}")
            return {
                'error': 'timeout',
                'message': 'Spiderfoot scan timed out'
            }
        except Exception as e:
            logger.error(f"Spiderfoot error: {e}")
            return {
                'error': str(e),
                'message': 'Failed to run Spiderfoot'
            }
    
    def _parse_spiderfoot_output(self, output: str) -> List[Dict]:
        """Parse Spiderfoot output for findings"""
        findings = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'ACCOUNT' in line or 'SOCIAL' in line:
                findings.append({
                    'type': 'account',
                    'data': line,
                    'confidence': 'medium'
                })
        
        return findings

    def run_spiderfoot_username_scan(self, username: str) -> Dict:
        """Run SpiderFoot specifically for username investigation"""
        # Use API-based approach instead of CLI (more stable)
        try:
            from .spiderfoot_api import run_spiderfoot_via_api
            
            logger.info(f"Running SpiderFoot via API for: {username}")
            result = run_spiderfoot_via_api(username)
            
            if result['status'] == 'completed':
                logger.info(f"SpiderFoot API scan completed with {len(result.get('findings', []))} findings")
                return result
            else:
                logger.warning(f"SpiderFoot API scan failed: {result.get('error', 'Unknown error')}")
                return result
                
        except ImportError:
            logger.error("Spiderfoot API module not available")
            return {
                'tool': 'spiderfoot',
                'target': username,
                'status': 'error',
                'findings': [],
                'error': 'Spiderfoot API module not available'
            }
        except Exception as e:
            logger.error(f"SpiderFoot API error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'tool': 'spiderfoot',
                'target': username,
                'status': 'error',
                'findings': [],
                'error': str(e)
            }

    def _parse_spiderfoot_json_output(self, output: str) -> List[Dict]:
        """Parse SpiderFoot JSON output to extract findings"""
        findings = []
        
        try:
            # SpiderFoot outputs multiple JSON objects, one per line
            for line in output.strip().split('\n'):
                if line.strip():
                    try:
                        data = json.loads(line)
                        
                        # Extract relevant information
                        finding = {
                            'type': data.get('type', 'unknown'),
                            'data': data.get('data', ''),
                            'module': data.get('module', ''),
                            'confidence': data.get('confidence', 'medium'),
                            'timestamp': data.get('generated', ''),
                            'source_data': data.get('sourceData', '')
                        }
                        
                        # Categorize findings
                        if 'SOCIAL_MEDIA' in finding['type'] or 'ACCOUNT' in finding['type']:
                            finding['category'] = 'social_media'
                        elif 'EMAIL' in finding['type']:
                            finding['category'] = 'email'
                        elif 'BREACH' in finding['type'] or 'LEAKED' in finding['type']:
                            finding['category'] = 'data_breach'
                        elif 'PHONE' in finding['type']:
                            finding['category'] = 'phone'
                        else:
                            finding['category'] = 'other'
                        
                        findings.append(finding)
                        
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error parsing SpiderFoot output: {e}")
        
        return findings

    def get_spiderfoot_scan_results(self, scan_name: str) -> Dict:
        """Get results from a SpiderFoot scan"""
        try:
            # Try to read results from SpiderFoot database or output files
            results_path = self.spiderfoot_path.parent / 'results' / f"{scan_name}.json"
            
            if results_path.exists():
                with open(results_path, 'r') as f:
                    return json.load(f)
            else:
                return {'error': 'Results not found'}
            
        except Exception as e:
            logger.error(f"Error reading SpiderFoot results: {e}")
            return {'error': str(e)}

    def verify_profile_url(self, url: str, timeout: int = 10) -> bool:
        """Verify if a profile URL actually exists"""
        try:
            response = requests.head(url, timeout=timeout, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def comprehensive_username_investigation(self, username: str, platform: str = None) -> Dict:
        """Run comprehensive investigation using multiple methods"""
        results = {
            'username': username,
            'platform': platform or 'Unknown',
            'timestamp': time.time(),
            'tools_used': [],
            'profiles_found': [],
            'spiderfoot_findings': []
        }
        
        # Method 1: SpiderFoot scan (primary method)
        logger.info("Starting SpiderFoot username scan...")
        spiderfoot_results = self.run_spiderfoot_username_scan(username)
        results['spiderfoot_results'] = spiderfoot_results
        
        if 'error' not in spiderfoot_results:
            results['tools_used'].append('spiderfoot')
            results['spiderfoot_findings'] = spiderfoot_results.get('findings', [])
            
            # Extract profiles from SpiderFoot findings
            for finding in results['spiderfoot_findings']:
                if finding.get('category') == 'social_media':
                    profile_url = self._extract_url_from_finding(finding)
                    if profile_url:
                        results['profiles_found'].append({
                            'platform': self._extract_platform_from_url(profile_url),
                            'url': profile_url,
                            'status': 'found',
                            'source': 'spiderfoot',
                            'confidence': finding.get('confidence', 'medium'),
                            'module': finding.get('module', '')
                        })
        
        # Method 2: Fallback URL checking
        logger.info("Running fallback URL checks...")
        fallback_results = self.investigate_username_fallback(username)
        results['fallback_results'] = fallback_results
        results['tools_used'].append('fallback_api')
        results['profiles_found'].extend(fallback_results.get('profiles', []))
        
        # Method 3: Try Sherlock if available
        try:
            sherlock_results = self.run_sherlock_investigation(username)
            results['sherlock_results'] = sherlock_results
            if sherlock_results.get('status') == 'success':
                results['tools_used'].append('sherlock')
        except Exception as e:
            logger.warning(f"Sherlock failed: {e}")
            results['sherlock_results'] = {'error': 'Sherlock not available'}
        
        # Generate comprehensive summary
        results['summary'] = self._generate_comprehensive_summary(results)
        
        return results

    def _generate_comprehensive_summary(self, results: Dict) -> Dict:
        """Generate comprehensive summary of investigation"""
        total_profiles = len(results['profiles_found'])
        spiderfoot_findings = len(results['spiderfoot_findings'])
        tools_used = results['tools_used']
        
        # Categorize findings
        categories = {}
        for finding in results['spiderfoot_findings']:
            category = finding.get('category', 'other')
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_profiles_found': total_profiles,
            'spiderfoot_findings_count': spiderfoot_findings,
            'tools_used': tools_used,
            'finding_categories': categories,
            'risk_assessment': self._assess_risk_level(results),
            'recommendations': self._generate_recommendations(results)
        }

    def _assess_risk_level(self, results: Dict) -> str:
        """Assess risk level based on findings"""
        profile_count = len(results['profiles_found'])
        breach_findings = sum(1 for f in results['spiderfoot_findings'] if f.get('category') == 'data_breach')
        
        if breach_findings > 0:
            return 'High'
        elif profile_count > 10:
            return 'Medium-High'
        elif profile_count > 5:
            return 'Medium'
        else:
            return 'Low'

    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        profile_count = len(results['profiles_found'])
        breach_findings = sum(1 for f in results['spiderfoot_findings'] if f.get('category') == 'data_breach')
        
        if profile_count > 10:
            recommendations.append("Consider reducing online presence across multiple platforms")
        
        if breach_findings > 0:
            recommendations.append("Change passwords on affected accounts immediately")
            recommendations.append("Enable two-factor authentication on all accounts")
        
        if profile_count > 0:
            recommendations.append("Review privacy settings on all identified accounts")
            recommendations.append("Consider using different usernames for different purposes")
        
        return recommendations

    def run_sherlock_investigation(self, username: str) -> Dict:
        """Run Sherlock investigation and capture actual output"""
        try:
            if not self.sherlock_path.exists():
                return {'status': 'error', 'message': 'Sherlock not found'}
            
            # Run Sherlock with proper output capture
            cmd = [
                'python', 
                str(self.sherlock_path),
                username,
                '--print-found',  # Only print found profiles
                '--no-color',     # Remove color codes
                '--timeout', '5'
            ]
            
            logger.info(f"Running Sherlock command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.sherlock_path.parent),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'found_profiles': self._extract_urls_from_sherlock_output(result.stdout)
                }
            else:
                logger.error(f"Sherlock failed: {result.stderr}")
                return {
                    'status': 'error',
                    'message': f"Sherlock execution failed: {result.stderr}",
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'message': 'Sherlock investigation timed out'}
        except Exception as e:
            logger.error(f"Sherlock investigation error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _extract_urls_from_sherlock_output(self, output: str) -> List[Dict]:
        """Extract actual URLs from Sherlock output"""
        profiles = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if '[+]' in line and 'http' in line:
                try:
                    # Parse line format: "[+] Platform: https://platform.com/username"
                    parts = line.split(': ', 1)
                    if len(parts) >= 2:
                        platform = parts[0].replace('[+]', '').strip()
                        url = parts[1].strip()
                        
                        if url.startswith(('http://', 'https://')):
                            profiles.append({
                                'platform': platform,
                                'url': url,
                                'status': 'found'
                            })
                except Exception as e:
                    logger.warning(f"Failed to parse line: {line} - {e}")
                    continue
        
        return profiles

    def investigate_username_fallback(self, username: str) -> Dict:
        """Fallback method using public APIs and URL patterns"""
        profiles = []
        
        # Common social media platforms with predictable URLs
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/@{username}',
            'TikTok': f'https://tiktok.com/@{username}',
            'Pinterest': f'https://pinterest.com/{username}',
            'Tumblr': f'https://{username}.tumblr.com',
            'Medium': f'https://medium.com/@{username}',
            'DeviantArt': f'https://{username}.deviantart.com',
            'Behance': f'https://behance.net/{username}',
            'Dribbble': f'https://dribbble.com/{username}',
            'Flickr': f'https://flickr.com/people/{username}',
            'SoundCloud': f'https://soundcloud.com/{username}',
            'Spotify': f'https://open.spotify.com/user/{username}',
            'Twitch': f'https://twitch.tv/{username}',
            'Steam': f'https://steamcommunity.com/id/{username}',
            'Discord': f'https://discord.com/users/{username}',
            'Telegram': f'https://t.me/{username}'
        }
        
        # Check each platform
        for platform, url in platforms.items():
            try:
                if self.check_url_exists(url):
                    profiles.append({
                        'platform': platform,
                        'url': url,
                        'status': 'found',
                        'verified': True,
                        'source': 'url_check'
                    })
                    logger.info(f"Found profile: {platform} - {url}")
                time.sleep(0.1)  # Faster rate limiting
            except Exception as e:
                logger.debug(f"Error checking {platform}: {e}")
                continue
        
        # Try GitHub API for more detailed info
        try:
            github_info = self.check_github_api(username)
            if github_info:
                profiles.append(github_info)
        except Exception as e:
            logger.debug(f"GitHub API check failed: {e}")
        
        return {
            'profiles': profiles,
            'total_found': len(profiles),
            'method': 'fallback_url_check',
            'status': 'success'
        }

    def check_url_exists(self, url: str, timeout: int = 3) -> bool:
        """Check if a URL exists and returns a valid response"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            
            # Consider 200, 301, 302 as valid (profile exists)
            if response.status_code in [200, 301, 302]:
                return True
            
            # Some sites return 405 for HEAD requests, try GET
            if response.status_code == 405:
                response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
                return response.status_code == 200
                
            return False
            
        except requests.exceptions.RequestException:
            return False

    def check_github_api(self, username: str) -> Dict:
        """Check GitHub API for user information"""
        try:
            url = f'https://api.github.com/users/{username}'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'platform': 'GitHub (API)',
                    'url': data.get('html_url', f'https://github.com/{username}'),
                    'status': 'found',
                    'verified': True,
                    'source': 'github_api',
                    'additional_info': {
                        'name': data.get('name'),
                        'bio': data.get('bio'),
                        'public_repos': data.get('public_repos'),
                        'followers': data.get('followers'),
                        'created_at': data.get('created_at')
                    }
                }
        except Exception as e:
            logger.debug(f"GitHub API error: {e}")
        
        return None

    def _extract_url_from_finding(self, finding: Dict) -> str:
        """Extract URL from SpiderFoot finding"""
        data = finding.get('data', '')
        
        # Look for URLs in the data
        import re
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, data)
        
        if urls:
            return urls[0]
        
        return ''

    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform name from a URL"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        platform_map = {
            'github.com': 'GitHub',
            'twitter.com': 'Twitter',
            'instagram.com': 'Instagram',
            'linkedin.com': 'LinkedIn',
            'tiktok.com': 'TikTok',
            'pinterest.com': 'Pinterest',
            'tumblr.com': 'Tumblr',
            'medium.com': 'Medium',
            'deviantart.com': 'DeviantArt',
            'behance.net': 'Behance',
            'dribbble.com': 'Dribbble',
            'flickr.com': 'Flickr',
            'soundcloud.com': 'SoundCloud',
            'open.spotify.com': 'Spotify',
            'twitch.tv': 'Twitch',
            'steamcommunity.com': 'Steam',
            'discord.com': 'Discord',
            't.me': 'Telegram'
        }
        
        for domain_suffix, platform in platform_map.items():
            if domain.endswith(domain_suffix):
                return platform
        
        return 'Unknown Platform'

    def _generate_investigation_summary(self, results: Dict) -> Dict:
        """Generate summary from all tool results"""
        summary = {
            'total_profiles_found': 0,
            'platforms_found': [],
            'risk_indicators': [],
            'confidence_level': 'low'
        }
        
        # Process Sherlock results
        sherlock_profiles = results.get('sherlock_results', {}).get('found_profiles', [])
        summary['total_profiles_found'] += len(sherlock_profiles)
        summary['platforms_found'].extend([p['platform'] for p in sherlock_profiles])
        
        # Process Spiderfoot results
        spiderfoot_findings = results.get('spiderfoot_results', {}).get('findings', [])
        summary['total_profiles_found'] += len(spiderfoot_findings)
        
        # Determine confidence level
        if summary['total_profiles_found'] > 5:
            summary['confidence_level'] = 'high'
        elif summary['total_profiles_found'] > 2:
            summary['confidence_level'] = 'medium'
        
        # Remove duplicates
        summary['platforms_found'] = list(set(summary['platforms_found']))
        
        return summary

    def run_sherlock_investigation(self, username: str) -> Dict:
        """Run Sherlock investigation and capture actual output"""
        try:
            if not self.sherlock_path.exists():
                return {'status': 'error', 'message': 'Sherlock not found'}
            
            # Run Sherlock with proper output capture
            cmd = [
                'python', 
                str(self.sherlock_path),
                username,
                '--print-found',  # Only print found profiles
                '--no-color',     # Remove color codes
                '--timeout', '5'
            ]
            
            logger.info(f"Running Sherlock command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(self.sherlock_path.parent),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'output': result.stdout,
                    'stderr': result.stderr,
                    'found_profiles': self._extract_urls_from_sherlock_output(result.stdout)
                }
            else:
                logger.error(f"Sherlock failed: {result.stderr}")
                return {
                    'status': 'error',
                    'message': f"Sherlock execution failed: {result.stderr}",
                    'output': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'message': 'Sherlock investigation timed out'}
        except Exception as e:
            logger.error(f"Sherlock investigation error: {str(e)}")
            return {'status': 'error', 'message': str(e)}

    def _extract_urls_from_sherlock_output(self, output: str) -> List[Dict]:
        """Extract actual URLs from Sherlock output"""
        profiles = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if '[+]' in line and 'http' in line:
                try:
                    # Parse line format: "[+] Platform: https://platform.com/username"
                    parts = line.split(': ', 1)
                    if len(parts) >= 2:
                        platform = parts[0].replace('[+]', '').strip()
                        url = parts[1].strip()
                        
                        if url.startswith(('http://', 'https://')):
                            profiles.append({
                                'platform': platform,
                                'url': url,
                                'status': 'found'
                            })
                except Exception as e:
                    logger.warning(f"Failed to parse line: {line} - {e}")
                    continue
        
        return profiles

    def investigate_username_fallback(self, username: str) -> Dict:
        """Fallback method using public APIs and URL patterns"""
        profiles = []
        
        # Common social media platforms with predictable URLs
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/@{username}',
            'TikTok': f'https://tiktok.com/@{username}',
            'Pinterest': f'https://pinterest.com/{username}',
            'Tumblr': f'https://{username}.tumblr.com',
            'Medium': f'https://medium.com/@{username}',
            'DeviantArt': f'https://{username}.deviantart.com',
            'Behance': f'https://behance.net/{username}',
            'Dribbble': f'https://dribbble.com/{username}',
            'Flickr': f'https://flickr.com/people/{username}',
            'SoundCloud': f'https://soundcloud.com/{username}',
            'Spotify': f'https://open.spotify.com/user/{username}',
            'Twitch': f'https://twitch.tv/{username}',
            'Steam': f'https://steamcommunity.com/id/{username}',
            'Discord': f'https://discord.com/users/{username}',
            'Telegram': f'https://t.me/{username}'
        }
        
        # Check each platform
        for platform, url in platforms.items():
            try:
                if self.check_url_exists(url):
                    profiles.append({
                        'platform': platform,
                        'url': url,
                        'status': 'found',
                        'verified': True,
                        'source': 'url_check'
                    })
                    logger.info(f"Found profile: {platform} - {url}")
                time.sleep(0.1)  # Faster rate limiting
            except Exception as e:
                logger.debug(f"Error checking {platform}: {e}")
                continue
        
        # Try GitHub API for more detailed info
        try:
            github_info = self.check_github_api(username)
            if github_info:
                profiles.append(github_info)
        except Exception as e:
            logger.debug(f"GitHub API check failed: {e}")
        
        return {
            'profiles': profiles,
            'total_found': len(profiles),
            'method': 'fallback_url_check',
            'status': 'success'
        }

    def check_url_exists(self, url: str, timeout: int = 3) -> bool:
        """Check if a URL exists and returns a valid response"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
            
            # Consider 200, 301, 302 as valid (profile exists)
            if response.status_code in [200, 301, 302]:
                return True
            
            # Some sites return 405 for HEAD requests, try GET
            if response.status_code == 405:
                response = requests.get(url, timeout=timeout, headers=headers, allow_redirects=True)
                return response.status_code == 200
                
            return False
            
        except requests.exceptions.RequestException:
            return False

    def check_github_api(self, username: str) -> Dict:
        """Check GitHub API for user information"""
        try:
            url = f'https://api.github.com/users/{username}'
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'platform': 'GitHub (API)',
                    'url': data.get('html_url', f'https://github.com/{username}'),
                    'status': 'found',
                    'verified': True,
                    'source': 'github_api',
                    'additional_info': {
                        'name': data.get('name'),
                        'bio': data.get('bio'),
                        'public_repos': data.get('public_repos'),
                        'followers': data.get('followers'),
                        'created_at': data.get('created_at')
                    }
                }
        except Exception as e:
            logger.debug(f"GitHub API error: {e}")
        
        return None













