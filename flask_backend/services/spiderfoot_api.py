"""
Spiderfoot API integration using web UI
This is more stable than CLI execution
"""
import logging
import time
import requests
from typing import Dict, List

logger = logging.getLogger(__name__)

class SpiderfootAPI:
    """Spiderfoot API client for web UI"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.is_available = self._check_availability()
        
    def _check_availability(self) -> bool:
        """Check if Spiderfoot server is available"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=2)
            return response.status_code == 200
        except:
            logger.warning(f"Spiderfoot server not available at {self.base_url}")
            return False
        
    def start_scan(self, target: str, scan_type: str = "USERNAME", modules: List[str] = None) -> Dict:
        """Start a new scan"""
        if not self.is_available:
            return {
                'status': 'error',
                'message': 'Spiderfoot server is not running. Please start Spiderfoot on port 5001.'
            }
        
        if modules is None:
            modules = ['sfp_accounts', 'sfp_social', 'sfp_github']
        
        try:
            # Create new scan
            url = f"{self.base_url}/startscan"
            payload = {
                'scanname': f"user_investigation_{target}_{int(time.time())}",
                'scantarget': target,
                'modulelist': ','.join(modules),
                'typelist': scan_type
            }
            
            logger.info(f"Starting Spiderfoot scan for {target}")
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'started',
                    'scan_id': data.get('id'),
                    'message': 'Scan started successfully'
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to start scan: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Spiderfoot API error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_scan_results(self, scan_id: str) -> Dict:
        """Get scan results"""
        try:
            url = f"{self.base_url}/scanresults"
            params = {'id': scan_id, 'format': 'json'}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'results': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Failed to get results: {response.text}'
                }
                
        except Exception as e:
            logger.error(f"Spiderfoot API error: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


def run_spiderfoot_via_api(username: str) -> Dict:
    """
    Run Spiderfoot investigation via web API
    This is more stable than CLI
    """
    try:
        api = SpiderfootAPI()
        
        # Start scan
        scan_result = api.start_scan(username, 'USERNAME', ['sfp_accounts', 'sfp_social', 'sfp_github'])
        
        if scan_result['status'] != 'started':
            return {
                'tool': 'spiderfoot',
                'target': username,
                'status': 'error',
                'findings': [],
                'error': scan_result.get('message', 'Failed to start scan')
            }
        
        scan_id = scan_result['scan_id']
        
        # Wait for scan to complete (with timeout)
        max_wait = 120  # 2 minutes - give Spiderfoot time to complete
        wait_time = 0
        wait_interval = 3  # Check every 3 seconds
        
        while wait_time < max_wait:
            time.sleep(wait_interval)
            wait_time += wait_interval
            
            results = api.get_scan_results(scan_id)
            
            if results['status'] == 'success':
                findings = parse_spiderfoot_results(results['results'])
                return {
                    'tool': 'spiderfoot',
                    'target': username,
                    'status': 'completed',
                    'findings': findings,
                    'scan_id': scan_id
                }
        
        # Timeout
        return {
            'tool': 'spiderfoot',
            'target': username,
            'status': 'timeout',
            'findings': [],
            'error': 'Scan timed out after 2 minutes'
        }
        
    except Exception as e:
        logger.error(f"Spiderfoot API error: {e}")
        return {
            'tool': 'spiderfoot',
            'target': username,
            'status': 'error',
            'findings': [],
            'error': str(e)
        }


def parse_spiderfoot_results(results: Dict) -> List[Dict]:
    """Parse Spiderfoot results into findings"""
    findings = []
    
    if not results or 'data' not in results:
        return findings
    
    for item in results['data']:
        findings.append({
            'type': item.get('type', 'unknown'),
            'data': item.get('data', ''),
            'module': item.get('module', ''),
            'confidence': item.get('confidence', 'medium'),
            'timestamp': item.get('generated', '')
        })
    
    return findings
