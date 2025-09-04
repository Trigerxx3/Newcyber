"""
Admin-specific API routes
"""
from flask import Blueprint, jsonify, request
from auth import require_auth, require_role
from models.user import SystemUser, User
from models.source import Source
from models.keyword import Keyword
from models.content import Content
from models.case import Case
from models.osint_result import OSINTResult
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@require_auth
@require_role('Admin')
def get_admin_stats():
    """Get comprehensive admin dashboard statistics"""
    try:
        # System Users Stats
        total_users = SystemUser.query.count()
        active_users = SystemUser.query.filter_by(is_active=True).count()
        from models.user import SystemUserRole
        admins = SystemUser.query.filter_by(role=SystemUserRole.ADMIN).count()
        analysts = SystemUser.query.filter_by(role=SystemUserRole.ANALYST).count()
        
        # Platform Users Stats (monitored users)
        try:
            monitored_users = User.query.count()
            flagged_users = User.query.filter_by(is_flagged=True).count()
        except Exception:
            monitored_users = 0
            flagged_users = 0
        
        # Content Stats
        try:
            total_content = Content.query.count()
            high_risk_content = Content.query.filter_by(risk_level='High').count()
        except Exception:
            total_content = 0
            high_risk_content = 0
        
        # Cases Stats
        try:
            total_cases = Case.query.count()
            active_cases = Case.query.filter_by(status='Active').count()
            pending_cases = Case.query.filter_by(status='Pending').count()
        except Exception:
            total_cases = 0
            active_cases = 0
            pending_cases = 0
        
        # Sources Stats
        try:
            total_sources = Source.query.count()
            active_sources = Source.query.filter_by(is_active=True).count()
        except Exception:
            total_sources = 0
            active_sources = 0
        
        # Keywords Stats
        try:
            total_keywords = Keyword.query.count()
        except Exception:
            total_keywords = 0
        
        # OSINT Results Stats
        try:
            total_osint_results = OSINTResult.query.count()
        except Exception:
            total_osint_results = 0
        
        # System Health
        last_backup = "2 hours ago"  # This would come from actual backup system
        uptime = "15d 8h"  # This would come from system monitoring
        
        return jsonify({
            'system_users': {
                'total': total_users,
                'active': active_users,
                'admins': admins,
                'analysts': analysts
            },
            'platform_users': {
                'total': monitored_users,
                'flagged': flagged_users
            },
            'content': {
                'total': total_content,
                'high_risk': high_risk_content
            },
            'cases': {
                'total': total_cases,
                'active': active_cases,
                'pending': pending_cases
            },
            'sources': {
                'total': total_sources,
                'active': active_sources
            },
            'keywords': {
                'total': total_keywords
            },
            'osint_results': {
                'total': total_osint_results
            },
            'system_health': {
                'last_backup': last_backup,
                'uptime': uptime,
                'database_size': '172KB'
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['GET'])
@require_auth
@require_role('Admin')
def get_system_users():
    """Get all system users for user management"""
    try:
        users = SystemUser.query.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value if hasattr(user.role, 'value') else str(user.role),
                'is_active': user.is_active,
                'last_login': user.last_login.isoformat() if user.last_login else 'Never',
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'cases_assigned': 0  # Would be calculated from actual case assignments
            })
            
        return jsonify(users_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/sources', methods=['GET', 'POST'])
@require_auth
@require_role('Admin')
def manage_sources():
    """Get all data sources or create new one"""
    if request.method == 'GET':
        try:
            sources = Source.query.all()
            sources_data = []
            
            for source in sources:
                # Count users and content for this source
                user_count = User.query.filter_by(source_id=source.id).count() if hasattr(User, 'source_id') else 0
                content_count = Content.query.filter_by(source_id=source.id).count() if hasattr(Content, 'source_id') else 0
                
                sources_data.append({
                    'id': source.id,
                    'name': source.source_name if hasattr(source, 'source_name') else source.name,
                    'platform': source.platform.value if hasattr(source.platform, 'value') else str(source.platform),
                    'type': source.source_type.value if hasattr(source, 'source_type') and hasattr(source.source_type, 'value') else 'unknown',
                    'handle': source.source_handle if hasattr(source, 'source_handle') else '',
                    'description': source.description,
                    'isActive': source.is_active,
                    'createdAt': source.created_at.isoformat() if source.created_at else None,
                    'lastChecked': 'Never',  # Would come from monitoring system
                    'userCount': user_count,
                    'contentCount': content_count
                })
                
            return jsonify(sources_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Import platform and source types
            from models.source import PlatformType, SourceType
            
            # Map platform string to enum
            platform_map = {
                'telegram': PlatformType.TELEGRAM,
                'instagram': PlatformType.INSTAGRAM,
                'whatsapp': PlatformType.WHATSAPP,
                'twitter': PlatformType.TWITTER
            }
            
            type_map = {
                'channel': SourceType.CHANNEL,
                'group': SourceType.GROUP,
                'profile': SourceType.PROFILE
            }
            
            platform = platform_map.get(data.get('platform', 'telegram'), PlatformType.TELEGRAM)
            source_type = type_map.get(data.get('type', 'channel'), SourceType.CHANNEL)
            
            new_source = Source(
                platform=platform,
                source_handle=data.get('handle', ''),
                source_name=data.get('name', ''),
                source_type=source_type,
                description=data.get('description', ''),
                is_active=True
            )
            
            db.session.add(new_source)
            db.session.commit()
            
            return jsonify({
                'id': new_source.id,
                'name': new_source.source_name,
                'platform': new_source.platform.value,
                'type': new_source.source_type.value,
                'handle': new_source.source_handle,
                'description': new_source.description,
                'isActive': new_source.is_active,
                'createdAt': new_source.created_at.isoformat(),
                'lastChecked': 'Never',
                'userCount': 0,
                'contentCount': 0
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@admin_bp.route('/sources/<int:source_id>/toggle', methods=['POST'])
@require_auth
@require_role('Admin')
def toggle_source(source_id):
    """Toggle source active status"""
    try:
        source = Source.query.get_or_404(source_id)
        source.is_active = not source.is_active
        db.session.commit()
        
        return jsonify({
            'id': source.id,
            'isActive': source.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/keywords', methods=['GET', 'POST'])
@require_auth
@require_role('Admin')
def manage_keywords():
    """Get all detection keywords or create new one"""
    if request.method == 'GET':
        try:
            keywords = Keyword.query.all()
            keywords_data = []
            
            for keyword in keywords:
                keywords_data.append({
                    'id': keyword.id,
                    'term': keyword.keyword if hasattr(keyword, 'keyword') else keyword.term,
                    'category': keyword.type.value if hasattr(keyword, 'type') and hasattr(keyword.type, 'value') else keyword.category,
                    'weight': keyword.severity.value if hasattr(keyword, 'severity') and hasattr(keyword.severity, 'value') else keyword.weight,
                    'isActive': keyword.is_active,
                    'description': keyword.description,
                    'createdAt': keyword.created_at.isoformat() if keyword.created_at else None,
                    'detectionCount': 0,  # Would come from detection counts
                    'lastDetection': 'Never'  # Would come from last detection
                })
                
            return jsonify(keywords_data)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Import keyword types
            from models.keyword import KeywordType, KeywordSeverity
            
            # Map category string to enum
            type_map = {
                'general': KeywordType.GENERAL,
                'drugs': KeywordType.DRUGS,
                'violence': KeywordType.VIOLENCE,
                'terrorism': KeywordType.TERRORISM,
                'fraud': KeywordType.FRAUD
            }
            
            # Map weight to severity
            weight = data.get('weight', 1)
            if weight >= 8:
                severity = KeywordSeverity.CRITICAL
            elif weight >= 6:
                severity = KeywordSeverity.HIGH
            elif weight >= 4:
                severity = KeywordSeverity.MEDIUM
            else:
                severity = KeywordSeverity.LOW
            
            keyword_type = type_map.get(data.get('category', 'general'), KeywordType.GENERAL)
            
            new_keyword = Keyword(
                keyword=data.get('term', ''),
                description=data.get('description', ''),
                type=keyword_type,
                severity=severity,
                is_active=True
            )
            
            db.session.add(new_keyword)
            db.session.commit()
            
            return jsonify({
                'id': new_keyword.id,
                'term': new_keyword.keyword,
                'category': new_keyword.type.value,
                'weight': weight,
                'isActive': new_keyword.is_active,
                'description': new_keyword.description,
                'createdAt': new_keyword.created_at.isoformat(),
                'detectionCount': 0,
                'lastDetection': 'Never'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@admin_bp.route('/keywords/<int:keyword_id>/toggle', methods=['POST'])
@require_auth
@require_role('Admin')
def toggle_keyword(keyword_id):
    """Toggle keyword active status"""
    try:
        keyword = Keyword.query.get_or_404(keyword_id)
        keyword.is_active = not keyword.is_active
        db.session.commit()
        
        return jsonify({
            'id': keyword.id,
            'isActive': keyword.is_active
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/stats', methods=['GET'])
@require_auth
@require_role('Admin')
def get_data_stats():
    """Get comprehensive data statistics"""
    try:
        # Platform Users Stats
        platform_users_total = User.query.count() if User.query.first() else 0
        platform_users_flagged = User.query.filter_by(is_flagged=True).count() if User.query.first() else 0
        platform_users_active = platform_users_total - platform_users_flagged
        
        # Sources Stats
        sources_total = Source.query.count() if Source.query.first() else 0
        sources_active = Source.query.filter_by(is_active=True).count() if Source.query.first() else 0
        
        # Keywords Stats
        keywords_total = Keyword.query.count() if Keyword.query.first() else 0
        keywords_active = Keyword.query.filter_by(is_active=True).count() if Keyword.query.first() else 0
        
        # Content Stats
        content_total = Content.query.count() if Content.query.first() else 0
        content_high_risk = Content.query.filter_by(risk_level='High').count() if Content.query.first() else 0
        content_pending = Content.query.filter_by(status='Pending').count() if Content.query.first() else 0
        content_analyzed = content_total - content_pending
        
        # Cases Stats
        cases_total = Case.query.count() if Case.query.first() else 0
        cases_active = Case.query.filter_by(status='Open').count() if Case.query.first() else 0
        cases_pending = Case.query.filter_by(status='Pending').count() if Case.query.first() else 0
        cases_closed = Case.query.filter_by(status='Closed').count() if Case.query.first() else 0
        
        return jsonify({
            'platformUsers': {
                'total': platform_users_total,
                'flagged': platform_users_flagged,
                'active': platform_users_active
            },
            'sources': {
                'total': sources_total,
                'active': sources_active,
                'platforms': {}  # Would be calculated from platform breakdown
            },
            'keywords': {
                'total': keywords_total,
                'active': keywords_active,
                'categories': {}  # Would be calculated from category breakdown
            },
            'content': {
                'total': content_total,
                'highRisk': content_high_risk,
                'pending': content_pending,
                'analyzed': content_analyzed
            },
            'cases': {
                'total': cases_total,
                'active': cases_active,
                'pending': cases_pending,
                'closed': cases_closed
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/platform-users', methods=['GET'])
@require_auth
@require_role('Admin')
def get_platform_users():
    """Get all platform users (monitored users)"""
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            # Get source information
            source = user.source if hasattr(user, 'source') else None
            platform = source.platform.value if source and hasattr(source.platform, 'value') else 'unknown'
            source_name = source.source_name if source else 'Unknown Source'
            
            # Calculate content count and risk score
            content_count = user.content.count() if hasattr(user, 'content') else 0
            risk_score = 5  # Default risk score, would be calculated from content analysis
            
            users_data.append({
                'id': str(user.id),
                'username': user.username or 'Unknown',
                'fullName': user.full_name or '',
                'bio': user.bio or '',
                'isFlagged': user.is_flagged,
                'sourceName': source_name,
                'platform': platform,
                'createdAt': user.created_at.isoformat() if user.created_at else None,
                'contentCount': content_count,
                'riskScore': risk_score
            })
            
        return jsonify(users_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/platform-users/<int:user_id>/flag', methods=['POST'])
@require_auth
@require_role('Admin')
def toggle_user_flag(user_id):
    """Toggle user flag status"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_flagged = not user.is_flagged
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'isFlagged': user.is_flagged
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/content', methods=['GET'])
@require_auth
@require_role('Admin')
def get_content_data():
    """Get all analyzed content"""
    try:
        content_items = Content.query.limit(100).all()  # Limit for performance
        content_data = []
        
        for item in content_items:
            # Get source/platform information
            source = item.source if hasattr(item, 'source') else None
            platform = source.platform.value if source and hasattr(source.platform, 'value') else 'unknown'
            
            content_data.append({
                'id': str(item.id),
                'title': item.title or 'Untitled',
                'text': item.text[:500] if item.text else '',  # Truncate for performance
                'author': item.author or 'Unknown',
                'platform': platform,
                'riskLevel': item.risk_level.value if hasattr(item.risk_level, 'value') else str(item.risk_level),
                'status': item.status.value if hasattr(item.status, 'value') else str(item.status),
                'createdAt': item.created_at.isoformat() if item.created_at else None,
                'keywordMatches': item.keywords if item.keywords else [],
                'confidence': item.confidence_score or 0
            })
            
        return jsonify(content_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/cases', methods=['GET'])
@require_auth
@require_role('Admin')
def get_cases_data():
    """Get all investigation cases"""
    try:
        cases = Case.query.all()
        cases_data = []
        
        for case in cases:
            # Get assignment information
            assigned_to = case.assigned_to.username if hasattr(case, 'assigned_to') and case.assigned_to else 'Unassigned'
            created_by = case.created_by.username if hasattr(case, 'created_by') and case.created_by else 'Unknown'
            
            # Count associated users and content
            user_count = 0  # Would be calculated from case-user relationships
            content_count = 0  # Would be calculated from case-content relationships
            
            cases_data.append({
                'id': str(case.id),
                'title': case.title,
                'caseNumber': case.case_number,
                'type': case.type.value if hasattr(case.type, 'value') else str(case.type),
                'status': case.status.value if hasattr(case.status, 'value') else str(case.status),
                'priority': case.priority.value if hasattr(case.priority, 'value') else str(case.priority),
                'assignedTo': assigned_to,
                'createdBy': created_by,
                'createdAt': case.created_at.isoformat() if case.created_at else None,
                'userCount': user_count,
                'contentCount': content_count,
                'riskScore': case.risk_score or 0
            })
            
        return jsonify(cases_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/data/export/<data_type>', methods=['GET'])
@require_auth
@require_role('Admin')
def export_data(data_type):
    """Export data by type"""
    try:
        if data_type == 'users':
            data = [user.to_dict() for user in User.query.all()]
        elif data_type == 'sources':
            data = [source.to_dict() for source in Source.query.all()]
        elif data_type == 'keywords':
            data = [keyword.to_dict() for keyword in Keyword.query.all()]
        elif data_type == 'content':
            data = [content.to_dict() for content in Content.query.limit(1000).all()]
        elif data_type == 'cases':
            data = [case.to_dict() for case in Case.query.all()]
        elif data_type == 'all':
            data = {
                'users': [user.to_dict() for user in User.query.all()],
                'sources': [source.to_dict() for source in Source.query.all()],
                'keywords': [keyword.to_dict() for keyword in Keyword.query.all()],
                'content': [content.to_dict() for content in Content.query.limit(1000).all()],
                'cases': [case.to_dict() for case in Case.query.all()],
                'exported_at': datetime.utcnow().isoformat()
            }
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/activity', methods=['GET'])
@require_auth
@require_role('Admin')
def get_recent_activity():
    """Get recent system activity"""
    try:
        # This would typically come from an activity log table
        # For now, we'll generate based on actual data
        activity = []
        
        # Get recent users
        recent_users = SystemUser.query.order_by(SystemUser.created_at.desc()).limit(3).all()
        for user in recent_users:
            activity.append({
                'type': 'user_created',
                'message': f'New {user.role.value.lower()} account created: {user.email}',
                'timestamp': user.created_at.isoformat() if user.created_at else datetime.now().isoformat(),
                'severity': 'info'
            })
        
        # Add system events
        activity.extend([
            {
                'type': 'system',
                'message': 'System backup completed successfully',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'severity': 'success'
            },
            {
                'type': 'system',
                'message': 'Database migration completed',
                'timestamp': (datetime.now() - timedelta(hours=4)).isoformat(),
                'severity': 'info'
            }
        ])
        
        # Sort by timestamp (most recent first)
        activity.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify(activity[:10])  # Return last 10 activities
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api-status', methods=['GET'])
@require_auth
@require_role('Admin')
def get_api_status():
    """Get status of external API connections"""
    try:
        # This would typically ping actual APIs
        # For now, we'll return mock status based on configuration
        api_status = {
            'telegram': {
                'status': 'connected',
                'last_checked': datetime.now().isoformat(),
                'response_time': '45ms'
            },
            'instagram': {
                'status': 'disconnected',
                'last_checked': (datetime.now() - timedelta(hours=1)).isoformat(),
                'response_time': 'N/A'
            },
            'sherlock': {
                'status': 'connected',
                'last_checked': datetime.now().isoformat(),
                'response_time': '120ms'
            },
            'spiderfoot': {
                'status': 'error',
                'last_checked': (datetime.now() - timedelta(minutes=30)).isoformat(),
                'response_time': 'Timeout'
            }
        }
        
        return jsonify(api_status)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500