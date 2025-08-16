from extensions import db
from datetime import datetime
import enum

class UserCaseRole(enum.Enum):
    """Enum for user case roles"""
    OWNER = "owner"
    ASSIGNEE = "assignee"
    INVESTIGATOR = "investigator"
    ANALYST = "analyst"
    REVIEWER = "reviewer"
    VIEWER = "viewer"
    CONTRIBUTOR = "contributor"

class UserCaseStatus(enum.Enum):
    """Enum for user case status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REMOVED = "removed"

class UserCaseLink(db.Model):
    """UserCaseLink model - many-to-many relationship between users and cases"""
    __tablename__ = 'user_case_links'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    
    # Role and Status
    role = db.Column(db.Enum(UserCaseRole), nullable=False, default=UserCaseRole.VIEWER)
    status = db.Column(db.Enum(UserCaseStatus), nullable=False, default=UserCaseStatus.ACTIVE)
    
    # Permissions
    can_edit = db.Column(db.Boolean, default=False, nullable=False)
    can_delete = db.Column(db.Boolean, default=False, nullable=False)
    can_assign = db.Column(db.Boolean, default=False, nullable=False)
    can_comment = db.Column(db.Boolean, default=True, nullable=False)
    can_view_sensitive = db.Column(db.Boolean, default=False, nullable=False)
    
    # Assignment Information
    assigned_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    assignment_reason = db.Column(db.Text)
    
    # Activity Tracking
    last_activity = db.Column(db.DateTime)
    activity_count = db.Column(db.Integer, default=0)
    
    # Notes and Metadata
    notes = db.Column(db.Text)
    meta_data = db.Column(db.JSON)  # Additional metadata
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    assigned_by = db.relationship('SystemUser', foreign_keys=[assigned_by_id], backref='assigned_user_cases')
    
    # Unique constraint to prevent duplicate user-case relationships
    __table_args__ = (
        db.UniqueConstraint('user_id', 'case_id', name='uq_user_case'),
    )
    
    def __repr__(self):
        return f'<UserCaseLink {self.user_id} -> {self.case_id} ({self.role.value})>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'case_id': self.case_id,
            'role': self.role.value if self.role else None,
            'status': self.status.value if self.status else None,
            'can_edit': self.can_edit,
            'can_delete': self.can_delete,
            'can_assign': self.can_assign,
            'can_comment': self.can_comment,
            'can_view_sensitive': self.can_view_sensitive,
            'assigned_by_id': self.assigned_by_id,
            'assigned_at': self.assigned_at.isoformat(),
            'assignment_reason': self.assignment_reason,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'activity_count': self.activity_count,
            'notes': self.notes,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_role(self, role, assigned_by_id=None, reason=None):
        """Update user role in case"""
        self.role = role
        self.updated_at = datetime.utcnow()
        
        if assigned_by_id:
            self.assigned_by_id = assigned_by_id
            self.assigned_at = datetime.utcnow()
            
        if reason:
            self.assignment_reason = reason
            
        # Update permissions based on role
        self._update_permissions_for_role(role)
        
        db.session.commit()
    
    def update_status(self, status):
        """Update user case status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def update_activity(self):
        """Update last activity timestamp and count"""
        self.last_activity = datetime.utcnow()
        self.activity_count += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_note(self, note):
        """Add a note to the user case link"""
        if self.notes:
            self.notes += f"\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        else:
            self.notes = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        db.session.commit()
    
    def _update_permissions_for_role(self, role):
        """Update permissions based on role"""
        if role == UserCaseRole.OWNER:
            self.can_edit = True
            self.can_delete = True
            self.can_assign = True
            self.can_comment = True
            self.can_view_sensitive = True
        elif role == UserCaseRole.ASSIGNEE:
            self.can_edit = True
            self.can_delete = False
            self.can_assign = False
            self.can_comment = True
            self.can_view_sensitive = True
        elif role == UserCaseRole.INVESTIGATOR:
            self.can_edit = True
            self.can_delete = False
            self.can_assign = False
            self.can_comment = True
            self.can_view_sensitive = True
        elif role == UserCaseRole.ANALYST:
            self.can_edit = True
            self.can_delete = False
            self.can_assign = False
            self.can_comment = True
            self.can_view_sensitive = False
        elif role == UserCaseRole.REVIEWER:
            self.can_edit = False
            self.can_delete = False
            self.can_assign = False
            self.can_comment = True
            self.can_view_sensitive = True
        elif role == UserCaseRole.CONTRIBUTOR:
            self.can_edit = True
            self.can_delete = False
            self.can_assign = False
            self.can_comment = True
            self.can_view_sensitive = False
        else:  # VIEWER
            self.can_edit = False
            self.can_delete = False
            self.can_assign = False
            self.can_comment = False
            self.can_view_sensitive = False
    
    def is_active(self):
        """Check if user case link is active"""
        return self.status == UserCaseStatus.ACTIVE
    
    def is_owner(self):
        """Check if user is owner of the case"""
        return self.role == UserCaseRole.OWNER
    
    def is_assignee(self):
        """Check if user is assignee of the case"""
        return self.role == UserCaseRole.ASSIGNEE
    
    def can_edit_case(self):
        """Check if user can edit the case"""
        return self.is_active() and self.can_edit
    
    def can_delete_case(self):
        """Check if user can delete the case"""
        return self.is_active() and self.can_delete
    
    def can_assign_users(self):
        """Check if user can assign other users to the case"""
        return self.is_active() and self.can_assign
    
    def can_view_sensitive_data(self):
        """Check if user can view sensitive data"""
        return self.is_active() and self.can_view_sensitive
    
    def get_role_display_name(self):
        """Get display name for role"""
        role_names = {
            UserCaseRole.OWNER: "Owner",
            UserCaseRole.ASSIGNEE: "Assignee",
            UserCaseRole.INVESTIGATOR: "Investigator",
            UserCaseRole.ANALYST: "Analyst",
            UserCaseRole.REVIEWER: "Reviewer",
            UserCaseRole.VIEWER: "Viewer",
            UserCaseRole.CONTRIBUTOR: "Contributor"
        }
        return role_names.get(self.role, self.role.value.title())
    
    def get_days_since_assignment(self):
        """Get days since assignment"""
        return (datetime.utcnow() - self.assigned_at).days
    
    def get_days_since_last_activity(self):
        """Get days since last activity"""
        if self.last_activity:
            return (datetime.utcnow() - self.last_activity).days
        return None 