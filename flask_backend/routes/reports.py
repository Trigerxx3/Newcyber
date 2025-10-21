"""
Reports API routes for generating and downloading investigation reports
"""
import os
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.exceptions import NotFound, BadRequest
from datetime import datetime

from extensions import db
from models.case import Case
from models.user import SystemUser, User
from models.active_case import ActiveCase
from models.content import Content
from models.osint_result import OSINTResult
from models.source import Source
from services.narcotics_report_generator import NarcoticsReportGenerator
from models.user_case_link import UserCaseLink

# Create blueprint
reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@reports_bp.route('/<int:case_id>/generate', methods=['GET'])
@jwt_required()
def generate_case_report(case_id):
    """
    Generate a PDF report for a specific case
    
    Args:
        case_id (int): The ID of the case to generate report for
        
    Returns:
        PDF file download
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = SystemUser.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': f'Case with ID {case_id} not found'}), 404
        
        # Enforce user access: analyst must be linked to the case
        if not db.session.query(UserCaseLink).filter_by(user_id=current_user.id, case_id=case_id).first():
            return jsonify({'error': 'You do not have access to this case'}), 403
        
        # Generate the report
        try:
            # Use the Narcotics Intelligence Platform report generator
            from services.narcotics_report_generator import generate_case_pdf_report
            
            # Get activities and content for the case
            from models.case_activity import CaseActivity
            from models.case_content_link import CaseContentLink
            
            # Get activities
            activities = CaseActivity.query.filter_by(
                case_id=case_id,
                include_in_report=True
            ).order_by(CaseActivity.activity_date.desc()).all()
            
            # Get related content
            content_links = db.session.query(CaseContentLink).filter_by(case_id=case_id).all()
            content_items = None
            if content_links:
                content_ids = [link.content_id for link in content_links]
                content_items = Content.query.filter(Content.id.in_(content_ids)).all()
            
            # Generate PDF using Narcotics Intelligence Platform format
            pdf_buffer = generate_case_pdf_report(
                case=case,
                activities=activities,
                content_items=content_items
            )
            
            # Update case's updated_at timestamp
            case.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Prepare filename
            filename = f"Case_{case.case_number}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Return the PDF file
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
            
        except Exception as e:
            current_app.logger.error(f"Error generating report for case {case_id}: {str(e)}")
            return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Unexpected error in generate_case_report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@reports_bp.route('/<int:case_id>/preview', methods=['GET'])
@jwt_required()
def preview_case_report(case_id):
    """
    Get a preview of the report data without generating the PDF
    
    Args:
        case_id (int): The ID of the case to preview
        
    Returns:
        JSON with report preview data
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = SystemUser.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if case exists
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': f'Case with ID {case_id} not found'}), 404
        # Ensure linkage
        if not db.session.query(UserCaseLink).filter_by(user_id=current_user.id, case_id=case_id).first():
            return jsonify({'error': 'You do not have access to this case'}), 403
        
        # Get case data for preview
        from models.case_content_link import CaseContentLink
        
        # Get related content
        content_links = db.session.query(CaseContentLink).filter_by(case_id=case_id).all()
        content_items = None
        if content_links:
            content_ids = [link.content_id for link in content_links]
            content_items = Content.query.filter(Content.id.in_(content_ids)).all()
        
        # Get OSINT results
        osint_results = OSINTResult.query.filter_by(case_id=case_id).all()
        
        # Get platform users (if any)
        platform_users = []  # This would need to be implemented based on your data model
        
        # Prepare preview data
        preview_data = {
            'case': {
                'id': case.id,
                'title': case.title,
                'case_number': case.case_number,
                'status': case.status.value if case.status else None,
                'priority': case.priority.value if case.priority else None,
                'created_at': case.created_at.isoformat(),
                'updated_at': case.updated_at.isoformat()
            },
            'statistics': {
                'platforms_analyzed': 'None',  # Default value
                'flagged_users': len(platform_users),
                'flagged_posts': len(content_items) if content_items else 0,
                'osint_results': len(osint_results)
            },
            'flagged_content_summary': [
                {
                    'id': content.id,
                    'author': content.author or 'Unknown',
                    'platform': content.source.platform.value if content.source and content.source.platform else 'Unknown',
                    'suspicion_score': content.suspicion_score or 0,
                    'risk_level': content.risk_level.value if content.risk_level else 'Low',
                    'intent': content.intent or 'Unknown',
                    'created_at': content.created_at.isoformat() if content.created_at else datetime.utcnow().isoformat()
                }
                for content in (content_items or [])[:5]  # Limit to first 5
            ],
            'osint_results_summary': [
                {
                    'id': result.id,
                    'query': result.query or 'Unknown',
                    'search_type': result.search_type.value if result.search_type else 'Unknown',
                    'status': result.status.value if result.status else 'Unknown',
                    'risk_score': result.risk_score or 0,
                    'created_at': result.created_at.isoformat() if result.created_at else datetime.utcnow().isoformat()
                }
                for result in osint_results[:5]  # Limit to first 5
            ]
        }
        
        return jsonify({
            'success': True,
            'data': preview_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in preview_case_report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@reports_bp.route('/active/generate', methods=['GET'])
@jwt_required()
def generate_active_case_report():
    """Generate a PDF report for the current user's active case"""
    try:
        current_user_id = get_jwt_identity()
        current_user = SystemUser.query.get(current_user_id)
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        active = ActiveCase.query.filter_by(user_id=current_user.id).first()
        if not active:
            return jsonify({'error': 'No active case set'}), 400
        case_id = active.case_id
        pdf_path = report_generator.generate_case_report(case_id)
        case = Case.query.get(case_id)
        case.updated_at = datetime.utcnow()
        db.session.commit()
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Case_{case_id}_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        current_app.logger.error(f"Error generating active case report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@reports_bp.route('/active/preview', methods=['GET'])
@jwt_required()
def preview_active_case_report():
    """Preview report for current user's active case"""
    try:
        current_app.logger.info("Starting preview_active_case_report")
        
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"Current user ID: {current_user_id}")
        
        current_user = SystemUser.query.get(current_user_id)
        if not current_user:
            current_app.logger.error("User not found")
            return jsonify({'error': 'User not found'}), 404
        
        current_app.logger.info(f"User found: {current_user.username}")
        
        active = ActiveCase.query.filter_by(user_id=current_user.id).first()
        if not active:
            current_app.logger.info("No active case found for user")
            # Return 200 with null data so frontend can gracefully handle absence
            return jsonify({'success': True, 'data': None}), 200
        
        current_app.logger.info(f"Active case found: {active.case_id}")
        case_id = active.case_id
        
        case = Case.query.get(case_id)
        if not case:
            current_app.logger.error(f"Case with ID {case_id} not found")
            return jsonify({'success': True, 'data': None}), 200
        
        current_app.logger.info(f"Case found: {case.title}")
        
        # Initialize counters
        content_count = 0
        osint_count = 0
        
        # Try to get content count with error handling
        try:
            current_app.logger.info("Getting content links...")
            from models.case_content_link import CaseContentLink
            content_links = db.session.query(CaseContentLink).filter_by(case_id=case_id).all()
            content_count = len(content_links)
            current_app.logger.info(f"Found {content_count} content links")
        except Exception as e:
            current_app.logger.warning(f"Could not get content links: {str(e)}")
            content_count = 0
        
        # Try to get OSINT results with error handling
        try:
            current_app.logger.info("Getting OSINT results...")
            osint_results = OSINTResult.query.filter_by(case_id=case_id).all()
            osint_count = len(osint_results)
            current_app.logger.info(f"Found {osint_count} OSINT results")
        except Exception as e:
            current_app.logger.warning(f"Could not get OSINT results: {str(e)}")
            osint_count = 0
        
        current_app.logger.info("Creating preview data...")
        preview_data = {
            'case': {
                'id': case.id,
                'title': case.title or 'Untitled',
                'case_number': case.case_number or 'N/A',
                'status': case.status.value if hasattr(case.status, 'value') else str(case.status) if case.status else 'Unknown',
                'priority': case.priority.value if hasattr(case.priority, 'value') else str(case.priority) if case.priority else 'Unknown',
                'created_at': case.created_at.isoformat() if case.created_at else datetime.utcnow().isoformat(),
                'updated_at': case.updated_at.isoformat() if case.updated_at else datetime.utcnow().isoformat()
            },
            'statistics': {
                'platforms_analyzed': 'None',
                'flagged_users': 0,
                'flagged_posts': content_count,
                'osint_results': osint_count
            }
        }
        
        current_app.logger.info("Preview data created successfully")
        return jsonify({'success': True, 'data': preview_data})
        
    except Exception as e:
        current_app.logger.error(f"Error in preview_active_case_report: {str(e)}")
        import traceback
        current_app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': True, 'data': None}), 200  # Return 200 with null data instead of 500


@reports_bp.route('/list', methods=['GET'])
@jwt_required()
def list_cases_for_reports():
    """
    List all cases that can have reports generated
    
    Returns:
        JSON list of cases with basic information
    """
    try:
        # Get current user
        current_user_id = get_jwt_identity()
        current_user = SystemUser.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        priority = request.args.get('priority')
        
        # Build query scoped to current user
        query = Case.query.join(UserCaseLink).filter(UserCaseLink.user_id == current_user.id)
        
        if status:
            query = query.filter(Case.status == status)
        if priority:
            query = query.filter(Case.priority == priority)
        
        # Order by updated_at descending
        query = query.order_by(Case.updated_at.desc())
        
        # Paginate
        cases = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Prepare response data
        cases_data = []
        for case in cases.items:
            # Get basic statistics for each case
            # NOTE: The current schema does not link sources/content/users directly to cases.
            # Until a linking table/field exists, provide placeholder counts to avoid 500s.
            flagged_content_count = 0
            osint_results_count = 0
            platform_users_count = 0
            
            cases_data.append({
                'id': case.id,
                'title': case.title,
                'case_number': case.case_number,
                'status': case.status.value if case.status else None,
                'priority': case.priority.value if case.priority else None,
                'type': case.type.value if case.type else None,
                'created_at': case.created_at.isoformat(),
                'updated_at': case.updated_at.isoformat(),
                'statistics': {
                    'flagged_content': flagged_content_count,
                    'osint_results': osint_results_count,
                    'platform_users': platform_users_count
                }
            })
        
        return jsonify({
            'success': True,
            'data': {
                'cases': cases_data,
                'pagination': {
                    'page': cases.page,
                    'pages': cases.pages,
                    'per_page': cases.per_page,
                    'total': cases.total,
                    'has_next': cases.has_next,
                    'has_prev': cases.has_prev
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in list_cases_for_reports: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@reports_bp.route('/<int:case_id>/generate-detailed', methods=['GET'])
# @jwt_required()  # Temporarily disabled for testing
def generate_detailed_case_report(case_id):
    """
    Generate a comprehensive PDF report with analyst activities
    
    Args:
        case_id (int): The ID of the case
        
    Query Parameters:
        include_activities (bool): Include analyst activities (default: true)
        include_content (bool): Include related content (default: true)
        
    Returns:
        PDF file download
    """
    try:
        from models.case_activity import CaseActivity
        from services.narcotics_report_generator import generate_case_pdf_report
        
        # Get parameters
        include_activities = request.args.get('include_activities', 'true').lower() == 'true'
        include_content = request.args.get('include_content', 'true').lower() == 'true'
        
        # For testing without JWT, use a default user
        current_user = SystemUser.query.first()  # Get first user as default
        if not current_user:
            return jsonify({'error': 'No users found in database'}), 400
        
        # Get case
        case = Case.query.get(case_id)
        if not case:
            return jsonify({'error': f'Case with ID {case_id} not found'}), 404
        
        # Get activities if requested
        activities = None
        if include_activities:
            activities = CaseActivity.query.filter_by(
                case_id=case_id,
                include_in_report=True
            ).order_by(CaseActivity.activity_date.desc()).all()
        
        # Get related content if requested
        content_items = None
        if include_content:
            # Get content linked to this case
            from models.case_content_link import CaseContentLink
            content_links = db.session.query(CaseContentLink).filter_by(case_id=case_id).all()
            if content_links:
                content_ids = [link.content_id for link in content_links]
                content_items = Content.query.filter(Content.id.in_(content_ids)).all()
        
        # Generate PDF using Narcotics Intelligence Platform format
        pdf_buffer = generate_case_pdf_report(
            case=case,
            activities=activities,
            content_items=content_items
        )
        
        # Prepare filename
        filename = f"case_{case.case_number}_detailed_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Send file
        pdf_buffer.seek(0)  # Reset buffer position
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        current_app.logger.error(f"Error generating detailed report: {str(e)}")
        print(f"Error generating detailed report: {str(e)}")  # Debug print
        import traceback
        traceback.print_exc()  # Print full traceback
        return jsonify({'error': f'Failed to generate report: {str(e)}'}), 500


@reports_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for reports service"""
    return jsonify({
        'status': 'healthy',
        'service': 'reports',
        'timestamp': datetime.utcnow().isoformat()
    })
