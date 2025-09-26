from extensions import db
from datetime import datetime
import enum

class RequestStatus(enum.Enum):
    """Enum for case request status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class CaseRequest(db.Model):
    """Model for case creation requests requiring admin approval"""
    __tablename__ = 'case_requests'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Request Information
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    case_type = db.Column(db.String(50))
    priority = db.Column(db.String(20))
    summary = db.Column(db.Text)
    objectives = db.Column(db.Text)
    methodology = db.Column(db.Text)
    tags = db.Column(db.JSON)
    
    # Request Details
    status = db.Column(db.Enum(RequestStatus), nullable=False, default=RequestStatus.PENDING)
    requested_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True)
    review_notes = db.Column(db.Text)
    
    # Timestamps
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requested_by = db.relationship('SystemUser', foreign_keys=[requested_by_id], backref='case_requests_made')
    reviewed_by = db.relationship('SystemUser', foreign_keys=[reviewed_by_id], backref='case_requests_reviewed')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'case_type': self.case_type,
            'priority': self.priority,
            'summary': self.summary,
            'objectives': self.objectives,
            'methodology': self.methodology,
            'tags': self.tags,
            'status': self.status.value if self.status else None,
            'requested_by_id': self.requested_by_id,
            'reviewed_by_id': self.reviewed_by_id,
            'review_notes': self.review_notes,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'requested_by': {
                'id': self.requested_by.id,
                'username': self.requested_by.username,
                'email': self.requested_by.email
            } if self.requested_by else None,
            'reviewed_by': {
                'id': self.reviewed_by.id,
                'username': self.reviewed_by.username,
                'email': self.reviewed_by.email
            } if self.reviewed_by else None
        }

