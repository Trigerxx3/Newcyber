"""
WhatsApp Business API integration for monitoring and data collection
This service provides methods to interact with WhatsApp Business API
"""
import os
import json
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

class WhatsAppScraper:
    """
    WhatsApp Business API client for monitoring and webhook handling
    Note: WhatsApp doesn't allow traditional scraping, only official API access
    """
    
    def __init__(self):
        self.access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN')
        self.business_account_id = os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID')
        self.phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID')
        self.webhook_verify_token = os.environ.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
        
        # WhatsApp Business API endpoints
        self.base_url = "https://graph.facebook.com/v18.0"
        self.messages_url = f"{self.base_url}/{self.phone_number_id}/messages"
        
        # Rate limiting
        self.rate_limit_delay = 1  # Seconds between requests
        
    def initialize(self) -> bool:
        """Initialize WhatsApp Business API client"""
        try:
            if not self.access_token or not self.business_account_id:
                logger.warning("WhatsApp Business API credentials not found.")
                logger.info("Please set WHATSAPP_ACCESS_TOKEN and WHATSAPP_BUSINESS_ACCOUNT_ID")
                logger.info("Get credentials from Facebook Developer Console")
                return False
            
            # Test API connection
            if self.test_connection():
                logger.info("WhatsApp Business API client initialized successfully")
                return True
            else:
                logger.error("WhatsApp Business API connection test failed")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp Business API client: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test WhatsApp Business API connection"""
        try:
            url = f"{self.base_url}/{self.business_account_id}/phone_numbers"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Connected to WhatsApp Business API. Found {len(data.get('data', []))} phone numbers")
                return True
            else:
                logger.error(f"WhatsApp API test failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"WhatsApp API connection test error: {e}")
            return False
    
    def get_business_profile(self) -> Optional[Dict[str, Any]]:
        """Get WhatsApp Business profile information"""
        try:
            if not self.access_token:
                return self._get_mock_business_profile()
            
            url = f"{self.base_url}/{self.phone_number_id}/whatsapp_business_profile"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                profile = data.get('data', [{}])[0]
                
                return {
                    'about': profile.get('about', ''),
                    'address': profile.get('address', ''),
                    'description': profile.get('description', ''),
                    'email': profile.get('email', ''),
                    'messaging_product': profile.get('messaging_product', 'whatsapp'),
                    'profile_picture_url': profile.get('profile_picture_url', ''),
                    'websites': profile.get('websites', []),
                    'vertical': profile.get('vertical', '')
                }
            else:
                logger.error(f"Failed to get business profile: {response.status_code}")
                return self._get_mock_business_profile()
                
        except Exception as e:
            logger.error(f"Error getting business profile: {e}")
            return self._get_mock_business_profile()
    
    def get_phone_numbers(self) -> List[Dict[str, Any]]:
        """Get registered phone numbers for the business account"""
        try:
            if not self.access_token:
                return self._get_mock_phone_numbers()
            
            url = f"{self.base_url}/{self.business_account_id}/phone_numbers"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.error(f"Failed to get phone numbers: {response.status_code}")
                return self._get_mock_phone_numbers()
                
        except Exception as e:
            logger.error(f"Error getting phone numbers: {e}")
            return self._get_mock_phone_numbers()
    
    def send_message(self, to: str, message: str) -> Dict[str, Any]:
        """
        Send a WhatsApp message (for testing and verification)
        
        Args:
            to: Recipient phone number (with country code)
            message: Message text
            
        Returns:
            Dictionary containing response data
        """
        try:
            if not self.access_token:
                return self._mock_send_message(to, message)
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': to,
                'type': 'text',
                'text': {
                    'body': message
                }
            }
            
            response = requests.post(self.messages_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Message sent successfully to {to}")
                return {
                    'success': True,
                    'message_id': data.get('messages', [{}])[0].get('id'),
                    'status': 'sent',
                    'to': to,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle incoming webhook data from WhatsApp
        
        Args:
            webhook_data: Webhook payload from WhatsApp
            
        Returns:
            Processed webhook data
        """
        try:
            processed_messages = []
            
            # Extract messages from webhook
            for entry in webhook_data.get('entry', []):
                for change in entry.get('changes', []):
                    if change.get('field') == 'messages':
                        value = change.get('value', {})
                        
                        # Process incoming messages
                        for message in value.get('messages', []):
                            processed_message = {
                                'id': message.get('id'),
                                'from': message.get('from'),
                                'timestamp': message.get('timestamp'),
                                'type': message.get('type'),
                                'text': message.get('text', {}).get('body', '') if message.get('type') == 'text' else '',
                                'media_url': self._extract_media_url(message),
                                'received_at': datetime.now().isoformat()
                            }
                            processed_messages.append(processed_message)
                        
                        # Process message status updates
                        for status in value.get('statuses', []):
                            processed_status = {
                                'id': status.get('id'),
                                'status': status.get('status'),
                                'timestamp': status.get('timestamp'),
                                'recipient_id': status.get('recipient_id')
                            }
                            # You could store this in database for message tracking
            
            return {
                'processed_messages': processed_messages,
                'message_count': len(processed_messages),
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {
                'error': str(e),
                'processed_messages': [],
                'message_count': 0
            }
    
    def get_media(self, media_id: str) -> Optional[Dict[str, Any]]:
        """Get media file information"""
        try:
            if not self.access_token:
                return None
            
            url = f"{self.base_url}/{media_id}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get media {media_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting media {media_id}: {e}")
            return None
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook for WhatsApp Business API"""
        try:
            if mode == 'subscribe' and token == self.webhook_verify_token:
                logger.info("Webhook verified successfully")
                return challenge
            else:
                logger.warning("Webhook verification failed")
                return None
                
        except Exception as e:
            logger.error(f"Webhook verification error: {e}")
            return None
    
    def _extract_media_url(self, message: Dict[str, Any]) -> Optional[str]:
        """Extract media URL from message"""
        message_type = message.get('type')
        
        if message_type in ['image', 'video', 'audio', 'document']:
            media_data = message.get(message_type, {})
            return media_data.get('url') or media_data.get('link')
        
        return None
    
    def _get_mock_business_profile(self) -> Dict[str, Any]:
        """Return mock business profile when real API is not available"""
        return {
            'about': 'Cyber Intelligence Platform WhatsApp Bot',
            'address': '123 Security Street, Cyber City',
            'description': 'Automated security monitoring and alerts',
            'email': 'support@cyberintel.com',
            'messaging_product': 'whatsapp',
            'profile_picture_url': 'https://via.placeholder.com/200?text=CyberBot',
            'websites': ['https://cyberintel.com'],
            'vertical': 'TECH'
        }
    
    def _get_mock_phone_numbers(self) -> List[Dict[str, Any]]:
        """Return mock phone numbers when real API is not available"""
        return [
            {
                'id': '1234567890',
                'display_phone_number': '+1 (555) 123-4567',
                'verified_name': 'Cyber Intelligence Bot',
                'status': 'CONNECTED',
                'quality_rating': 'GREEN'
            }
        ]
    
    def _mock_send_message(self, to: str, message: str) -> Dict[str, Any]:
        """Return mock send message response when real API is not available"""
        import random
        
        return {
            'success': True,
            'message_id': f"wamid.mock_{random.randint(1000, 9999)}",
            'status': 'sent',
            'to': to,
            'timestamp': datetime.now().isoformat(),
            'note': 'This is a mock response - no actual message was sent'
        }
    
    def get_webhook_setup_info(self) -> Dict[str, Any]:
        """Get information for setting up webhooks"""
        return {
            'webhook_url': 'https://your-domain.com/api/scraping/whatsapp/webhook',
            'verify_token': self.webhook_verify_token or 'your-verify-token',
            'subscription_fields': [
                'messages',
                'message_deliveries',
                'message_reads',
                'message_echoes'
            ],
            'setup_instructions': [
                "1. Go to Facebook Developer Console",
                "2. Select your WhatsApp Business app",
                "3. Go to WhatsApp > Configuration",
                "4. Add the webhook URL and verify token",
                "5. Subscribe to webhook fields",
                "6. Test the webhook connection"
            ]
        }

# Global scraper instance
whatsapp_scraper = WhatsAppScraper()

def get_whatsapp_scraper():
    """Get the global WhatsApp scraper instance"""
    if not whatsapp_scraper.access_token:
        whatsapp_scraper.initialize()
    return whatsapp_scraper
