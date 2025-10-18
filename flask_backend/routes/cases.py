"""
Cases API routes
"""
from flask import Blueprint, request, jsonify
from auth import require_auth, require_role
from extensions import db
from models.case import Case, CaseStatus
from models.active_case import ActiveCase
from models.user_case_link import UserCaseLink
from models.user import User
from models.source import Source
from models.case_request import CaseRequest, RequestStatus
from services.case_service import CaseService
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func

cases_bp = Blueprint('cases', __name__)
case_service = CaseService()

@cases_bp.route('/', methods=['GET'])
@require_auth
def get_cases():
    """Get all cases"""
    try:
        current_user = getattr(request, 'current_user', None)
        current_user_id = current_user.id if current_user else None
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        case_type = request.args.get('type')
        assigned_to_id = request.args.get('assigned_to_id', type=int)
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Use case service
        success, message, data = case_service.get_all_cases(
            status=status,
            priority=priority,
            case_type=case_type,
            assigned_to_id=assigned_to_id,
            page=page,
            per_page=per_page,
            current_user_id=current_user_id
        )
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'data': data['cases'],
            'pagination': data['pagination']
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/', methods=['POST'])
@require_auth
def create_case():
    """Create new case"""
    try:
        data = request.get_json()
        
        # Required fields
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        # Get current user ID from auth context
        current_user = getattr(request, 'current_user', None)
        created_by_id = current_user.id if current_user else None
        
        # Check if user can create a case directly
        can_create, check_message = case_service.can_create_case(created_by_id)
        
        if not can_create:
            # User cannot create case directly, create a request instead
            success, message, case_request = case_service.create_case_request(
                title=data['title'],
                description=data.get('description'),
                case_type=data.get('type'),
                priority=data.get('priority'),
                summary=data.get('summary'),
                objectives=data.get('objectives'),
                methodology=data.get('methodology'),
                tags=data.get('tags'),
                requested_by_id=created_by_id
            )
            
            if success:
                return jsonify({
                    'status': 'success',
                    'message': message,
                    'requires_approval': True,
                    'request_id': case_request.id
                }), 201
            else:
                return jsonify({'status': 'error', 'message': message}), 400
        
        # User can create case directly
        success, message, case = case_service.create_case(
            title=data['title'],
            description=data.get('description'),
            case_type=data.get('type'),
            priority=data.get('priority'),
            created_by_id=created_by_id,
            **{k: v for k, v in data.items() if k not in ['title', 'description', 'type', 'priority']}
        )
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        # Set this new case as the active case for the creator
        try:
            active = ActiveCase.query.filter_by(user_id=created_by_id).first()
            if active:
                active.case_id = case.id
            else:
                active = ActiveCase(user_id=created_by_id, case_id=case.id)
                db.session.add(active)
            db.session.commit()
        except Exception:
            db.session.rollback()
            # Do not fail case creation if active-case setting fails
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': case.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>', methods=['GET'])
@require_auth
def get_case(case_id):
    """Get specific case with linked users"""
    try:
        # Use case service
        success, message, case_data = case_service.get_case_details(case_id)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 404
        
        return jsonify({
            'status': 'success',
            'data': case_data
        }), 200
        
    except Exception as e:
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
        
        # Get current user ID from auth context
        assigned_by_id = getattr(request, 'user_id', None)
        
        # Use case service
        success, message, user_case_link = case_service.link_user_to_case(
            user_id=user_id,
            case_id=case_id,
            role=data.get('role'),
            assigned_by_id=assigned_by_id,
            assignment_reason=data.get('assignment_reason'),
            **{k: v for k, v in data.items() if k not in ['user_id', 'role', 'assignment_reason']}
        )
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': user_case_link.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/content', methods=['POST'])
@require_auth
def link_content_to_case(case_id):
    """Attach one or more content items to a case"""
    try:
        data = request.get_json() or {}
        content_ids = data.get('content_ids', [])
        if not isinstance(content_ids, list) or not content_ids:
            return jsonify({'status': 'error', 'message': 'content_ids (non-empty list) required'}), 400
        success, message, created = case_service.link_content_to_case(case_id, content_ids)
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        return jsonify({'status': 'success', 'message': message, 'created': created}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/content/<int:content_id>', methods=['DELETE'])
@require_auth
def unlink_content_from_case(case_id, content_id):
    try:
        success, message = case_service.unlink_content_from_case(case_id, content_id)
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        return jsonify({'status': 'success', 'message': message}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/status', methods=['PUT'])
@require_auth
def update_case_status(case_id):
    """Update case status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        # Use case service
        success, message, case = case_service.update_case_status(case_id, status)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': case.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/close', methods=['PUT'])
@require_auth
def close_case(case_id):
    """Close a case with notes"""
    try:
        data = request.get_json()
        notes = data.get('notes', '')
        
        # Get current user ID from auth context
        closed_by_id = getattr(request, 'user_id', None)
        
        # Use case service
        success, message, case = case_service.close_case(
            case_id=case_id,
            notes=notes,
            closed_by_id=closed_by_id
        )
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': case.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/users/<int:user_id>', methods=['DELETE'])
@require_auth
def unlink_user_from_case(case_id, user_id):
    """Unlink user from case"""
    try:
        # Use case service
        success, message = case_service.unlink_user_from_case(user_id, case_id)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/<int:case_id>/progress', methods=['PUT'])
@require_auth
def update_case_progress(case_id):
    """Update case progress percentage"""
    try:
        data = request.get_json()
        progress = data.get('progress_percentage')
        
        if progress is None:
            return jsonify({'error': 'progress_percentage is required'}), 400
        
        # Use case service
        success, message, case = case_service.update_case_progress(case_id, progress)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': case.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/user/<int:user_id>', methods=['GET'])
@require_auth
def get_cases_by_user(user_id):
    """Get all cases linked to a specific user"""
    try:
        role = request.args.get('role')
        
        # Use case service
        success, message, cases = case_service.get_cases_by_user(user_id, role)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'data': cases
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/active', methods=['GET'])
@require_auth
def get_active_case():
    """Get the active case for the current user"""
    try:
        current_user = getattr(request, 'current_user', None)
        if not current_user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        active = ActiveCase.query.filter_by(user_id=current_user.id).first()
        if not active:
            return jsonify({'status': 'success', 'data': None}), 200
        case = Case.query.get(active.case_id)
        return jsonify({'status': 'success', 'data': case.to_dict() if case else None}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/active', methods=['POST'])
@require_auth
def set_active_case():
    """Set the active case for the current user"""
    try:
        current_user = getattr(request, 'current_user', None)
        if not current_user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        data = request.get_json() or {}
        case_id = data.get('case_id')
        if not case_id:
            return jsonify({'status': 'error', 'message': 'case_id is required'}), 400
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'status': 'error', 'message': 'Case not found'}), 404
        active = ActiveCase.query.filter_by(user_id=current_user.id).first()
        if active:
            active.case_id = case_id
        else:
            active = ActiveCase(user_id=current_user.id, case_id=case_id)
            db.session.add(active)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Active case set', 'data': case.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/active', methods=['DELETE'])
@require_auth
def clear_active_case():
    """Clear the active case for the current user"""
    try:
        current_user = getattr(request, 'current_user', None)
        if not current_user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        ActiveCase.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Active case cleared'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/statistics', methods=['GET'])
@require_auth
def get_case_statistics():
    """Get overall case statistics"""
    try:
        # Use case service
        success, message, stats = case_service.get_case_statistics()
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Case Request Routes
@cases_bp.route('/requests', methods=['GET'])
@require_auth
def get_case_requests():
    """Get case creation requests"""
    try:
        status = request.args.get('status')
        requested_by_id = request.args.get('requested_by_id', type=int)
        
        # Get current user
        current_user = getattr(request, 'current_user', None)
        user_id = current_user.id if current_user else None
        
        # Non-admins can only see their own requests
        if not current_user or current_user.role.value != 'Admin':
            requested_by_id = user_id
        
        success, message, requests = case_service.get_case_requests(status, requested_by_id)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'data': [req.to_dict() for req in requests]
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@require_auth
@require_role('Admin')
def approve_case_request(request_id):
    """Approve a case creation request (Admin only)"""
    try:
        data = request.get_json() or {}
        review_notes = data.get('review_notes', '')
        
        # Get current user
        current_user = getattr(request, 'current_user', None)
        reviewed_by_id = current_user.id if current_user else None
        
        success, message, case = case_service.approve_case_request(request_id, reviewed_by_id, review_notes)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message,
            'data': case.to_dict() if case else None
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/requests/<int:request_id>/reject', methods=['POST'])
@require_auth
@require_role('Admin')
def reject_case_request(request_id):
    """Reject a case creation request (Admin only)"""
    try:
        data = request.get_json() or {}
        review_notes = data.get('review_notes', '')
        
        if not review_notes:
            return jsonify({'status': 'error', 'message': 'Review notes are required for rejection'}), 400
        
        # Get current user
        current_user = getattr(request, 'current_user', None)
        reviewed_by_id = current_user.id if current_user else None
        
        success, message = case_service.reject_case_request(request_id, reviewed_by_id, review_notes)
        
        if not success:
            return jsonify({'status': 'error', 'message': message}), 400
        
        return jsonify({
            'status': 'success',
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@cases_bp.route('/can-create', methods=['GET'])
@require_auth
def can_create_case():
    """Check if current user can create a new case"""
    try:
        # Get current user
        current_user = getattr(request, 'current_user', None)
        user_id = current_user.id if current_user else None
        
        if not user_id:
            return jsonify({'status': 'error', 'message': 'User not authenticated'}), 401
        
        can_create, message = case_service.can_create_case(user_id)
        
        return jsonify({
            'status': 'success',
            'can_create': can_create,
            'message': message
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
