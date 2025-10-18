"""
Case Service for managing investigation cases
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, and_, or_

from extensions import db
from models.case import Case, CaseStatus, CasePriority, CaseType
from models.user_case_link import UserCaseLink, UserCaseRole, UserCaseStatus
from models.user import User, SystemUser, SystemUserRole
from models.content import Content
from models.case_content_link import CaseContentLink
from models.case_request import CaseRequest, RequestStatus

logger = logging.getLogger(__name__)

class CaseService:
    """Service for managing cases and user-case relationships"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def can_create_case(self, user_id: int) -> Tuple[bool, str]:
        """Check if a user can create a new case"""
        try:
            # Get user role
            user = SystemUser.query.get(user_id)
            if not user:
                return False, "User not found"
            
            # Admins can always create cases
            if user.role == SystemUserRole.ADMIN:
                return True, "Admin can create cases"
            
            # For analysts, check if they have any open cases
            open_cases = Case.query.join(UserCaseLink).filter(
                and_(
                    UserCaseLink.user_id == user_id,
                    UserCaseLink.role == UserCaseRole.OWNER,
                    Case.status.in_([CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING])
                )
            ).count()
            
            if open_cases > 0:
                return False, f"You have {open_cases} open case(s). Please close existing cases before creating new ones. Contact admin for approval if urgent."
            
            return True, "Can create case"
            
        except Exception as e:
            self.logger.error(f"Error checking case creation permission: {e}")
            return False, "Error checking permissions"

    def create_case_request(self, title: str, description: str = None, case_type: str = None, 
                           priority: str = None, summary: str = None, objectives: str = None, 
                           methodology: str = None, tags: list = None, requested_by_id: int = None) -> Tuple[bool, str, Optional[CaseRequest]]:
        """Create a case creation request for admin approval"""
        try:
            case_request = CaseRequest(
                title=title,
                description=description,
                case_type=case_type,
                priority=priority,
                summary=summary,
                objectives=objectives,
                methodology=methodology,
                tags=tags,
                requested_by_id=requested_by_id,
                status=RequestStatus.PENDING
            )
            
            db.session.add(case_request)
            db.session.commit()
            
            self.logger.info(f"Case request created: {case_request.id} by user {requested_by_id}")
            return True, "Case creation request submitted for admin approval", case_request
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Error creating case request: {e}")
            return False, f"Failed to create case request: {str(e)}", None

    def get_case_requests(self, status: str = None, requested_by_id: int = None) -> Tuple[bool, str, List[CaseRequest]]:
        """Get case creation requests"""
        try:
            query = CaseRequest.query
            
            # Safely handle optional status filter (case-insensitive, ignore invalid)
            if status is not None and str(status).strip() != "":
                try:
                    normalized_status = str(status).strip().lower()
                    # Validate against enum values; ignore if invalid instead of raising
                    valid_values = {s.value for s in RequestStatus}
                    if normalized_status in valid_values:
                        query = query.filter(CaseRequest.status == RequestStatus(normalized_status))
                except Exception as parse_error:
                    # Log and continue without applying invalid status filter
                    self.logger.warning(f"Ignoring invalid case request status filter '{status}': {parse_error}")
            
            if requested_by_id:
                query = query.filter(CaseRequest.requested_by_id == requested_by_id)
            
            requests = query.order_by(CaseRequest.requested_at.desc()).all()
            return True, "Case requests retrieved successfully", requests
            
        except Exception as e:
            self.logger.error(f"Error retrieving case requests: {e}")
            return False, f"Failed to retrieve case requests: {str(e)}", []

    def approve_case_request(self, request_id: int, reviewed_by_id: int, review_notes: str = None) -> Tuple[bool, str, Optional[Case]]:
        """Approve a case creation request and create the case"""
        try:
            case_request = CaseRequest.query.get(request_id)
            if not case_request:
                return False, "Case request not found", None
            
            if case_request.status != RequestStatus.PENDING:
                return False, "Case request is not pending", None
            
            # Create the case
            success, message, case = self.create_case(
                title=case_request.title,
                description=case_request.description,
                case_type=case_request.case_type,
                priority=case_request.priority,
                created_by_id=case_request.requested_by_id,
                summary=case_request.summary,
                objectives=case_request.objectives,
                methodology=case_request.methodology,
                tags=case_request.tags
            )
            
            if success:
                # Update request status
                case_request.status = RequestStatus.APPROVED
                case_request.reviewed_by_id = reviewed_by_id
                case_request.review_notes = review_notes
                case_request.reviewed_at = datetime.utcnow()
                
                db.session.commit()
                self.logger.info(f"Case request {request_id} approved and case {case.id} created")
                return True, "Case request approved and case created successfully", case
            else:
                return False, f"Failed to create case: {message}", None
                
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error approving case request: {e}")
            return False, f"Failed to approve case request: {str(e)}", None

    def reject_case_request(self, request_id: int, reviewed_by_id: int, review_notes: str) -> Tuple[bool, str]:
        """Reject a case creation request"""
        try:
            case_request = CaseRequest.query.get(request_id)
            if not case_request:
                return False, "Case request not found"
            
            if case_request.status != RequestStatus.PENDING:
                return False, "Case request is not pending"
            
            case_request.status = RequestStatus.REJECTED
            case_request.reviewed_by_id = reviewed_by_id
            case_request.review_notes = review_notes
            case_request.reviewed_at = datetime.utcnow()
            
            db.session.commit()
            self.logger.info(f"Case request {request_id} rejected")
            return True, "Case request rejected successfully"
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error rejecting case request: {e}")
            return False, f"Failed to reject case request: {str(e)}"

    def create_case(self, title: str, description: str = None, case_type: str = None, 
                   priority: str = None, created_by_id: int = None, **kwargs) -> Tuple[bool, str, Optional[Case]]:
        """Create a new case"""
        try:
            # Check if user can create a case
            if created_by_id:
                can_create, message = self.can_create_case(created_by_id)
                if not can_create:
                    return False, message, None
            
            case_number = self._generate_case_number()
            
            case_type_enum = CaseType.DRUG_TRAFFICKING_INVESTIGATION
            if case_type:
                try:
                    case_type_enum = CaseType(case_type.lower())
                except ValueError:
                    self.logger.warning(f"Invalid case type: {case_type}, using DRUG_TRAFFICKING_INVESTIGATION")
            
            priority_enum = CasePriority.MEDIUM
            if priority:
                try:
                    priority_enum = CasePriority(priority.lower())
                except ValueError:
                    self.logger.warning(f"Invalid priority: {priority}, using MEDIUM")
            
            case = Case(
                title=title,
                description=description,
                case_number=case_number,
                type=case_type_enum,
                priority=priority_enum,
                created_by_id=created_by_id,
                **kwargs
            )
            
            db.session.add(case)
            db.session.commit()
            
            if created_by_id:
                self.link_user_to_case(
                    user_id=created_by_id,
                    case_id=case.id,
                    role=UserCaseRole.OWNER.value,
                    assigned_by_id=created_by_id
                )
            
            self.logger.info(f"Created case {case_number}: {title}")
            return True, "Case created successfully", case
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Failed to create case: {str(e)}")
            return False, f"Failed to create case: {str(e)}", None
    
    def get_all_cases(self, status: str = None, priority: str = None, 
                     case_type: str = None, assigned_to_id: int = None,
                     page: int = 1, per_page: int = 10,
                     current_user_id: int | None = None) -> Tuple[bool, str, Dict]:
        """Get all cases with optional filtering"""
        try:
            # Start from cases; if a user is provided, scope to cases linked to that user
            query = Case.query
            if current_user_id:
                query = query.join(UserCaseLink).filter(UserCaseLink.user_id == current_user_id)
            
            if status:
                try:
                    status_enum = CaseStatus(status.lower().replace(' ', '_'))
                    query = query.filter(Case.status == status_enum)
                except ValueError:
                    return False, f"Invalid status: {status}", {}
            
            if priority:
                try:
                    priority_enum = CasePriority(priority.lower())
                    query = query.filter(Case.priority == priority_enum)
                except ValueError:
                    return False, f"Invalid priority: {priority}", {}
            
            if case_type:
                try:
                    case_type_enum = CaseType(case_type.lower())
                    query = query.filter(Case.type == case_type_enum)
                except ValueError:
                    return False, f"Invalid case type: {case_type}", {}
            
            if assigned_to_id:
                query = query.filter(Case.assigned_to_id == assigned_to_id)
            
            query = query.order_by(Case.created_at.desc())
            
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            cases_data = []
            for case in pagination.items:
                case_dict = case.to_dict()
                
                user_count = db.session.query(func.count(UserCaseLink.user_id)).filter_by(case_id=case.id).scalar()
                case_dict['user_count'] = user_count or 0
                
                content_count = 0  # Simplified for now
                case_dict['content_count'] = content_count
                
                cases_data.append(case_dict)
            
            return True, "Cases retrieved successfully", {
                'cases': cases_data,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get cases: {str(e)}")
            return False, f"Failed to get cases: {str(e)}", {}
    
    def get_case_details(self, case_id: int) -> Tuple[bool, str, Optional[Dict]]:
        """Get detailed information about a case including linked users and content"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return False, "Case not found", None
            
            case_data = case.to_dict()
            
            user_links = db.session.query(UserCaseLink).filter(
                UserCaseLink.case_id == case_id
            ).all()
            
            linked_users = []
            for link in user_links:
                link_data = link.to_dict()
                # Use SystemUser since that's what the authentication system uses
                user = SystemUser.query.get(link.user_id)
                if user:
                    user_dict = user.to_dict()
                    # Add username field for frontend compatibility
                    user_dict['username'] = user.username
                    user_dict['is_flagged'] = False  # Add default flagged status
                    link_data['user'] = user_dict
                else:
                    # If no SystemUser found, create a placeholder
                    link_data['user'] = {
                        'id': link.user_id,
                        'username': f'user_{link.user_id}',
                        'full_name': 'Unknown User',
                        'is_flagged': False
                    }
                linked_users.append(link_data)
            
            case_data['linked_users'] = linked_users
            # Linked content
            content_links = db.session.query(CaseContentLink).filter(
                CaseContentLink.case_id == case_id
            ).all()
            linked_content = []
            for cl in content_links:
                content = Content.query.get(cl.content_id)
                if content:
                    content_dict = content.to_dict()
                    content_dict['link_id'] = cl.id
                    linked_content.append(content_dict)
            case_data['linked_content'] = linked_content
            
            case_data['statistics'] = {
                'user_count': len(linked_users),
                'content_count': 0,
                'days_open': (datetime.utcnow() - case.created_at).days,
                'is_overdue': case.is_overdue(),
                'progress_percentage': case.progress_percentage
            }
            
            return True, "Case details retrieved successfully", case_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get case details: {str(e)}")
            return False, f"Failed to get case details: {str(e)}", None

    def link_content_to_case(self, case_id: int, content_ids: list[int]) -> Tuple[bool, str, int]:
        """Attach one or more content items to a case. Returns number of links created."""
        try:
            created = 0
            # Validate case exists
            case = Case.query.get(case_id)
            if not case:
                return False, "Case not found", 0
            
            for content_id in content_ids:
                content = Content.query.get(content_id)
                if not content:
                    continue
                # Skip if link exists
                existing = CaseContentLink.query.filter_by(case_id=case_id, content_id=content_id).first()
                if existing:
                    continue
                link = CaseContentLink(case_id=case_id, content_id=content_id)
                db.session.add(link)
                created += 1
            db.session.commit()
            return True, f"Linked {created} content item(s) to case", created
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error linking content to case: {e}")
            return False, f"Failed to link content: {str(e)}", 0

    def unlink_content_from_case(self, case_id: int, content_id: int) -> Tuple[bool, str]:
        try:
            link = CaseContentLink.query.filter_by(case_id=case_id, content_id=content_id).first()
            if not link:
                return False, "Link not found"
            db.session.delete(link)
            db.session.commit()
            return True, "Content unlinked from case"
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error unlinking content from case: {e}")
            return False, f"Failed to unlink content: {str(e)}"
    
    def link_user_to_case(self, user_id: int, case_id: int, role: str = None,
                         assigned_by_id: int = None, assignment_reason: str = None,
                         **kwargs) -> Tuple[bool, str, Optional[UserCaseLink]]:
        """Link a user to a case"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return False, "Case not found", None
            
            # Use SystemUser since that's what the authentication system uses
            user = SystemUser.query.get(user_id)
            if not user:
                return False, "User not found", None
            
            existing = UserCaseLink.query.filter_by(case_id=case_id, user_id=user_id).first()
            if existing:
                return False, "User already linked to this case", existing
            
            role_enum = UserCaseRole.VIEWER
            if role:
                try:
                    role_enum = UserCaseRole(role.lower())
                except ValueError:
                    self.logger.warning(f"Invalid role: {role}, using VIEWER")
            
            user_case_link = UserCaseLink(
                user_id=user_id,
                case_id=case_id,
                role=role_enum,
                assigned_by_id=assigned_by_id,
                assignment_reason=assignment_reason,
                **kwargs
            )
            
            db.session.add(user_case_link)
            db.session.commit()
            
            self.logger.info(f"Linked user {user_id} to case {case_id} with role {role_enum.value}")
            return True, "User linked to case successfully", user_case_link
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Failed to link user to case: {str(e)}")
            return False, f"Failed to link user to case: {str(e)}", None
    
    def unlink_user_from_case(self, user_id: int, case_id: int) -> Tuple[bool, str]:
        """Unlink a user from a case"""
        try:
            link = UserCaseLink.query.filter_by(user_id=user_id, case_id=case_id).first()
            if not link:
                return False, "User-case link not found"
            
            db.session.delete(link)
            db.session.commit()
            
            self.logger.info(f"Unlinked user {user_id} from case {case_id}")
            return True, "User unlinked from case successfully"
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Failed to unlink user from case: {str(e)}")
            return False, f"Failed to unlink user from case: {str(e)}"
    
    def close_case(self, case_id: int, notes: str = None, closed_by_id: int = None) -> Tuple[bool, str, Optional[Case]]:
        """Close a case with optional notes"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return False, "Case not found", None
            
            case.status = CaseStatus.CLOSED
            case.actual_completion = datetime.utcnow()
            
            if notes:
                if case.findings:
                    case.findings += f"\n\nClosing Notes ({datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}):\n{notes}"
                else:
                    case.findings = f"Closing Notes ({datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}):\n{notes}"
            
            case.progress_percentage = 100
            
            db.session.commit()
            
            self.logger.info(f"Closed case {case.case_number}: {case.title}")
            return True, "Case closed successfully", case
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Failed to close case: {str(e)}")
            return False, f"Failed to close case: {str(e)}", None
    
    def update_case_status(self, case_id: int, status: str) -> Tuple[bool, str, Optional[Case]]:
        """Update case status"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return False, "Case not found", None
            
            try:
                status_enum = CaseStatus(status.lower().replace(' ', '_'))
            except ValueError:
                valid_statuses = [status.value for status in CaseStatus]
                return False, f"Invalid status. Valid options: {valid_statuses}", None
            
            case.status = status_enum
            
            if status_enum in [CaseStatus.CLOSED, CaseStatus.RESOLVED]:
                case.actual_completion = datetime.utcnow()
                case.progress_percentage = 100
            
            db.session.commit()
            
            self.logger.info(f"Updated case {case.case_number} status to {status_enum.value}")
            return True, "Case status updated successfully", case
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Failed to update case status: {str(e)}")
            return False, f"Failed to update case status: {str(e)}", None
    
    def update_case_progress(self, case_id: int, progress_percentage: int) -> Tuple[bool, str, Optional[Case]]:
        """Update case progress percentage"""
        try:
            case = Case.query.get(case_id)
            if not case:
                return False, "Case not found", None
            
            if not 0 <= progress_percentage <= 100:
                return False, "Progress percentage must be between 0 and 100", None
            
            case.progress_percentage = progress_percentage
            db.session.commit()
            
            self.logger.info(f"Updated case {case.case_number} progress to {progress_percentage}%")
            return True, "Case progress updated successfully", case
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"Failed to update case progress: {str(e)}")
            return False, f"Failed to update case progress: {str(e)}", None
    
    def get_cases_by_user(self, user_id: int, role: str = None) -> Tuple[bool, str, List[Dict]]:
        """Get all cases linked to a specific user"""
        try:
            query = db.session.query(Case).join(UserCaseLink).filter(
                UserCaseLink.user_id == user_id
            )
            
            if role:
                try:
                    role_enum = UserCaseRole(role.lower())
                    query = query.filter(UserCaseLink.role == role_enum)
                except ValueError:
                    return False, f"Invalid role: {role}", []
            
            cases = query.order_by(Case.created_at.desc()).all()
            
            cases_data = []
            for case in cases:
                case_dict = case.to_dict()
                
                user_link = UserCaseLink.query.filter_by(
                    user_id=user_id, case_id=case.id
                ).first()
                if user_link:
                    case_dict['user_role'] = user_link.role.value
                    case_dict['user_permissions'] = {
                        'can_edit': user_link.can_edit,
                        'can_delete': user_link.can_delete,
                        'can_assign': user_link.can_assign,
                        'can_comment': user_link.can_comment,
                        'can_view_sensitive': user_link.can_view_sensitive
                    }
                
                cases_data.append(case_dict)
            
            return True, "User cases retrieved successfully", cases_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get cases by user: {str(e)}")
            return False, f"Failed to get cases by user: {str(e)}", []
    
    def _generate_case_number(self) -> str:
        """Generate unique case number"""
        try:
            latest_case = Case.query.order_by(Case.id.desc()).first()
            
            if latest_case and latest_case.case_number:
                try:
                    parts = latest_case.case_number.split('-')
                    if len(parts) >= 3:
                        last_number = int(parts[-1])
                        new_number = last_number + 1
                    else:
                        new_number = 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            current_year = datetime.now().year
            case_number = f"CASE-{current_year}-{new_number:03d}"
            
            return case_number
            
        except Exception as e:
            self.logger.error(f"Failed to generate case number: {str(e)}")
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            return f"CASE-{timestamp}"
    
    def get_case_statistics(self) -> Tuple[bool, str, Dict]:
        """Get overall case statistics"""
        try:
            stats = {}
            
            stats['total_cases'] = Case.query.count()
            
            status_counts = db.session.query(
                Case.status, func.count(Case.id)
            ).group_by(Case.status).all()
            stats['by_status'] = {status.value: count for status, count in status_counts}
            
            priority_counts = db.session.query(
                Case.priority, func.count(Case.id)
            ).group_by(Case.priority).all()
            stats['by_priority'] = {priority.value: count for priority, count in priority_counts}
            
            type_counts = db.session.query(
                Case.type, func.count(Case.id)
            ).group_by(Case.type).all()
            stats['by_type'] = {case_type.value: count for case_type, count in type_counts}
            
            closed_cases = Case.query.filter(
                Case.actual_completion.isnot(None)
            ).all()
            
            if closed_cases:
                total_days = sum([
                    (case.actual_completion - case.start_date).days 
                    for case in closed_cases
                ])
                stats['average_duration_days'] = round(total_days / len(closed_cases), 2)
            else:
                stats['average_duration_days'] = 0
            
            overdue_cases = Case.query.filter(
                and_(
                    Case.due_date < datetime.utcnow(),
                    Case.status.in_([CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING])
                )
            ).count()
            stats['overdue_cases'] = overdue_cases
            
            return True, "Statistics retrieved successfully", stats
            
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to get case statistics: {str(e)}")
            return False, f"Failed to get case statistics: {str(e)}", {}
