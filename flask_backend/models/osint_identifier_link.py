from extensions import db
from datetime import datetime
import enum

class LinkType(enum.Enum):
    """Enum for OSINT identifier link types"""
    DIRECT = "direct"
    INDIRECT = "indirect"
    ASSOCIATED = "associated"
    MENTIONED = "mentioned"
    REFERENCED = "referenced"
    SIMILAR = "similar"

class LinkConfidence(enum.Enum):
    """Enum for link confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class OSINTIdentifierLink(db.Model):
    """OSINTIdentifierLink model - many-to-many relationship between OSINT results and identifiers"""
    __tablename__ = 'osint_identifier_links'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    osint_result_id = db.Column(db.Integer, db.ForeignKey('osint_results.id'), nullable=False, index=True)
    identifier_id = db.Column(db.Integer, db.ForeignKey('identifiers.id'), nullable=False, index=True)
    
    # Link Information
    link_type = db.Column(db.Enum(LinkType), nullable=False, default=LinkType.DIRECT)
    confidence_score = db.Column(db.Float, default=0.0, nullable=False)
    confidence_level = db.Column(db.Enum(LinkConfidence), nullable=False, default=LinkConfidence.MEDIUM)
    
    # Context and Evidence
    context = db.Column(db.Text)  # Context where the link was found
    evidence = db.Column(db.JSON)  # Supporting evidence for the link
    source_url = db.Column(db.String(1000))  # Source URL where link was found
    source_type = db.Column(db.String(100))  # Type of source (website, social media, etc.)
    
    # Analysis Results
    analysis_notes = db.Column(db.Text)  # Analyst notes about the link
    risk_assessment = db.Column(db.JSON)  # Risk assessment for this link
    verification_status = db.Column(db.Boolean, default=False, nullable=False)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True)
    verified_at = db.Column(db.DateTime)
    
    # Metadata
    tags = db.Column(db.JSON)  # Tags for categorization
    meta_data = db.Column(db.JSON)  # Additional metadata
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    verified_by = db.relationship('SystemUser', foreign_keys=[verified_by_id], backref='verified_osint_links')
    
    # Unique constraint to prevent duplicate OSINT-identifier relationships
    __table_args__ = (
        db.UniqueConstraint('osint_result_id', 'identifier_id', name='uq_osint_identifier'),
    )
    
    def __repr__(self):
        return f'<OSINTIdentifierLink {self.osint_result_id} -> {self.identifier_id} ({self.link_type.value})>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'osint_result_id': self.osint_result_id,
            'identifier_id': self.identifier_id,
            'link_type': self.link_type.value if self.link_type else None,
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level.value if self.confidence_level else None,
            'context': self.context,
            'evidence': self.evidence,
            'source_url': self.source_url,
            'source_type': self.source_type,
            'analysis_notes': self.analysis_notes,
            'risk_assessment': self.risk_assessment,
            'verification_status': self.verification_status,
            'verified_by_id': self.verified_by_id,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'tags': self.tags,
            'meta_data': self.meta_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_confidence(self, score):
        """Update confidence score and level"""
        self.confidence_score = score
        
        if score >= 0.9:
            self.confidence_level = LinkConfidence.VERY_HIGH
        elif score >= 0.7:
            self.confidence_level = LinkConfidence.HIGH
        elif score >= 0.5:
            self.confidence_level = LinkConfidence.MEDIUM
        else:
            self.confidence_level = LinkConfidence.LOW
            
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def verify(self, user_id, notes=None):
        """Mark link as verified"""
        self.verification_status = True
        self.verified_by_id = user_id
        self.verified_at = datetime.utcnow()
        
        if notes:
            self.analysis_notes = notes
            
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_evidence(self, evidence_data):
        """Add evidence to the link"""
        if not self.evidence:
            self.evidence = []
        
        evidence_entry = {
            'id': len(self.evidence) + 1,
            'data': evidence_data,
            'added_at': datetime.utcnow().isoformat()
        }
        
        self.evidence.append(evidence_entry)
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_note(self, note):
        """Add a note to the link"""
        if self.analysis_notes:
            self.analysis_notes += f"\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        else:
            self.analysis_notes = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the link"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the link"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()
            db.session.commit()
    
    def update_risk_assessment(self, risk_data):
        """Update risk assessment"""
        self.risk_assessment = risk_data
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_verified(self):
        """Check if link is verified"""
        return self.verification_status
    
    def is_high_confidence(self):
        """Check if link has high confidence"""
        return self.confidence_level in [LinkConfidence.HIGH, LinkConfidence.VERY_HIGH]
    
    def is_direct_link(self):
        """Check if link is direct"""
        return self.link_type == LinkType.DIRECT
    
    def get_confidence_percentage(self):
        """Get confidence as percentage"""
        return int(self.confidence_score * 100)
    
    def get_tags_string(self):
        """Get tags as comma-separated string"""
        if self.tags:
            return ', '.join(self.tags)
        return ''
    
    def get_evidence_count(self):
        """Get number of evidence entries"""
        if self.evidence:
            return len(self.evidence)
        return 0
    
    def get_days_since_verification(self):
        """Get days since verification"""
        if self.verified_at:
            return (datetime.utcnow() - self.verified_at).days
        return None
    
    def get_link_type_display_name(self):
        """Get display name for link type"""
        type_names = {
            LinkType.DIRECT: "Direct",
            LinkType.INDIRECT: "Indirect",
            LinkType.ASSOCIATED: "Associated",
            LinkType.MENTIONED: "Mentioned",
            LinkType.REFERENCED: "Referenced",
            LinkType.SIMILAR: "Similar"
        }
        return type_names.get(self.link_type, self.link_type.value.title()) 