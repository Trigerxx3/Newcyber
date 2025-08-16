from flask import Blueprint, request, jsonify
from models.content import Content
from models.source import Source
from models.osint_result import OSINTResult
from extensions import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
def dashboard_root():
    """Root Dashboard endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Dashboard API is running',
        'endpoints': {
            'stats': '/stats (GET)',
            'recent_content': '/recent-content (GET)',
            'high_risk_content': '/high-risk-content (GET)',
            'trends': '/trends (GET)',
            'alerts': '/alerts (GET)'
        }
    }), 200

@dashboard_bp.route('/stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Get date range for filtering
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Content statistics
        total_content = Content.query.count()
        recent_content = Content.query.filter(
            Content.created_at >= start_date
        ).count()
        
        # Risk level distribution
        risk_distribution = db.session.query(
            Content.risk_level,
            func.count(Content.id)
        ).group_by(Content.risk_level).all()
        
        # Source statistics
        total_sources = Source.query.count()
        active_sources = Source.query.filter_by(is_active=True).count()
        
        # OSINT statistics
        total_osint_searches = OSINTResult.query.count()
        recent_osint_searches = OSINTResult.query.filter(
            OSINTResult.created_at >= start_date
        ).count()
        
        # Content by source
        content_by_source = db.session.query(
            Source.name,
            func.count(Content.id)
        ).join(Content).group_by(Source.name).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'content': {
                    'total': total_content,
                    'recent': recent_content,
                    'risk_distribution': dict(risk_distribution)
                },
                'sources': {
                    'total': total_sources,
                    'active': active_sources
                },
                'osint': {
                    'total_searches': total_osint_searches,
                    'recent_searches': recent_osint_searches
                },
                'content_by_source': dict(content_by_source),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@dashboard_bp.route('/recent-content', methods=['GET'])
def get_recent_content():
    """Get recent content for dashboard"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        recent_content = Content.query.order_by(
            Content.created_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'data': [content.to_dict() for content in recent_content]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@dashboard_bp.route('/high-risk-content', methods=['GET'])
def get_high_risk_content():
    """Get high-risk content"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        high_risk_content = Content.query.filter(
            Content.risk_level.in_(['high', 'critical'])
        ).order_by(Content.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'status': 'success',
            'data': [content.to_dict() for content in high_risk_content]
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@dashboard_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get content trends over time"""
    try:
        days = request.args.get('days', 30, type=int)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Daily content creation trends
        daily_content = db.session.query(
            func.date(Content.created_at),
            func.count(Content.id)
        ).filter(
            Content.created_at >= start_date
        ).group_by(func.date(Content.created_at)).all()
        
        # Risk level trends
        risk_trends = db.session.query(
            func.date(Content.created_at),
            Content.risk_level,
            func.count(Content.id)
        ).filter(
            Content.created_at >= start_date
        ).group_by(func.date(Content.created_at), Content.risk_level).all()
        
        return jsonify({
            'status': 'success',
            'data': {
                'daily_content': [{'date': str(date), 'count': count} for date, count in daily_content],
                'risk_trends': [{'date': str(date), 'risk_level': risk, 'count': count} for date, risk, count in risk_trends]
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@dashboard_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get system alerts and notifications"""
    try:
        # This would typically integrate with an alerting system
        # For now, we'll return a mock structure
        alerts = [
            {
                'id': 1,
                'type': 'high_risk_content',
                'message': 'New high-risk content detected',
                'severity': 'high',
                'timestamp': datetime.now().isoformat(),
                'read': False
            },
            {
                'id': 2,
                'type': 'source_failure',
                'message': 'Source "Dark Web Monitor" is not responding',
                'severity': 'medium',
                'timestamp': (datetime.now() - timedelta(hours=2)).isoformat(),
                'read': True
            }
        ]
        
        return jsonify({
            'status': 'success',
            'data': alerts
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@dashboard_bp.route('/alerts/<int:alert_id>/read', methods=['PUT'])
def mark_alert_read(alert_id):
    """Mark an alert as read"""
    try:
        # This would typically update the alert status in the database
        # For now, we'll return a success response
        return jsonify({
            'status': 'success',
            'message': 'Alert marked as read'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500 