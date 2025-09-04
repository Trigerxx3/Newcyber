"""
Scraping management API routes
"""
from flask import Blueprint, jsonify, request
from auth import require_auth, require_role
from models.user import SystemUser
from models.source import Source
from models.content import Content
from models.keyword import Keyword
from extensions import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import json
import uuid
import asyncio

# Import scraping services
from services.telegram_scraper import get_telegram_scraper
from services.instagram_scraper import get_instagram_scraper
from services.whatsapp_scraper import get_whatsapp_scraper

scraping_bp = Blueprint('scraping', __name__)

# Mock scraping job storage (in production, this would be in the database)
scraping_jobs = {}

@scraping_bp.route('/stats', methods=['GET'])
@require_auth
@require_role('Admin')
def get_scraping_stats():
    """Get comprehensive scraping statistics"""
    try:
        # Calculate stats from actual data and mock jobs
        total_jobs = len(scraping_jobs)
        active_jobs = len([job for job in scraping_jobs.values() if job['status'] == 'running'])
        paused_jobs = len([job for job in scraping_jobs.values() if job['status'] == 'paused'])
        
        # Get content stats
        total_content = Content.query.count() if Content.query.first() else 0
        today = datetime.now().date()
        today_scraped = Content.query.filter(
            func.date(Content.created_at) == today
        ).count() if Content.query.first() else 0
        
        # Calculate average per day (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        week_content = Content.query.filter(
            Content.created_at >= week_ago
        ).count() if Content.query.first() else 0
        average_per_day = round(week_content / 7)
        
        # Platform distribution
        platforms = {
            'telegram': {'jobs': 0, 'content': 0},
            'instagram': {'jobs': 0, 'content': 0},
            'whatsapp': {'jobs': 0, 'content': 0}
        }
        
        # Count jobs by platform
        for job in scraping_jobs.values():
            platform = job.get('platform', 'telegram')
            if platform in platforms:
                platforms[platform]['jobs'] += 1
        
        # Count content by platform (would need platform field in Content model)
        # For now, distribute randomly
        if total_content > 0:
            platforms['telegram']['content'] = int(total_content * 0.6)
            platforms['instagram']['content'] = int(total_content * 0.3)
            platforms['whatsapp']['content'] = int(total_content * 0.1)
        
        # Top sources (mock data for now)
        top_sources = [
            {'name': '@cyberthreat_news', 'platform': 'telegram', 'content': 1250},
            {'name': '@security_alerts', 'platform': 'telegram', 'content': 890},
            {'name': 'cybersec_daily', 'platform': 'instagram', 'content': 456},
            {'name': 'threat_intel', 'platform': 'whatsapp', 'content': 234}
        ]
        
        return jsonify({
            'totalJobs': total_jobs,
            'activeJobs': active_jobs,
            'pausedJobs': paused_jobs,
            'totalContent': total_content,
            'todayScraped': today_scraped,
            'averagePerDay': average_per_day,
            'platforms': platforms,
            'topSources': top_sources
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/jobs', methods=['GET', 'POST'])
@require_auth
@require_role('Admin')
def manage_scraping_jobs():
    """Get all scraping jobs or create new one"""
    if request.method == 'GET':
        try:
            jobs_list = []
            for job_id, job in scraping_jobs.items():
                jobs_list.append({
                    'id': job_id,
                    'name': job['name'],
                    'platform': job['platform'],
                    'target': job['target'],
                    'targetType': job['targetType'],
                    'status': job['status'],
                    'schedule': job['schedule'],
                    'lastRun': job['lastRun'],
                    'nextRun': job['nextRun'],
                    'totalScraped': job['totalScraped'],
                    'newItems': job['newItems'],
                    'errors': job['errors'],
                    'isActive': job['isActive'],
                    'settings': job['settings'],
                    'createdAt': job['createdAt'],
                    'updatedAt': job['updatedAt']
                })
            
            return jsonify(jobs_list)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            job_id = str(uuid.uuid4())
            new_job = {
                'id': job_id,
                'name': data.get('name'),
                'platform': data.get('platform'),
                'target': data.get('target'),
                'targetType': data.get('targetType'),
                'status': 'stopped',
                'schedule': data.get('schedule'),
                'lastRun': 'Never',
                'nextRun': 'Manual',
                'totalScraped': 0,
                'newItems': 0,
                'errors': 0,
                'isActive': True,
                'settings': data.get('settings', {}),
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }
            
            scraping_jobs[job_id] = new_job
            
            return jsonify(new_job)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@scraping_bp.route('/jobs/<job_id>/control', methods=['POST'])
@require_auth
@require_role('Admin')
def control_scraping_job(job_id):
    """Control scraping job (start, pause, stop, delete)"""
    try:
        data = request.get_json()
        action = data.get('action')
        
        if job_id not in scraping_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = scraping_jobs[job_id]
        
        if action == 'start':
            job['status'] = 'running'
            job['lastRun'] = datetime.now().isoformat()
            # In production, this would trigger the actual scraping process
            
        elif action == 'pause':
            job['status'] = 'paused'
            
        elif action == 'stop':
            job['status'] = 'stopped'
            
        elif action == 'delete':
            del scraping_jobs[job_id]
            return jsonify({'message': 'Job deleted successfully'})
        
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        job['updatedAt'] = datetime.now().isoformat()
        
        return jsonify({
            'id': job_id,
            'status': job['status'],
            'message': f'Job {action}ed successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/jobs/<job_id>/toggle', methods=['POST'])
@require_auth
@require_role('Admin')
def toggle_scraping_job(job_id):
    """Toggle job active status"""
    try:
        if job_id not in scraping_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = scraping_jobs[job_id]
        job['isActive'] = not job['isActive']
        job['updatedAt'] = datetime.now().isoformat()
        
        return jsonify({
            'id': job_id,
            'isActive': job['isActive']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/jobs/<job_id>/run', methods=['POST'])
@require_auth
@require_role('Admin')
def run_scraping_job_now(job_id):
    """Run scraping job immediately"""
    try:
        if job_id not in scraping_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = scraping_jobs[job_id]
        job['status'] = 'running'
        job['lastRun'] = datetime.now().isoformat()
        job['updatedAt'] = datetime.now().isoformat()
        
        # In production, this would trigger the actual scraping process
        # For now, simulate some activity
        import random
        job['newItems'] = random.randint(5, 50)
        job['totalScraped'] += job['newItems']
        
        return jsonify({
            'id': job_id,
            'status': job['status'],
            'message': 'Job started successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/content', methods=['GET'])
@require_auth
@require_role('Admin')
def get_scraped_content():
    """Get scraped content"""
    try:
        limit = request.args.get('limit', 100, type=int)
        
        # Get real content from database
        content_items = Content.query.order_by(desc(Content.created_at)).limit(limit).all()
        content_data = []
        
        for item in content_items:
            # Get source information for platform
            source = item.source if hasattr(item, 'source') else None
            platform = source.platform.value if source and hasattr(source.platform, 'value') else 'unknown'
            
            # Mock engagement data (in production, this would be stored)
            import random
            engagement = {
                'likes': random.randint(0, 1000),
                'comments': random.randint(0, 100),
                'shares': random.randint(0, 50)
            }
            
            content_data.append({
                'id': str(item.id),
                'jobId': 'mock-job-id',
                'platform': platform,
                'author': item.author or 'Unknown',
                'text': item.text[:500] if item.text else '',
                'url': item.url or '',
                'mediaUrls': [],  # Would be populated from media storage
                'timestamp': item.created_at.isoformat() if item.created_at else datetime.now().isoformat(),
                'scrapedAt': item.created_at.isoformat() if item.created_at else datetime.now().isoformat(),
                'keywordMatches': item.keywords if item.keywords else [],
                'sentiment': item.sentiment_score or 0,
                'engagement': engagement,
                'processed': True,
                'flagged': False
            })
        
        return jsonify(content_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/export/<data_type>', methods=['GET'])
@require_auth
@require_role('Admin')
def export_scraping_data(data_type):
    """Export scraping data"""
    try:
        if data_type == 'jobs':
            data = list(scraping_jobs.values())
        elif data_type == 'content':
            # Export content from database
            content_items = Content.query.all()
            data = [item.to_dict() for item in content_items]
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        return jsonify({
            'type': data_type,
            'count': len(data),
            'data': data,
            'exported_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Telegram-specific endpoints
@scraping_bp.route('/telegram/channels', methods=['GET'])
@require_auth
@require_role('Admin')
def get_telegram_channels():
    """Get available Telegram channels for scraping"""
    try:
        # Get real Telegram channels using the scraper
        telegram_scraper = get_telegram_scraper()
        
        # Use asyncio to call async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            channels = loop.run_until_complete(telegram_scraper.get_public_channels())
        finally:
            loop.close()
        
        return jsonify(channels)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/telegram/scrape', methods=['POST'])
@require_auth
@require_role('Admin')
def scrape_telegram_channel():
    """Scrape a Telegram channel manually"""
    try:
        data = request.get_json()
        channel_id = data.get('channel_id')
        max_messages = data.get('max_messages', 50)
        keywords = data.get('keywords', [])
        
        if not channel_id:
            return jsonify({'error': 'Channel ID is required'}), 400
        
        # Get real Telegram scraper
        telegram_scraper = get_telegram_scraper()
        
        # Use asyncio to call async scraping method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            scrape_result = loop.run_until_complete(
                telegram_scraper.scrape_channel(channel_id, max_messages, keywords)
            )
        finally:
            loop.close()
        
        # Store scraped data in database
        scraped_count = 0
        try:
            # Find or create source
            source = Source.query.filter_by(source_handle=channel_id).first()
            if not source:
                from models.source import PlatformType, SourceType
                source = Source(
                    platform=PlatformType.TELEGRAM,
                    source_handle=channel_id,
                    source_name=scrape_result.get('channel_title', f"Channel {channel_id}"),
                    source_type=SourceType.CHANNEL,
                    description=f"Auto-created for scraping {channel_id}",
                    is_active=True
                )
                db.session.add(source)
                db.session.flush()
            
            # Store scraped messages
            for message in scrape_result.get('messages', []):
                try:
                    content = Content(
                        source_id=source.id,
                        text=message.get('text', ''),
                        author=message.get('author', 'Unknown'),
                        url=message.get('url', ''),
                        keywords=keywords,
                        analysis_summary=f"Scraped from {channel_id} on {datetime.now().isoformat()}"
                    )
                    db.session.add(content)
                    scraped_count += 1
                    
                except Exception as content_error:
                    print(f"Error creating content: {content_error}")
                    continue
            
            db.session.commit()
            
        except Exception as db_error:
            db.session.rollback()
            print(f"Error storing scraped data: {db_error}")
        
        return jsonify({
            'channel_id': channel_id,
            'scraped_count': scraped_count,
            'total_messages': len(scrape_result.get('messages', [])),
            'message': f'Successfully scraped {scraped_count} messages from {channel_id}',
            'scrape_result': scrape_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Instagram-specific endpoints
@scraping_bp.route('/instagram/profiles', methods=['GET'])
@require_auth
@require_role('Admin')
def get_instagram_profiles():
    """Get Instagram profiles for scraping"""
    try:
        # Get real Instagram scraper
        instagram_scraper = get_instagram_scraper()
        
        # Search for some popular cybersecurity accounts
        search_queries = ['cybersecurity', 'infosec', 'hacking']
        all_profiles = []
        
        for query in search_queries:
            try:
                profiles = instagram_scraper.search_users(query, limit=5)
                all_profiles.extend(profiles)
            except Exception as search_error:
                print(f"Error searching for {query}: {search_error}")
                continue
        
        # Remove duplicates and limit results
        seen_usernames = set()
        unique_profiles = []
        for profile in all_profiles:
            if profile['username'] not in seen_usernames:
                seen_usernames.add(profile['username'])
                unique_profiles.append(profile)
                if len(unique_profiles) >= 10:
                    break
        
        return jsonify(unique_profiles)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/instagram/scrape', methods=['POST'])
@require_auth
@require_role('Admin')
def scrape_instagram_profile():
    """Scrape an Instagram profile manually"""
    try:
        data = request.get_json()
        username = data.get('username')
        max_posts = data.get('max_posts', 20)
        
        if not username:
            return jsonify({'error': 'Username is required'}), 400
        
        # Get real Instagram scraper
        instagram_scraper = get_instagram_scraper()
        
        # Scrape the profile
        scrape_result = instagram_scraper.scrape_user_posts(username, max_posts)
        
        # Store scraped data in database
        scraped_count = 0
        try:
            # Find or create source
            source = Source.query.filter_by(source_handle=f"@{username}").first()
            if not source:
                from models.source import PlatformType, SourceType
                user_info = scrape_result.get('user_info', {})
                source = Source(
                    platform=PlatformType.INSTAGRAM,
                    source_handle=f"@{username}",
                    source_name=user_info.get('full_name', username),
                    source_type=SourceType.PROFILE,
                    description=f"Instagram profile: {username}",
                    is_active=True
                )
                db.session.add(source)
                db.session.flush()
            
            # Store scraped posts
            for post in scrape_result.get('posts', []):
                try:
                    content = Content(
                        source_id=source.id,
                        text=post.get('caption', ''),
                        author=username,
                        url=post.get('url', ''),
                        keywords=post.get('hashtags', []),
                        analysis_summary=f"Instagram post from @{username}"
                    )
                    db.session.add(content)
                    scraped_count += 1
                    
                except Exception as content_error:
                    print(f"Error creating content: {content_error}")
                    continue
            
            db.session.commit()
            
        except Exception as db_error:
            db.session.rollback()
            print(f"Error storing Instagram data: {db_error}")
        
        return jsonify({
            'username': username,
            'scraped_count': scraped_count,
            'total_posts': len(scrape_result.get('posts', [])),
            'message': f'Successfully scraped {scraped_count} posts from @{username}',
            'scrape_result': scrape_result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# WhatsApp-specific endpoints (limited to public groups)
@scraping_bp.route('/whatsapp/groups', methods=['GET'])
@require_auth
@require_role('Admin')
def get_whatsapp_groups():
    """Get WhatsApp Business API information"""
    try:
        # Get real WhatsApp scraper
        whatsapp_scraper = get_whatsapp_scraper()
        
        # Get business profile and phone numbers
        business_profile = whatsapp_scraper.get_business_profile()
        phone_numbers = whatsapp_scraper.get_phone_numbers()
        webhook_info = whatsapp_scraper.get_webhook_setup_info()
        
        return jsonify({
            'business_profile': business_profile,
            'phone_numbers': phone_numbers,
            'webhook_info': webhook_info,
            'note': 'WhatsApp does not allow traditional scraping. Use Business API for official messaging.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/whatsapp/webhook', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Handle WhatsApp Business API webhooks"""
    try:
        whatsapp_scraper = get_whatsapp_scraper()
        
        if request.method == 'GET':
            # Webhook verification
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            verification_result = whatsapp_scraper.verify_webhook(mode, token, challenge)
            if verification_result:
                return verification_result
            else:
                return 'Verification failed', 403
        
        elif request.method == 'POST':
            # Handle incoming webhook data
            webhook_data = request.get_json()
            
            if webhook_data:
                processed_data = whatsapp_scraper.handle_webhook(webhook_data)
                
                # Store processed messages in database if needed
                for message in processed_data.get('processed_messages', []):
                    try:
                        # You could store WhatsApp messages here
                        # Note: This requires proper business account setup
                        pass
                    except Exception as store_error:
                        print(f"Error storing WhatsApp message: {store_error}")
                
                return jsonify({
                    'status': 'success',
                    'processed': processed_data['message_count']
                })
            
            return jsonify({'status': 'no_data'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scraping_bp.route('/health-check', methods=['GET'])
def health_check():
    """Health check for scraping services"""
    try:
        # Check Telegram
        telegram_status = {
            'available': False,
            'api_connected': False,
            'rate_limit': '30 requests/minute',
            'last_check': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            telegram_scraper = get_telegram_scraper()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                initialized = loop.run_until_complete(telegram_scraper.initialize())
                telegram_status['available'] = True
                telegram_status['api_connected'] = initialized
            finally:
                loop.close()
        except Exception as telegram_error:
            telegram_status['error'] = str(telegram_error)
        
        # Check Instagram
        instagram_status = {
            'available': False,
            'api_connected': False,
            'rate_limit': '200 requests/hour',
            'last_check': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            instagram_scraper = get_instagram_scraper()
            initialized = instagram_scraper.initialize()
            instagram_status['available'] = True
            instagram_status['api_connected'] = initialized
        except Exception as instagram_error:
            instagram_status['error'] = str(instagram_error)
        
        # Check WhatsApp
        whatsapp_status = {
            'available': False,
            'api_connected': False,
            'rate_limit': 'Business API limits',
            'last_check': datetime.now().isoformat(),
            'error': None
        }
        
        try:
            whatsapp_scraper = get_whatsapp_scraper()
            initialized = whatsapp_scraper.initialize()
            whatsapp_status['available'] = True
            whatsapp_status['api_connected'] = initialized
        except Exception as whatsapp_error:
            whatsapp_status['error'] = str(whatsapp_error)
        
        status = {
            'telegram': telegram_status,
            'instagram': instagram_status,
            'whatsapp': whatsapp_status,
            'overall_health': {
                'total_services': 3,
                'available_services': sum([
                    telegram_status['available'],
                    instagram_status['available'],
                    whatsapp_status['available']
                ]),
                'connected_services': sum([
                    telegram_status['api_connected'],
                    instagram_status['api_connected'],
                    whatsapp_status['api_connected']
                ])
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
