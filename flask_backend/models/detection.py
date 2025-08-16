from extensions import db
from datetime import datetime
import enum

class DetectionStatus(enum.Enum):
    """Enum for detection status"""
    NEW = "new"
    REVIEWED = "reviewed"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    IGNORED = "ignored"
    ESCALATED = "escalated"

class DetectionConfidence(enum.Enum):
    """Enum for detection confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class Detection(db.Model):
    """Detection model - link table between content and keywords"""
    __tablename__ = 'detections'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False, index=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('keywords.id'), nullable=False, index=True)
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False, index=True)
    detected_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True, index=True)
    
    # Detection Details
    matched_text = db.Column(db.Text)  # The actual text that matched
    context_before = db.Column(db.Text)  # Text before the match
    context_after = db.Column(db.Text)  # Text after the match
    position_start = db.Column(db.Integer)  # Start position in text
    position_end = db.Column(db.Integer)  # End position in text
    
    # Analysis Results
    confidence_score = db.Column(db.Float, nullable=False, default=0.0)
    confidence_level = db.Column(db.Enum(DetectionConfidence), nullable=False, default=DetectionConfidence.MEDIUM)
    status = db.Column(db.Enum(DetectionStatus), nullable=False, default=DetectionStatus.NEW)
    
    # Additional Data
    meta_data = db.Column(db.JSON)  # Additional detection metadata
    notes = db.Column(db.Text)  # Analyst notes
    tags = db.Column(db.JSON)  # Tags for categorization
    
    # Review Information
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    reviewed_by = db.relationship('SystemUser', foreign_keys=[reviewed_by_id], backref='reviewed_detections')
    
    def __repr__(self):
        return f'<Detection {self.id}: {self.keyword.keyword if self.keyword else "Unknown"} in Content {self.content_id}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'content_id': self.content_id,
            'keyword_id': self.keyword_id,
            'source_id': self.source_id,
            'detected_by_id': self.detected_by_id,
            'matched_text': self.matched_text,
            'context_before': self.context_before,
            'context_after': self.context_after,
            'position_start': self.position_start,
            'position_end': self.position_end,
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level.value if self.confidence_level else None,
            'status': self.status.value if self.status else None,
            'meta_data': self.meta_data,
            'notes': self.notes,
            'tags': self.tags,
            'reviewed_by_id': self.reviewed_by_id,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'review_notes': self.review_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_confidence(self, score):
        """Update confidence score and level"""
        self.confidence_score = score
        
        if score >= 0.9:
            self.confidence_level = DetectionConfidence.VERY_HIGH
        elif score >= 0.7:
            self.confidence_level = DetectionConfidence.HIGH
        elif score >= 0.5:
            self.confidence_level = DetectionConfidence.MEDIUM
        else:
            self.confidence_level = DetectionConfidence.LOW
            
        db.session.commit()
    
    def mark_reviewed(self, user_id, status, notes=None):
        """Mark detection as reviewed"""
        self.status = status
        self.reviewed_by_id = user_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = notes
        db.session.commit()
    
    def add_note(self, note):
        """Add a note to the detection"""
        if self.notes:
            self.notes += f"\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        else:
            self.notes = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the detection"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the detection"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def get_context(self, context_length=100):
        """Get full context around the detection"""
        context = ""
        if self.context_before:
            context += self.context_before[-context_length:] + " "
        context += f"[{self.matched_text}]"
        if self.context_after:
            context += " " + self.context_after[:context_length]
        return context
    
    def is_high_confidence(self):
        """Check if detection has high confidence"""
        return self.confidence_level in [DetectionConfidence.HIGH, DetectionConfidence.VERY_HIGH]
    
    def is_confirmed(self):
        """Check if detection is confirmed"""
        return self.status == DetectionStatus.CONFIRMED
    
    def is_false_positive(self):
        """Check if detection is marked as false positive"""
        return self.status == DetectionStatus.FALSE_POSITIVE
    
    def get_tags_string(self):
        """Get tags as comma-separated string"""
        if self.tags:
            return ', '.join(self.tags)
        return '' 