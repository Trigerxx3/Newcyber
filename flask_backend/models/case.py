from extensions import db
from datetime import datetime
import enum

class CaseStatus(enum.Enum):
    """Enum for case status"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING = "pending"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ARCHIVED = "archived"

class CasePriority(enum.Enum):
    """Enum for case priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CaseType(enum.Enum):
    """Enum for case types"""
    THREAT_INVESTIGATION = "threat_investigation"
    INCIDENT_RESPONSE = "incident_response"
    VULNERABILITY_ASSESSMENT = "vulnerability_assessment"
    COMPLIANCE_AUDIT = "compliance_audit"
    FORENSIC_ANALYSIS = "forensic_analysis"
    OSINT_INVESTIGATION = "osint_investigation"
    MALWARE_ANALYSIS = "malware_analysis"
    NETWORK_MONITORING = "network_monitoring"
    CUSTOM = "custom"

class Case(db.Model):
    """Case model for investigation management"""
    __tablename__ = 'cases'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    case_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    type = db.Column(db.Enum(CaseType), nullable=False, default=CaseType.CUSTOM)
    
    # Status and Priority
    status = db.Column(db.Enum(CaseStatus), nullable=False, default=CaseStatus.OPEN)
    priority = db.Column(db.Enum(CasePriority), nullable=False, default=CasePriority.MEDIUM)
    
    # Assignment and Ownership
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, index=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True, index=True)
    
    # Case Details
    summary = db.Column(db.Text)
    objectives = db.Column(db.Text)
    methodology = db.Column(db.Text)
    findings = db.Column(db.Text)
    recommendations = db.Column(db.Text)
    
    # Risk Assessment
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='low')
    threat_indicators = db.Column(db.JSON)  # Associated threat indicators
    
    # Metadata
    tags = db.Column(db.JSON)  # Tags for categorization
    meta_data = db.Column(db.JSON)  # Additional metadata
    external_references = db.Column(db.JSON)  # External case references
    
    # Timelines
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    estimated_completion = db.Column(db.DateTime)
    actual_completion = db.Column(db.DateTime)
    
    # Progress Tracking
    progress_percentage = db.Column(db.Integer, default=0)
    milestones = db.Column(db.JSON)  # Case milestones
    checkpoints = db.Column(db.JSON)  # Progress checkpoints
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assigned_to = db.relationship('SystemUser', foreign_keys=[assigned_to_id], backref='assigned_cases')
    created_by = db.relationship('SystemUser', foreign_keys=[created_by_id], backref='created_cases')
    owner = db.relationship('SystemUser', foreign_keys=[owner_id], backref='owned_cases')
    user_links = db.relationship('UserCaseLink', backref='case', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Case {self.case_number}: {self.title}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'case_number': self.case_number,
            'type': self.type.value if self.type else None,
            'status': self.status.value if self.status else None,
            'priority': self.priority.value if self.priority else None,
            'assigned_to_id': self.assigned_to_id,
            'created_by_id': self.created_by_id,
            'owner_id': self.owner_id,
            'summary': self.summary,
            'objectives': self.objectives,
            'methodology': self.methodology,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'threat_indicators': self.threat_indicators,
            'tags': self.tags,
            'meta_data': self.meta_data,
            'external_references': self.external_references,
            'start_date': self.start_date.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'actual_completion': self.actual_completion.isoformat() if self.actual_completion else None,
            'progress_percentage': self.progress_percentage,
            'milestones': self.milestones,
            'checkpoints': self.checkpoints,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_status(self, status):
        """Update case status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == CaseStatus.RESOLVED or status == CaseStatus.CLOSED:
            self.actual_completion = datetime.utcnow()
            
        db.session.commit()
    
    def update_progress(self, percentage):
        """Update case progress"""
        self.progress_percentage = max(0, min(100, percentage))
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_milestone(self, milestone):
        """Add a milestone to the case"""
        if not self.milestones:
            self.milestones = []
        
        milestone_data = {
            'id': len(self.milestones) + 1,
            'title': milestone['title'],
            'description': milestone.get('description', ''),
            'due_date': milestone.get('due_date'),
            'completed': milestone.get('completed', False),
            'completed_at': milestone.get('completed_at'),
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.milestones.append(milestone_data)
        db.session.commit()
    
    def complete_milestone(self, milestone_id):
        """Mark a milestone as completed"""
        if self.milestones:
            for milestone in self.milestones:
                if milestone['id'] == milestone_id:
                    milestone['completed'] = True
                    milestone['completed_at'] = datetime.utcnow().isoformat()
                    db.session.commit()
                    break
    
    def add_tag(self, tag):
        """Add a tag to the case"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the case"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def update_risk_assessment(self, risk_score, risk_level, threat_indicators=None):
        """Update risk assessment"""
        self.risk_score = risk_score
        self.risk_level = risk_level
        
        if threat_indicators:
            self.threat_indicators = threat_indicators
            
        db.session.commit()
    
    def assign_user(self, user_id):
        """Assign case to a user"""
        self.assigned_to_id = user_id
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_open(self):
        """Check if case is open"""
        return self.status in [CaseStatus.OPEN, CaseStatus.IN_PROGRESS, CaseStatus.PENDING]
    
    def is_closed(self):
        """Check if case is closed"""
        return self.status in [CaseStatus.RESOLVED, CaseStatus.CLOSED, CaseStatus.ARCHIVED]
    
    def is_high_priority(self):
        """Check if case is high priority"""
        return self.priority in [CasePriority.HIGH, CasePriority.CRITICAL]
    
    def is_overdue(self):
        """Check if case is overdue"""
        if self.due_date and self.due_date < datetime.utcnow():
            return not self.is_closed()
        return False
    
    def get_tags_string(self):
        """Get tags as comma-separated string"""
        if self.tags:
            return ', '.join(self.tags)
        return ''
    
    def get_threat_indicators_string(self):
        """Get threat indicators as comma-separated string"""
        if self.threat_indicators:
            return ', '.join(self.threat_indicators)
        return ''
    
    def get_duration_days(self):
        """Get case duration in days"""
        if self.actual_completion:
            return (self.actual_completion - self.start_date).days
        elif self.is_closed():
            return (self.updated_at - self.start_date).days
        else:
            return (datetime.utcnow() - self.start_date).days 