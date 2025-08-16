"""
Content API routes
"""
from flask import Blueprint, request, jsonify
from auth import require_auth, require_role
from extensions import db
from models.content import Content
from models.user import User
from models.source import Source
from models.detection import Detection
from models.keyword import Keyword
from sqlalchemy.exc import SQLAlchemyError

content_bp = Blueprint('content', __name__)

@content_bp.route('/', methods=['GET'])
@require_auth
def get_content():
    """Get content with filtering and pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        min_score = request.args.get('min_score', type=int)
        source_id = request.args.get('source_id', type=int)
        user_id = request.args.get('user_id', type=int)
        
        query = Content.query
        
        # Apply filters
        if min_score is not None:
            query = query.filter(Content.suspicion_score >= min_score)
        if source_id:
            query = query.filter(Content.source_id == source_id)
        if user_id:
            query = query.filter(Content.user_id == user_id)
        
        # Order by suspicion score and date (highest score and newest first)
        query = query.order_by(
            Content.suspicion_score.desc(),
            Content.posted_at.desc()
        )
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        content_data = [content.to_dict() for content in pagination.items]
        
        return jsonify({
            'status': 'success',
            'data': content_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@content_bp.route('/', methods=['POST'])
@require_auth
def create_content():
    """Create new content"""
    try:
        data = request.get_json()
        
        required_fields = ['source_id', 'user_id', 'text_content']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new content
        content = Content(**data)
        db.session.add(content)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Content created successfully',
            'data': content.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@content_bp.route('/<int:content_id>', methods=['GET'])
@require_auth
def get_content_item(content_id):
    """Get specific content with detections"""
    try:
        content = Content.query.get(content_id)
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        content_data = content.to_dict()
        
        # Get detections for this content
        detections = Detection.query.filter_by(content_id=content_id).all()
        content_data['detections'] = [detection.to_dict() for detection in detections]
        
        return jsonify({
            'status': 'success',
            'data': content_data
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@content_bp.route('/<int:content_id>/score', methods=['PUT'])
@require_auth
def update_content_score(content_id):
    """Update content suspicion score"""
    try:
        data = request.get_json()
        score = data.get('suspicion_score')
        
        if score is None or not (0 <= score <= 100):
            return jsonify({'error': 'Invalid suspicion score (0-100)'}), 400
        
        content = Content.query.get(content_id)
        
        if not content:
            return jsonify({'error': 'Content not found'}), 404
        
        content.suspicion_score = score
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Content score updated successfully',
            'data': content.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@content_bp.route('/high-risk', methods=['GET'])
@require_auth
def get_high_risk_content():
    """Get high-risk content (score >= 70)"""
    try:
        # Get high-risk content ordered by suspicion score (highest first)
        high_risk_content = Content.query.filter(
            Content.suspicion_score >= 70
        ).order_by(
            Content.suspicion_score.desc()
        ).limit(50).all()
        
        content_data = [content.to_dict() for content in high_risk_content]
        
        return jsonify({
            'status': 'success',
            'data': content_data
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
