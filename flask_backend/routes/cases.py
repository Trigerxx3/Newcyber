"""
Cases API routes
"""
from flask import Blueprint, request, jsonify
from auth import require_auth, require_role
from extensions import db
from models.case import Case, CaseStatus
from models.user_case_link import UserCaseLink
from models.user import User
from models.source import Source
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

cases_bp = Blueprint('cases', __name__)

@cases_bp.route('/', methods=['GET'])
@require_auth
def get_cases():
    """Get all cases"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        query = Case.query
        
        if status:
            # Convert string status to enum
            try:
                status_enum = CaseStatus(status.lower().replace(' ', '_'))
                query = query.filter(Case.status == status_enum)
            except ValueError:
                return jsonify({'error': 'Invalid status'}), 400
        
        # Order by creation date (newest first)
        query = query.order_by(Case.created_at.desc())
        
        # Get paginated results
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        cases_data = []
        for case in pagination.items:
            case_dict = case.to_dict()
            # Get user count for each case
            user_count = db.session.query(func.count(UserCaseLink.user_id)).filter_by(case_id=case.id).scalar()
            case_dict['user_count'] = user_count or 0
            cases_data.append(case_dict)
        
        return jsonify({
            'status': 'success',
            'data': cases_data,
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

@cases_bp.route('/', methods=['POST'])
@require_auth
def create_case():
    """Create new case"""
    try:
        data = request.get_json()
        
        # Note: Case model uses 'title' not 'case_name'
        required_fields = ['title']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new case
        case = Case(**data)
        db.session.add(case)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Case created successfully',
            'data': case.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>', methods=['GET'])
@require_auth
def get_case(case_id):
    """Get specific case with linked users"""
    try:
        case = Case.query.get(case_id)
        
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        case_data = case.to_dict()
        
        # Get linked users with their source information
        user_links = db.session.query(UserCaseLink).filter(
            UserCaseLink.case_id == case_id
        ).all()
        
        linked_users = []
        for link in user_links:
            link_data = link.to_dict()
            # Get the user information separately
            user = User.query.get(link.user_id)
            if user:
                link_data['user'] = user.to_dict()
            linked_users.append(link_data)
        
        case_data['linked_users'] = linked_users
        
        return jsonify({
            'status': 'success',
            'data': case_data
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/users', methods=['POST'])
@require_auth
def link_user_to_case(case_id):
    """Link user to case"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        # Check if case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if link already exists
        existing = UserCaseLink.query.filter_by(case_id=case_id, user_id=user_id).first()
        
        if existing:
            return jsonify({'error': 'User already linked to this case'}), 400
        
        # Create new link
        user_case_link = UserCaseLink(
            case_id=case_id,
            user_id=user_id,
            **{k: v for k, v in data.items() if k not in ['case_id', 'user_id']}
        )
        
        db.session.add(user_case_link)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'User linked to case successfully',
            'data': user_case_link.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/status', methods=['PUT'])
@require_auth
def update_case_status(case_id):
    """Update case status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        # Convert status string to enum
        try:
            status_enum = CaseStatus(status.lower().replace(' ', '_'))
        except ValueError:
            valid_statuses = [status.value for status in CaseStatus]
            return jsonify({'error': f'Invalid status. Valid options: {valid_statuses}'}), 400
        
        case = Case.query.get(case_id)
        
        if not case:
            return jsonify({'error': 'Case not found'}), 404
        
        case.status = status_enum
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Case status updated successfully',
            'data': case.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
