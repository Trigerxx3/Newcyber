"""
Case Activity Model - Track all analyst work and activities on cases
"""
from extensions import db
from datetime import datetime
import enum

class ActivityType(enum.Enum):
    """Types of case activities"""
    NOTE = "note"  # General investigation note
    FINDING = "finding"  # Important finding/discovery
    EVIDENCE = "evidence"  # Evidence collected
    INTERVIEW = "interview"  # Interview notes
    ANALYSIS = "analysis"  # Analysis/assessment
    ACTION = "action"  # Action taken
    MEETING = "meeting"  # Meeting notes
    COMMUNICATION = "communication"  # Communication logs
    TASK = "task"  # Task completed
    UPDATE = "update"  # Status update
    MILESTONE = "milestone"  # Milestone reached
    OBSERVATION = "observation"  # Observation made
    RECOMMENDATION = "recommendation"  # Recommendation given
    DECISION = "decision"  # Decision made
    INVESTIGATION = "investigation"  # User investigation activity
    CONTENT_ANALYSIS = "content_analysis"  # Content analysis activity
    OSINT_SEARCH = "osint_search"  # OSINT search activity
    BATCH_ANALYSIS = "batch_analysis"  # Batch content analysis
    PLATFORM_SCRAPING = "platform_scraping"  # Platform scraping activity
    OTHER = "other"  # Other activity

class ActivityStatus(enum.Enum):
    """Status of case activities"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CaseActivity(db.Model):
    """
    Model to track all analyst work and activities on cases
    This allows detailed tracking and reporting of investigation work
    """
    __tablename__ = 'case_activities'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    analyst_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, index=True)
    
    # Activity Information
    activity_type = db.Column(db.Enum(ActivityType), nullable=False, default=ActivityType.NOTE)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Activity Metadata
    status = db.Column(db.Enum(ActivityStatus), nullable=False, default=ActivityStatus.ACTIVE)
    tags = db.Column(db.JSON)  # Tags for categorization
    priority = db.Column(db.String(20))  # low, medium, high, critical
    
    # Evidence/Attachments
    attachments = db.Column(db.JSON)  # Links to files, images, etc.
    evidence_links = db.Column(db.JSON)  # Links to evidence
    related_content_ids = db.Column(db.JSON)  # Related content IDs
    related_source_ids = db.Column(db.JSON)  # Related source IDs
    
    # Time Tracking
    activity_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    time_spent_minutes = db.Column(db.Integer, default=0)  # Time spent on this activity
    
    # Visibility and Report Inclusion
    include_in_report = db.Column(db.Boolean, default=True)  # Include in PDF report
    is_confidential = db.Column(db.Boolean, default=False)  # Mark as confidential
    visibility_level = db.Column(db.String(20), default='team')  # public, team, restricted, confidential
    
    # Edit History
    edited_at = db.Column(db.DateTime)
    edited_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'))
    edit_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    case = db.relationship('Case', backref=db.backref('activities', lazy='dynamic', cascade='all, delete-orphan'))
    analyst = db.relationship('SystemUser', foreign_keys=[analyst_id], backref='case_activities')
    edited_by = db.relationship('SystemUser', foreign_keys=[edited_by_id])
    
    def __repr__(self):
        return f'<CaseActivity {self.id}: {self.title}>'
    
    def to_dict(self, include_relationships=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'case_id': self.case_id,
            'analyst_id': self.analyst_id,
            'activity_type': self.activity_type.value if self.activity_type else None,
            'title': self.title,
            'description': self.description,
            'status': self.status.value if self.status else None,
            'tags': self.tags or [],
            'priority': self.priority,
            'attachments': self.attachments or [],
            'evidence_links': self.evidence_links or [],
            'related_content_ids': self.related_content_ids or [],
            'related_source_ids': self.related_source_ids or [],
            'activity_date': self.activity_date.isoformat() if self.activity_date else None,
            'time_spent_minutes': self.time_spent_minutes,
            'include_in_report': self.include_in_report,
            'is_confidential': self.is_confidential,
            'visibility_level': self.visibility_level,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'edited_by_id': self.edited_by_id,
            'edit_count': self.edit_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_relationships:
            data['analyst'] = {
                'id': self.analyst.id,
                'username': self.analyst.username,
                'email': self.analyst.email
            } if self.analyst else None
            
            if self.edited_by:
                data['edited_by'] = {
                    'id': self.edited_by.id,
                    'username': self.edited_by.username,
                    'email': self.edited_by.email
                }
        
        return data
    
    def mark_edited(self, editor_id):
        """Mark activity as edited"""
        self.edited_at = datetime.utcnow()
        self.edited_by_id = editor_id
        self.edit_count += 1
        self.updated_at = datetime.utcnow()
    
    def add_attachment(self, attachment_url, attachment_type, description=None):
        """Add an attachment"""
        if not self.attachments:
            self.attachments = []
        
        self.attachments.append({
            'url': attachment_url,
            'type': attachment_type,
            'description': description,
            'added_at': datetime.utcnow().isoformat()
        })
    
    def add_evidence_link(self, evidence_type, evidence_id, description=None):
        """Add evidence link"""
        if not self.evidence_links:
            self.evidence_links = []
        
        self.evidence_links.append({
            'type': evidence_type,
            'id': evidence_id,
            'description': description,
            'added_at': datetime.utcnow().isoformat()
        })
    
    def link_content(self, content_id):
        """Link to content"""
        if not self.related_content_ids:
            self.related_content_ids = []
        
        if content_id not in self.related_content_ids:
            self.related_content_ids.append(content_id)
    
    def link_source(self, source_id):
        """Link to source"""
        if not self.related_source_ids:
            self.related_source_ids = []
        
        if source_id not in self.related_source_ids:
            self.related_source_ids.append(source_id)
    
    def toggle_report_inclusion(self):
        """Toggle whether to include in report"""
        self.include_in_report = not self.include_in_report
        self.updated_at = datetime.utcnow()
    
    def set_confidential(self, is_confidential):
        """Set confidentiality status"""
        self.is_confidential = is_confidential
        if is_confidential:
            self.visibility_level = 'confidential'
        self.updated_at = datetime.utcnow()

