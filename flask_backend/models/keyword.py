from extensions import db
from datetime import datetime
import enum

class KeywordType(enum.Enum):
    """Enum for keyword types"""
    THREAT = "threat"
    MALWARE = "malware"
    EXPLOIT = "exploit"
    VULNERABILITY = "vulnerability"
    ATTACK = "attack"
    PERSON = "person"
    ORGANIZATION = "organization"
    LOCATION = "location"
    TECHNOLOGY = "technology"
    EVENT = "event"
    CUSTOM = "custom"

class KeywordSeverity(enum.Enum):
    """Enum for keyword severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class KeywordStatus(enum.Enum):
    """Enum for keyword status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    TESTING = "testing"

class Keyword(db.Model):
    """Keyword model for threat detection"""
    __tablename__ = 'keywords'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Basic Information
    keyword = db.Column(db.String(255), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    type = db.Column(db.Enum(KeywordType), nullable=False, default=KeywordType.CUSTOM)
    severity = db.Column(db.Enum(KeywordSeverity), nullable=False, default=KeywordSeverity.MEDIUM)
    status = db.Column(db.Enum(KeywordStatus), nullable=False, default=KeywordStatus.ACTIVE)
    
    # Pattern Matching
    pattern = db.Column(db.String(500))  # Regex pattern for matching
    is_regex = db.Column(db.Boolean, default=False, nullable=False)
    case_sensitive = db.Column(db.Boolean, default=False, nullable=False)
    
    # Context and Metadata
    context = db.Column(db.JSON)  # Additional context information
    aliases = db.Column(db.JSON)  # Alternative spellings/variations
    tags = db.Column(db.JSON)  # Tags for categorization
    
    # Usage Statistics
    detection_count = db.Column(db.Integer, default=0)
    last_detected = db.Column(db.DateTime)
    first_detected = db.Column(db.DateTime)
    
    # Configuration
    confidence_threshold = db.Column(db.Float, default=0.8)  # Minimum confidence for detection
    cooldown_period = db.Column(db.Integer, default=0)  # Cooldown period in seconds
    
    # Relationships
    detections = db.relationship('Detection', backref='keyword', lazy='dynamic')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Keyword {self.keyword}: {self.type.value}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'keyword': self.keyword,
            'description': self.description,
            'type': self.type.value if self.type else None,
            'severity': self.severity.value if self.severity else None,
            'status': self.status.value if self.status else None,
            'pattern': self.pattern,
            'is_regex': self.is_regex,
            'case_sensitive': self.case_sensitive,
            'context': self.context,
            'aliases': self.aliases,
            'tags': self.tags,
            'detection_count': self.detection_count,
            'last_detected': self.last_detected.isoformat() if self.last_detected else None,
            'first_detected': self.first_detected.isoformat() if self.first_detected else None,
            'confidence_threshold': self.confidence_threshold,
            'cooldown_period': self.cooldown_period,
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
    
    def add_alias(self, alias):
        """Add an alias to the keyword"""
        if not self.aliases:
            self.aliases = []
        
        if alias not in self.aliases:
            self.aliases.append(alias)
            db.session.commit()
    
    def remove_alias(self, alias):
        """Remove an alias from the keyword"""
        if self.aliases and alias in self.aliases:
            self.aliases.remove(alias)
            db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the keyword"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the keyword"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def is_active(self):
        """Check if keyword is active"""
        return self.status == KeywordStatus.ACTIVE
    
    def is_critical(self):
        """Check if keyword is critical severity"""
        return self.severity == KeywordSeverity.CRITICAL
    
    def get_pattern_for_matching(self):
        """Get the pattern to use for matching"""
        if self.is_regex and self.pattern:
            return self.pattern
        return self.keyword
    
    def matches_text(self, text):
        """Check if keyword matches text"""
        import re
        
        if not text:
            return False
        
        pattern = self.get_pattern_for_matching()
        
        if self.is_regex:
            flags = 0 if self.case_sensitive else re.IGNORECASE
            return bool(re.search(pattern, text, flags))
        else:
            if self.case_sensitive:
                return pattern in text
            else:
                return pattern.lower() in text.lower()
    
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