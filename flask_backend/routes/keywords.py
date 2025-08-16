"""
Keywords API routes
"""
from flask import Blueprint, request, jsonify
from auth import require_auth, require_role
from extensions import db
from models.keyword import Keyword
from sqlalchemy.exc import SQLAlchemyError

keywords_bp = Blueprint('keywords', __name__)

@keywords_bp.route('/', methods=['GET'])
@require_auth
def get_keywords():
    """Get all keywords"""
    try:
        category = request.args.get('category')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 200)
        
        query = Keyword.query
        
        if category:
            query = query.filter(Keyword.category == category)
        
        # Order by weight (highest first) then by term alphabetically
        query = query.order_by(Keyword.weight.desc(), Keyword.term.asc())
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        keywords_data = [keyword.to_dict() for keyword in pagination.items]
        
        return jsonify({
            'status': 'success',
            'data': keywords_data,
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

@keywords_bp.route('/', methods=['POST'])
@require_role('Admin')
def create_keyword():
    """Create new keyword"""
    try:
        data = request.get_json()
        
        required_fields = ['term', 'category', 'weight']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not (1 <= data['weight'] <= 10):
            return jsonify({'error': 'Weight must be between 1 and 10'}), 400
        
        # Create new keyword
        keyword = Keyword(**data)
        db.session.add(keyword)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Keyword created successfully',
            'data': keyword.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keywords_bp.route('/<int:keyword_id>', methods=['PUT'])
@require_role('Admin')
def update_keyword(keyword_id):
    """Update keyword"""
    try:
        data = request.get_json()
        
        if 'weight' in data and not (1 <= data['weight'] <= 10):
            return jsonify({'error': 'Weight must be between 1 and 10'}), 400
        
        keyword = Keyword.query.get(keyword_id)
        
        if not keyword:
            return jsonify({'error': 'Keyword not found'}), 404
        
        # Update keyword attributes
        for key, value in data.items():
            if hasattr(keyword, key) and key not in ['id', 'created_at']:
                setattr(keyword, key, value)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Keyword updated successfully',
            'data': keyword.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@keywords_bp.route('/<int:keyword_id>', methods=['DELETE'])
@require_role('Admin')
def delete_keyword(keyword_id):
    """Delete keyword"""
    try:
        keyword = Keyword.query.get(keyword_id)
        
        if not keyword:
            return jsonify({'error': 'Keyword not found'}), 404
        
        db.session.delete(keyword)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Keyword deleted successfully'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
