"""
Activity Tracking Service
Automatically tracks user activities for investigations and content analysis
"""
from datetime import datetime
from typing import Dict, Any, Optional
from extensions import db
from models.case_activity import CaseActivity, ActivityType, ActivityStatus
from models.user import SystemUser
from models.case import Case
from models.content import Content
from models.osint_result import OSINTResult
import logging

logger = logging.getLogger(__name__)

class ActivityTracker:
    """Service for automatically tracking user activities"""
    
    def __init__(self):
        self.logger = logger
    
    def track_investigation_activity(self, user_id: int, username: str, platform: str, 
                                   investigation_results: Dict[str, Any], 
                                   case_id: Optional[int] = None) -> Optional[CaseActivity]:
        """
        Track user investigation activity
        
        Args:
            user_id: ID of the user performing investigation
            username: Username being investigated
            platform: Platform being investigated
            investigation_results: Results from investigation
            case_id: Optional case ID to link activity to
            
        Returns:
            CaseActivity object if created successfully
        """
        try:
            # Check if CaseActivity table exists
            inspector = db.inspect(db.engine)
            if 'case_activities' not in inspector.get_table_names():
                self.logger.warning("case_activities table does not exist, skipping activity tracking")
                return None
            
            # Get user
            user = SystemUser.query.get(user_id)
            if not user:
                self.logger.error(f"User {user_id} not found for activity tracking")
                return None
            
            # Determine activity details based on results
            total_profiles = investigation_results.get('totalProfilesFound', 0)
            risk_level = investigation_results.get('riskLevel', 'Unknown')
            tools_used = investigation_results.get('toolsUsed', [])
            
            # Create activity title and description
            title = f"User Investigation: {username} on {platform}"
            description = f"Investigated username '{username}' on {platform}. "
            description += f"Found {total_profiles} linked profiles. "
            description += f"Risk Level: {risk_level}. "
            if tools_used:
                description += f"Tools used: {', '.join(tools_used)}."
            
            # Determine priority based on risk level
            priority = self._get_priority_from_risk(risk_level)
            
            # Create tags
            tags = [platform.lower(), 'investigation', 'osint']
            if risk_level.lower() != 'low':
                tags.append('high-risk')
            
            # Create activity
            activity = CaseActivity(
                case_id=case_id or self._get_default_case_id(),
                analyst_id=user_id,
                activity_type=ActivityType.INVESTIGATION,
                title=title,
                description=description,
                status=ActivityStatus.ACTIVE,
                tags=tags,
                priority=priority,
                activity_date=datetime.utcnow(),
                time_spent_minutes=self._estimate_investigation_time(total_profiles),
                include_in_report=True,
                is_confidential=risk_level.lower() in ['high', 'critical'],
                visibility_level='team'
            )
            
            # Add investigation metadata
            activity.attachments = {
                'investigation_type': 'user_investigation',
                'target_username': username,
                'platform': platform,
                'total_profiles_found': total_profiles,
                'risk_level': risk_level,
                'tools_used': tools_used,
                'investigation_timestamp': datetime.utcnow().isoformat()
            }
            
            db.session.add(activity)
            db.session.commit()
            
            self.logger.info(f"Tracked investigation activity for user {user_id}: {username}")
            return activity
            
        except Exception as e:
            self.logger.error(f"Error tracking investigation activity: {str(e)}")
            db.session.rollback()
            return None
    
    def track_content_analysis_activity(self, user_id: int, content_text: str, 
                                      platform: str, username: str,
                                      analysis_results: Dict[str, Any],
                                      content_id: Optional[int] = None,
                                      case_id: Optional[int] = None) -> Optional[CaseActivity]:
        """
        Track content analysis activity
        
        Args:
            user_id: ID of the user performing analysis
            content_text: Content being analyzed
            platform: Platform where content was found
            username: Username who posted the content
            analysis_results: Results from content analysis
            content_id: Optional content ID if saved to database
            case_id: Optional case ID to link activity to
            
        Returns:
            CaseActivity object if created successfully
        """
        try:
            # Check if CaseActivity table exists
            inspector = db.inspect(db.engine)
            if 'case_activities' not in inspector.get_table_names():
                self.logger.warning("case_activities table does not exist, skipping activity tracking")
                return None
            
            # Get user
            user = SystemUser.query.get(user_id)
            if not user:
                self.logger.error(f"User {user_id} not found for activity tracking")
                return None
            
            # Extract analysis details
            suspicion_score = analysis_results.get('suspicion_score', 0)
            intent = analysis_results.get('intent', 'Unknown')
            is_flagged = analysis_results.get('is_flagged', False)
            matched_keywords = analysis_results.get('matched_keywords', [])
            
            # Create activity title and description
            title = f"Content Analysis: {username} on {platform}"
            description = f"Analyzed content from {username} on {platform}. "
            description += f"Suspicion Score: {suspicion_score}/100. "
            description += f"Intent: {intent}. "
            if matched_keywords:
                description += f"Keywords: {', '.join(matched_keywords[:5])}. "
            if is_flagged:
                description += "Content flagged for review."
            
            # Determine priority based on suspicion score
            priority = self._get_priority_from_suspicion_score(suspicion_score)
            
            # Create tags
            tags = [platform.lower(), 'content_analysis', 'nlp']
            if is_flagged:
                tags.append('flagged')
            if intent.lower() != 'unknown':
                tags.append(intent.lower())
            
            # Create activity
            activity = CaseActivity(
                case_id=case_id or self._get_default_case_id(),
                analyst_id=user_id,
                activity_type=ActivityType.ANALYSIS,
                title=title,
                description=description,
                status=ActivityStatus.ACTIVE,
                tags=tags,
                priority=priority,
                activity_date=datetime.utcnow(),
                time_spent_minutes=self._estimate_analysis_time(len(content_text)),
                include_in_report=is_flagged,  # Only include flagged content in reports
                is_confidential=is_flagged and suspicion_score >= 70,
                visibility_level='team'
            )
            
            # Add analysis metadata
            activity.attachments = {
                'analysis_type': 'content_analysis',
                'platform': platform,
                'author': username,
                'suspicion_score': suspicion_score,
                'intent': intent,
                'is_flagged': is_flagged,
                'matched_keywords': matched_keywords,
                'content_preview': content_text[:200] + '...' if len(content_text) > 200 else content_text,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Link to content if available
            if content_id:
                activity.related_content_ids = [content_id]
            
            db.session.add(activity)
            db.session.commit()
            
            self.logger.info(f"Tracked content analysis activity for user {user_id}: {username}")
            return activity
            
        except Exception as e:
            self.logger.error(f"Error tracking content analysis activity: {str(e)}")
            db.session.rollback()
            return None
    
    def track_batch_analysis_activity(self, user_id: int, batch_results: list,
                                    platform: str, case_id: Optional[int] = None) -> Optional[CaseActivity]:
        """
        Track batch content analysis activity
        
        Args:
            user_id: ID of the user performing batch analysis
            batch_results: List of analysis results
            platform: Platform being analyzed
            case_id: Optional case ID to link activity to
            
        Returns:
            CaseActivity object if created successfully
        """
        try:
            # Check if CaseActivity table exists
            inspector = db.inspect(db.engine)
            if 'case_activities' not in inspector.get_table_names():
                self.logger.warning("case_activities table does not exist, skipping activity tracking")
                return None
            
            # Get user
            user = SystemUser.query.get(user_id)
            if not user:
                self.logger.error(f"User {user_id} not found for activity tracking")
                return None
            
            # Calculate batch statistics
            total_analyzed = len(batch_results)
            flagged_count = sum(1 for result in batch_results if result.get('is_flagged', False))
            avg_suspicion = sum(result.get('suspicion_score', 0) for result in batch_results) / total_analyzed if total_analyzed > 0 else 0
            
            # Create activity title and description
            title = f"Batch Content Analysis: {platform}"
            description = f"Performed batch analysis on {total_analyzed} content items from {platform}. "
            description += f"Flagged {flagged_count} items for review. "
            description += f"Average suspicion score: {avg_suspicion:.1f}/100."
            
            # Determine priority based on flagged count
            priority = 'high' if flagged_count > total_analyzed * 0.3 else 'medium'
            
            # Create tags
            tags = [platform.lower(), 'batch_analysis', 'content_analysis']
            if flagged_count > 0:
                tags.append('flagged_content')
            
            # Create activity
            activity = CaseActivity(
                case_id=case_id or self._get_default_case_id(),
                analyst_id=user_id,
                activity_type=ActivityType.ANALYSIS,
                title=title,
                description=description,
                status=ActivityStatus.ACTIVE,
                tags=tags,
                priority=priority,
                activity_date=datetime.utcnow(),
                time_spent_minutes=self._estimate_batch_analysis_time(total_analyzed),
                include_in_report=flagged_count > 0,
                is_confidential=flagged_count > total_analyzed * 0.5,
                visibility_level='team'
            )
            
            # Add batch analysis metadata
            activity.attachments = {
                'analysis_type': 'batch_content_analysis',
                'platform': platform,
                'total_items_analyzed': total_analyzed,
                'flagged_items': flagged_count,
                'average_suspicion_score': avg_suspicion,
                'batch_timestamp': datetime.utcnow().isoformat()
            }
            
            db.session.add(activity)
            db.session.commit()
            
            self.logger.info(f"Tracked batch analysis activity for user {user_id}: {total_analyzed} items")
            return activity
            
        except Exception as e:
            self.logger.error(f"Error tracking batch analysis activity: {str(e)}")
            db.session.rollback()
            return None
    
    def track_osint_search_activity(self, user_id: int, search_query: str, 
                                  search_type: str, results: Dict[str, Any],
                                  case_id: Optional[int] = None) -> Optional[CaseActivity]:
        """
        Track OSINT search activity
        
        Args:
            user_id: ID of the user performing search
            search_query: Search query used
            search_type: Type of OSINT search
            results: Search results
            case_id: Optional case ID to link activity to
            
        Returns:
            CaseActivity object if created successfully
        """
        try:
            # Get user
            user = SystemUser.query.get(user_id)
            if not user:
                self.logger.error(f"User {user_id} not found for activity tracking")
                return None
            
            # Extract results details
            results_count = results.get('total_results', 0)
            risk_score = results.get('risk_score', 0)
            status = results.get('status', 'completed')
            
            # Create activity title and description
            title = f"OSINT Search: {search_type}"
            description = f"Performed {search_type} search for '{search_query}'. "
            description += f"Found {results_count} results. "
            description += f"Risk Score: {risk_score}/100. "
            description += f"Status: {status}."
            
            # Determine priority based on risk score
            priority = self._get_priority_from_risk_score(risk_score)
            
            # Create tags
            tags = ['osint', search_type.lower(), 'search']
            if risk_score >= 70:
                tags.append('high-risk')
            
            # Create activity
            activity = CaseActivity(
                case_id=case_id or self._get_default_case_id(),
                analyst_id=user_id,
                activity_type=ActivityType.INVESTIGATION,
                title=title,
                description=description,
                status=ActivityStatus.ACTIVE,
                tags=tags,
                priority=priority,
                activity_date=datetime.utcnow(),
                time_spent_minutes=self._estimate_osint_time(search_type),
                include_in_report=risk_score >= 50,
                is_confidential=risk_score >= 70,
                visibility_level='team'
            )
            
            # Add OSINT metadata
            activity.attachments = {
                'search_type': 'osint_search',
                'search_query': search_query,
                'search_type': search_type,
                'results_count': results_count,
                'risk_score': risk_score,
                'search_timestamp': datetime.utcnow().isoformat()
            }
            
            db.session.add(activity)
            db.session.commit()
            
            self.logger.info(f"Tracked OSINT search activity for user {user_id}: {search_type}")
            return activity
            
        except Exception as e:
            self.logger.error(f"Error tracking OSINT search activity: {str(e)}")
            db.session.rollback()
            return None
    
    def _get_priority_from_risk(self, risk_level: str) -> str:
        """Convert risk level to priority"""
        risk_mapping = {
            'low': 'low',
            'medium': 'medium', 
            'high': 'high',
            'critical': 'critical'
        }
        return risk_mapping.get(risk_level.lower(), 'medium')
    
    def _get_priority_from_suspicion_score(self, score: int) -> str:
        """Convert suspicion score to priority"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _get_priority_from_risk_score(self, score: int) -> str:
        """Convert risk score to priority"""
        if score >= 80:
            return 'critical'
        elif score >= 60:
            return 'high'
        elif score >= 40:
            return 'medium'
        else:
            return 'low'
    
    def _estimate_investigation_time(self, profiles_found: int) -> int:
        """Estimate investigation time based on results"""
        base_time = 15  # Base 15 minutes
        additional_time = profiles_found * 2  # 2 minutes per profile found
        return min(base_time + additional_time, 120)  # Cap at 2 hours
    
    def _estimate_analysis_time(self, content_length: int) -> int:
        """Estimate analysis time based on content length"""
        base_time = 5  # Base 5 minutes
        additional_time = content_length // 100  # 1 minute per 100 characters
        return min(base_time + additional_time, 30)  # Cap at 30 minutes
    
    def _estimate_batch_analysis_time(self, item_count: int) -> int:
        """Estimate batch analysis time"""
        return min(item_count * 2, 60)  # 2 minutes per item, cap at 1 hour
    
    def _estimate_osint_time(self, search_type: str) -> int:
        """Estimate OSINT search time"""
        time_mapping = {
            'username': 10,
            'email': 15,
            'phone': 20,
            'domain': 25,
            'ip': 30
        }
        return time_mapping.get(search_type.lower(), 15)
    
    def _get_default_case_id(self) -> Optional[int]:
        """Get default case ID for activities not linked to specific cases"""
        # Try to find an active case, or return None
        active_case = Case.query.filter_by(status='open').first()
        return active_case.id if active_case else None


# Global activity tracker instance
activity_tracker = ActivityTracker()
