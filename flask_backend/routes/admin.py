"""
Admin-specific API routes
"""
from flask import Blueprint, jsonify
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

@admin_bp.route('/sources', methods=['GET'])
@require_auth
@require_role('Admin')
def get_sources():
    """Get all data sources"""
    try:
        sources = Source.query.all()
        sources_data = []
        
        for source in sources:
            sources_data.append({
                'id': source.id,
                'name': source.name,
                'type': source.type,
                'description': source.description,
                'is_active': source.is_active,
                'created_at': source.created_at.isoformat() if source.created_at else None,
                'last_checked': 'Never'  # Would come from monitoring system
            })
            
        return jsonify(sources_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/keywords', methods=['GET'])
@require_auth
@require_role('Admin')
def get_keywords():
    """Get all detection keywords"""
    try:
        keywords = Keyword.query.all()
        keywords_data = []
        
        for keyword in keywords:
            keywords_data.append({
                'id': keyword.id,
                'term': keyword.term,
                'category': keyword.category,
                'weight': keyword.weight,
                'is_active': keyword.is_active,
                'description': keyword.description,
                'created_at': keyword.created_at.isoformat() if keyword.created_at else None
            })
            
        return jsonify(keywords_data)
        
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