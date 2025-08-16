"""
Sources API routes
"""
from flask import Blueprint, request, jsonify
from auth import require_auth, require_role
from extensions import db
from models.source import Source
from sqlalchemy.exc import SQLAlchemyError

sources_bp = Blueprint('sources', __name__)

@sources_bp.route('/', methods=['GET'])
@require_auth
def get_sources():
    """Get all sources with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        platform = request.args.get('platform')
        
        query = Source.query
        
        if platform:
            query = query.filter(Source.platform == platform)
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        sources = [source.to_dict() for source in pagination.items]
        
        return jsonify({
            'status': 'success',
            'data': sources,
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

@sources_bp.route('/', methods=['POST'])
@require_role('Admin')
def create_source():
    """Create new source"""
    try:
        data = request.get_json()
        
        required_fields = ['platform', 'source_handle']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new source
        source = Source(**data)
        db.session.add(source)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Source created successfully',
            'data': source.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@sources_bp.route('/<int:source_id>', methods=['GET'])
@require_auth
def get_source(source_id):
    """Get specific source"""
    try:
        source = Source.query.get(source_id)
        
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': source.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@sources_bp.route('/<int:source_id>', methods=['PUT'])
@require_role('Admin')
def update_source(source_id):
    """Update source"""
    try:
        data = request.get_json()
        source = Source.query.get(source_id)
        
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        # Update source attributes
        for key, value in data.items():
            if hasattr(source, key) and key not in ['id', 'created_at']:
                setattr(source, key, value)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Source updated successfully',
            'data': source.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@sources_bp.route('/<int:source_id>', methods=['DELETE'])
@require_role('Admin')
def delete_source(source_id):
    """Delete source"""
    try:
        source = Source.query.get(source_id)
        
        if not source:
            return jsonify({'error': 'Source not found'}), 404
        
        db.session.delete(source)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Source deleted successfully'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
