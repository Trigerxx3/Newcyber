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


@bp.route('/api/analysts/<int:analyst_id>/activities', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_analyst_activities(analyst_id):
    """Get all activities for a specific analyst across all cases"""
    try:
        # Check if analyst exists
        analyst = SystemUser.query.get(analyst_id)
        if not analyst:
            return jsonify({'message': 'Analyst not found'}), 404
        
        # Get query parameters
        case_id = request.args.get('case_id')
        activity_type = request.args.get('type')
        include_in_report = request.args.get('include_in_report')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Build query
        query = CaseActivity.query.filter_by(analyst_id=analyst_id)
        
        if case_id:
            query = query.filter_by(case_id=case_id)
        
        if activity_type:
            query = query.filter_by(activity_type=ActivityType(activity_type))
        
        if include_in_report is not None:
            query = query.filter_by(include_in_report=include_in_report.lower() == 'true')
        
        # Order by date (most recent first) and paginate
        activities = query.order_by(CaseActivity.activity_date.desc()).offset(offset).limit(limit).all()
        
        # Get total count for pagination
        total_count = query.count()
        
        # Calculate summary statistics
        all_activities = CaseActivity.query.filter_by(analyst_id=analyst_id).all()
        total_time_spent = sum(a.time_spent_minutes for a in all_activities)
        
        # Count by type
        by_type = {}
        for activity in all_activities:
            activity_type = activity.activity_type.value
            by_type[activity_type] = by_type.get(activity_type, 0) + 1
        
        # Count by case
        by_case = {}
        for activity in all_activities:
            case_title = activity.case.title if activity.case else 'Unknown Case'
            by_case[case_title] = by_case.get(case_title, 0) + 1
        
        # Count report items
        report_items = sum(1 for a in all_activities if a.include_in_report)
        
        summary = {
            'total_activities': len(all_activities),
            'total_time_spent_minutes': total_time_spent,
            'total_time_spent_hours': round(total_time_spent / 60, 2),
            'by_type': by_type,
            'by_case': by_case,
            'report_items_count': report_items
        }
        
        return jsonify({
            'activities': [activity.to_dict(include_relationships=True) for activity in activities],
            'summary': summary,
            'pagination': {
                'total': total_count,
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching analyst activities: {str(e)}'}), 500


@bp.route('/api/analysts/<int:analyst_id>/activities/summary', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def get_analyst_activities_summary(analyst_id):
    """Get comprehensive summary of analyst activities and performance metrics"""
    try:
        # Check if analyst exists
        analyst = SystemUser.query.get(analyst_id)
        if not analyst:
            return jsonify({'message': 'Analyst not found'}), 404
        
        # Get all activities for this analyst
        activities = CaseActivity.query.filter_by(analyst_id=analyst_id).all()
        
        if not activities:
            return jsonify({
                'analyst': {
                    'id': analyst.id,
                    'username': analyst.username,
                    'email': analyst.email,
                    'role': analyst.role.value if analyst.role else 'Unknown'
                },
                'summary': {
                    'total_activities': 0,
                    'total_time_spent_minutes': 0,
                    'total_time_spent_hours': 0,
                    'by_type': {},
                    'by_case': {},
                    'by_month': {},
                    'report_items_count': 0,
                    'average_activity_duration': 0,
                    'most_productive_day': None,
                    'activity_trend': []
                },
                'performance_metrics': {
                    'productivity_score': 0,
                    'consistency_score': 0,
                    'quality_score': 0,
                    'collaboration_score': 0
                }
            }), 200
        
        # Calculate basic statistics
        total_activities = len(activities)
        total_time_spent = sum(a.time_spent_minutes for a in activities)
        
        # Count by type
        by_type = {}
        for activity in activities:
            activity_type = activity.activity_type.value
            by_type[activity_type] = by_type.get(activity_type, 0) + 1
        
        # Count by case
        by_case = {}
        for activity in activities:
            case_title = activity.case.title if activity.case else 'Unknown Case'
            by_case[case_title] = by_case.get(case_title, 0) + 1
        
        # Count by month (for trend analysis)
        by_month = {}
        for activity in activities:
            month_key = activity.activity_date.strftime('%Y-%m')
            by_month[month_key] = by_month.get(month_key, 0) + 1
        
        # Count report items
        report_items = sum(1 for a in activities if a.include_in_report)
        
        # Calculate performance metrics
        # Productivity: activities per day
        if activities:
            date_range = (max(a.activity_date for a in activities) - min(a.activity_date for a in activities)).days + 1
            productivity_score = min(100, (total_activities / max(1, date_range)) * 10)
        else:
            productivity_score = 0
        
        # Consistency: regularity of activity
        if len(by_month) > 1:
            monthly_counts = list(by_month.values())
            consistency_score = min(100, 100 - (max(monthly_counts) - min(monthly_counts)) / max(monthly_counts) * 100)
        else:
            consistency_score = 100
        
        # Quality: percentage of activities marked for reports
        quality_score = (report_items / total_activities * 100) if total_activities > 0 else 0
        
        # Collaboration: working on multiple cases
        collaboration_score = min(100, len(by_case) * 20) if by_case else 0
        
        # Activity trend (last 6 months)
        activity_trend = []
        from datetime import datetime, timedelta
        for i in range(6):
            month_date = datetime.now() - timedelta(days=30*i)
            month_key = month_date.strftime('%Y-%m')
            activity_trend.append({
                'month': month_key,
                'count': by_month.get(month_key, 0)
            })
        activity_trend.reverse()
        
        # Most productive day of week
        by_day = {}
        for activity in activities:
            day = activity.activity_date.strftime('%A')
            by_day[day] = by_day.get(day, 0) + 1
        most_productive_day = max(by_day.items(), key=lambda x: x[1])[0] if by_day else None
        
        # Average activity duration
        avg_duration = total_time_spent / total_activities if total_activities > 0 else 0
        
        return jsonify({
            'analyst': {
                'id': analyst.id,
                'username': analyst.username,
                'email': analyst.email,
                'role': analyst.role.value if analyst.role else 'Unknown'
            },
            'summary': {
                'total_activities': total_activities,
                'total_time_spent_minutes': total_time_spent,
                'total_time_spent_hours': round(total_time_spent / 60, 2),
                'by_type': by_type,
                'by_case': by_case,
                'by_month': by_month,
                'report_items_count': report_items,
                'average_activity_duration': round(avg_duration, 1),
                'most_productive_day': most_productive_day,
                'activity_trend': activity_trend
            },
            'performance_metrics': {
                'productivity_score': round(productivity_score, 1),
                'consistency_score': round(consistency_score, 1),
                'quality_score': round(quality_score, 1),
                'collaboration_score': round(collaboration_score, 1)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching analyst summary: {str(e)}'}), 500
