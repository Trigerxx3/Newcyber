from extensions import db
from datetime import datetime
import enum

class IdentifierType(enum.Enum):
    """Enum for identifier types"""
    EMAIL = "email"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    PERSON_NAME = "person_name"
    ORGANIZATION = "organization"
    LOCATION = "location"
    DATE = "date"
    CUSTOM = "custom"

class IdentifierStatus(enum.Enum):
    """Enum for identifier status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"

class Identifier(db.Model):
    """Identifier model for tracking entities"""
    __tablename__ = 'identifiers'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    value = db.Column(db.String(500), nullable=False, index=True)
    type = db.Column(db.Enum(IdentifierType), nullable=False, default=IdentifierType.CUSTOM)
    status = db.Column(db.Enum(IdentifierStatus), nullable=False, default=IdentifierStatus.ACTIVE)
    
    # Metadata
    description = db.Column(db.Text)
    confidence_score = db.Column(db.Float, default=0.0)
    verification_status = db.Column(db.Boolean, default=False, nullable=False)
    verification_date = db.Column(db.DateTime)
    verified_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True)
    
    # Context and Relationships
    context = db.Column(db.JSON)  # Additional context information
    aliases = db.Column(db.JSON)  # Alternative representations
    tags = db.Column(db.JSON)  # Tags for categorization
    meta_data = db.Column(db.JSON)  # Additional metadata
    
    # Usage Statistics
    detection_count = db.Column(db.Integer, default=0)
    first_detected = db.Column(db.DateTime)
    last_detected = db.Column(db.DateTime)
    
    # Risk Assessment
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='low')  # low, medium, high, critical
    threat_indicators = db.Column(db.JSON)  # Associated threat indicators
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    verified_by = db.relationship('SystemUser', foreign_keys=[verified_by_id], backref='verified_identifiers')
    osint_results = db.relationship('OSINTIdentifierLink', backref='identifier', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Identifier {self.value}: {self.type.value}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'value': self.value,
            'type': self.type.value if self.type else None,
            'status': self.status.value if self.status else None,
            'description': self.description,
            'confidence_score': self.confidence_score,
            'verification_status': self.verification_status,
            'verification_date': self.verification_date.isoformat() if self.verification_date else None,
            'verified_by_id': self.verified_by_id,
            'context': self.context,
            'aliases': self.aliases,
            'tags': self.tags,
            'meta_data': self.meta_data,
            'detection_count': self.detection_count,
            'first_detected': self.first_detected.isoformat() if self.first_detected else None,
            'last_detected': self.last_detected.isoformat() if self.last_detected else None,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'threat_indicators': self.threat_indicators,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def increment_detection_count(self):
        """Increment detection count and update timestamps"""
        self.detection_count += 1
        self.last_detected = datetime.utcnow()
        
        if not self.first_detected:
            self.first_detected = datetime.utcnow()
            
        db.session.commit()
    
    def verify(self, user_id, confidence_score=None):
        """Mark identifier as verified"""
        self.verification_status = True
        self.verified_by_id = user_id
        self.verification_date = datetime.utcnow()
        
        if confidence_score is not None:
            self.confidence_score = confidence_score
            
        db.session.commit()
    
    def add_alias(self, alias):
        """Add an alias to the identifier"""
        if not self.aliases:
            self.aliases = []
        
        if alias not in self.aliases:
            self.aliases.append(alias)
            db.session.commit()
    
    def remove_alias(self, alias):
        """Remove an alias from the identifier"""
        if self.aliases and alias in self.aliases:
            self.aliases.remove(alias)
            db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the identifier"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the identifier"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def update_risk_score(self, score, level=None):
        """Update risk score and level"""
        self.risk_score = score
        
        if level:
            self.risk_level = level
        elif score >= 0.8:
            self.risk_level = 'critical'
        elif score >= 0.6:
            self.risk_level = 'high'
        elif score >= 0.4:
            self.risk_level = 'medium'
        else:
            self.risk_level = 'low'
            
        db.session.commit()
    
    def add_threat_indicator(self, indicator):
        """Add a threat indicator"""
        if not self.threat_indicators:
            self.threat_indicators = []
        
        if indicator not in self.threat_indicators:
            self.threat_indicators.append(indicator)
            db.session.commit()
    
    def is_verified(self):
        """Check if identifier is verified"""
        return self.verification_status
    
    def is_high_risk(self):
        """Check if identifier is high risk"""
        return self.risk_level in ['high', 'critical']
    
    def is_active(self):
        """Check if identifier is active"""
        return self.status == IdentifierStatus.ACTIVE
    
    def get_aliases_string(self):
        """Get aliases as comma-separated string"""
        if self.aliases:
            return ', '.join(self.aliases)
        return ''
    
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