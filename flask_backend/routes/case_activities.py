"""
Case Activities API Routes
Manage analyst work, notes, findings, and activities on cases
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import CaseActivity, ActivityType, ActivityStatus, Case, SystemUser
from datetime import datetime

bp = Blueprint('case_activities', __name__)

@bp.route('/api/cases/<int:case_id>/activities', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_case_activities(case_id):
    """Get all activities for a case"""
    try:
        # Check if case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'message': 'Case not found'}), 404
        
        # Get query parameters
        activity_type = request.args.get('type')
        include_in_report = request.args.get('include_in_report')
        analyst_id = request.args.get('analyst_id')
        
        # Build query
        query = CaseActivity.query.filter_by(case_id=case_id)
        
        if activity_type:
            query = query.filter_by(activity_type=ActivityType(activity_type))
        
        if include_in_report is not None:
            query = query.filter_by(include_in_report=include_in_report.lower() == 'true')
        
        if analyst_id:
            query = query.filter_by(analyst_id=int(analyst_id))
        
        # Order by date (most recent first)
        activities = query.order_by(CaseActivity.activity_date.desc()).all()
        
        return jsonify({
            'activities': [activity.to_dict(include_relationships=True) for activity in activities],
            'total': len(activities)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching activities: {str(e)}'}), 500


@bp.route('/api/cases/<int:case_id>/activities', methods=['POST'])
# @jwt_required()  # Temporarily disabled for testing
def create_case_activity(case_id):
    """Create a new case activity"""
    try:
        # For testing without JWT, use a default user
        current_user = SystemUser.query.first()  # Get first user as default
        if not current_user:
            return jsonify({'message': 'No users found in database'}), 400
        
        # Check if case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'message': 'Case not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('description'):
            return jsonify({'message': 'Title and description are required'}), 400
        
        # Create activity
        try:
            activity_type = ActivityType(data.get('activity_type', 'NOTE'))
        except ValueError:
            activity_type = ActivityType.NOTE
            
        try:
            status = ActivityStatus(data.get('status', 'ACTIVE'))
        except ValueError:
            status = ActivityStatus.ACTIVE
            
        activity = CaseActivity(
            case_id=case_id,
            analyst_id=current_user.id,
            activity_type=activity_type,
            title=data['title'],
            description=data['description'],
            status=status,
            tags=data.get('tags', []),
            priority=data.get('priority'),
            activity_date=datetime.fromisoformat(data['activity_date']) if data.get('activity_date') else datetime.utcnow(),
            time_spent_minutes=data.get('time_spent_minutes', 0),
            include_in_report=data.get('include_in_report', True),
            is_confidential=data.get('is_confidential', False),
            visibility_level=data.get('visibility_level', 'team')
        )
        
        # Add optional relationships
        if data.get('related_content_ids'):
            activity.related_content_ids = data['related_content_ids']
        
        if data.get('related_source_ids'):
            activity.related_source_ids = data['related_source_ids']
        
        if data.get('attachments'):
            activity.attachments = data['attachments']
        
        if data.get('evidence_links'):
            activity.evidence_links = data['evidence_links']
        
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'message': 'Activity created successfully',
            'activity': activity.to_dict(include_relationships=True)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating activity: {str(e)}")  # Debug print
        return jsonify({'message': f'Error creating activity: {str(e)}'}), 500


@bp.route('/api/cases/<int:case_id>/activities/<int:activity_id>', methods=['GET'])
@jwt_required()
def get_activity(case_id, activity_id):
    """Get a specific activity"""
    try:
        activity = CaseActivity.query.filter_by(id=activity_id, case_id=case_id).first()
        
        if not activity:
            return jsonify({'message': 'Activity not found'}), 404
        
        return jsonify({
            'activity': activity.to_dict(include_relationships=True)
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching activity: {str(e)}'}), 500


@bp.route('/api/cases/<int:case_id>/activities/<int:activity_id>', methods=['PUT'])
@jwt_required()
def update_activity(case_id, activity_id):
    """Update an existing activity"""
    try:
        current_user_email = get_jwt_identity()
        current_user = SystemUser.get_by_email(current_user_email)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        activity = CaseActivity.query.filter_by(id=activity_id, case_id=case_id).first()
        
        if not activity:
            return jsonify({'message': 'Activity not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            activity.title = data['title']
        
        if 'description' in data:
            activity.description = data['description']
        
        if 'activity_type' in data:
            activity.activity_type = ActivityType(data['activity_type'])
        
        if 'status' in data:
            activity.status = ActivityStatus(data['status'])
        
        if 'tags' in data:
            activity.tags = data['tags']
        
        if 'priority' in data:
            activity.priority = data['priority']
        
        if 'activity_date' in data:
            activity.activity_date = datetime.fromisoformat(data['activity_date'])
        
        if 'time_spent_minutes' in data:
            activity.time_spent_minutes = data['time_spent_minutes']
        
        if 'include_in_report' in data:
            activity.include_in_report = data['include_in_report']
        
        if 'is_confidential' in data:
            activity.is_confidential = data['is_confidential']
        
        if 'visibility_level' in data:
            activity.visibility_level = data['visibility_level']
        
        if 'related_content_ids' in data:
            activity.related_content_ids = data['related_content_ids']
        
        if 'related_source_ids' in data:
            activity.related_source_ids = data['related_source_ids']
        
        if 'attachments' in data:
            activity.attachments = data['attachments']
        
        if 'evidence_links' in data:
            activity.evidence_links = data['evidence_links']
        
        # Mark as edited
        activity.mark_edited(current_user.id)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Activity updated successfully',
            'activity': activity.to_dict(include_relationships=True)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error updating activity: {str(e)}'}), 500


@bp.route('/api/cases/<int:case_id>/activities/<int:activity_id>', methods=['DELETE'])
@jwt_required()
def delete_activity(case_id, activity_id):
    """Delete an activity"""
    try:
        current_user_email = get_jwt_identity()
        current_user = SystemUser.get_by_email(current_user_email)
        
        if not current_user:
            return jsonify({'message': 'User not found'}), 404
        
        activity = CaseActivity.query.filter_by(id=activity_id, case_id=case_id).first()
        
        if not activity:
            return jsonify({'message': 'Activity not found'}), 404
        
        # Check if user can delete (owner or admin)
        if activity.analyst_id != current_user.id and current_user.role.value != 'ADMIN':
            return jsonify({'message': 'Unauthorized to delete this activity'}), 403
        
        db.session.delete(activity)
        db.session.commit()
        
        return jsonify({'message': 'Activity deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error deleting activity: {str(e)}'}), 500


@bp.route('/api/cases/<int:case_id>/activities/<int:activity_id>/toggle-report', methods=['POST'])
@jwt_required()
def toggle_report_inclusion(case_id, activity_id):
    """Toggle whether activity should be included in report"""
    try:
        activity = CaseActivity.query.filter_by(id=activity_id, case_id=case_id).first()
        
        if not activity:
            return jsonify({'message': 'Activity not found'}), 404
        
        activity.toggle_report_inclusion()
        db.session.commit()
        
        return jsonify({
            'message': 'Report inclusion toggled',
            'include_in_report': activity.include_in_report
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error toggling report inclusion: {str(e)}'}), 500


@bp.route('/api/cases/<int:case_id>/activities/summary', methods=['GET'])
@jwt_required()
def get_activities_summary(case_id):
    """Get summary of case activities"""
    try:
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'message': 'Case not found'}), 404
        
        # Get all activities
        activities = CaseActivity.query.filter_by(case_id=case_id).all()
        
        # Calculate summary
        total_activities = len(activities)
        total_time_spent = sum(a.time_spent_minutes for a in activities)
        
        # Count by type
        by_type = {}
        for activity in activities:
            activity_type = activity.activity_type.value
            by_type[activity_type] = by_type.get(activity_type, 0) + 1
        
        # Count by analyst
        by_analyst = {}
        for activity in activities:
            analyst_id = activity.analyst_id
            analyst_name = activity.analyst.username if activity.analyst else 'Unknown'
            by_analyst[analyst_name] = by_analyst.get(analyst_name, 0) + 1
        
        # Count report items
        report_items = sum(1 for a in activities if a.include_in_report)
        
        return jsonify({
            'total_activities': total_activities,
            'total_time_spent_minutes': total_time_spent,
            'total_time_spent_hours': round(total_time_spent / 60, 2),
            'by_type': by_type,
            'by_analyst': by_analyst,
            'report_items_count': report_items,
            'recent_activities': [a.to_dict(include_relationships=True) for a in activities[:5]]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching summary: {str(e)}'}), 500

