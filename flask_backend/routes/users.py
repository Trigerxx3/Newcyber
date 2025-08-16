"""
Platform Users API routes (monitored users, not system users)
"""
from flask import Blueprint, request, jsonify
from auth import require_auth, require_role
from extensions import db
from models.user import User
from models.content import Content
from models.identifier import Identifier
from sqlalchemy.exc import SQLAlchemyError

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@require_auth
def get_users():
    """Get all platform users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        flagged_only = request.args.get('flagged', 'false').lower() == 'true'
        
        query = User.query
        
        if flagged_only:
            query = query.filter(User.is_flagged == True)
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'status': 'success',
            'data': users,
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

@users_bp.route('/', methods=['POST'])
@require_auth
def create_user():
    """Create new platform user"""
    try:
        data = request.get_json()
        
        required_fields = ['source_id', 'username']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User created successfully',
            'data': user.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    """Get specific user with related data"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user_data = user.to_dict()
        
        # Get user's content (recent 10)
        recent_content = Content.query.filter_by(user_id=user_id).limit(10).all()
        user_data['recent_content'] = [content.to_dict() for content in recent_content]
        
        # Get user's identifiers
        identifiers = Identifier.query.filter_by(user_id=user_id).all()
        user_data['identifiers'] = [identifier.to_dict() for identifier in identifiers]
        
        return jsonify({
            'status': 'success',
            'data': user_data
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@users_bp.route('/<int:user_id>/flag', methods=['PUT'])
@require_auth
def flag_user(user_id):
    """Flag/unflag user"""
    try:
        data = request.get_json()
        is_flagged = data.get('is_flagged', True)
        
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_flagged = is_flagged
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'User {"flagged" if is_flagged else "unflagged"} successfully',
            'data': user.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
