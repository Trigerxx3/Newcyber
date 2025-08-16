from extensions import db
from datetime import datetime
import enum

class OSINTSearchType(enum.Enum):
    """Enum for OSINT search types"""
    GENERAL = "general"
    THREAT = "threat"
    PERSON = "person"
    ORGANIZATION = "organization"
    DOMAIN = "domain"
    IP_ADDRESS = "ip_address"
    EMAIL = "email"
    PHONE = "phone"
    SOCIAL_MEDIA = "social_media"
    DARK_WEB = "dark_web"
    NEWS = "news"
    TECHNICAL = "technical"

class OSINTStatus(enum.Enum):
    """Enum for OSINT result status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"

class OSINTResult(db.Model):
    """OSINTResult model for storing search results and analysis"""
    __tablename__ = 'osint_results'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=True, index=True)
    
    # Search Information
    query = db.Column(db.String(500), nullable=False, index=True)
    search_type = db.Column(db.Enum(OSINTSearchType), nullable=False, default=OSINTSearchType.GENERAL)
    status = db.Column(db.Enum(OSINTStatus), nullable=False, default=OSINTStatus.PENDING)
    
    # Search Configuration
    search_sources = db.Column(db.JSON)  # List of sources to search
    search_parameters = db.Column(db.JSON)  # Additional search parameters
    filters = db.Column(db.JSON)  # Search filters
    
    # Results and Analysis
    results = db.Column(db.JSON)  # Raw search results
    analysis = db.Column(db.JSON)  # Analysis results
    summary = db.Column(db.Text)  # Human-readable summary
    
    # Performance Metrics
    total_sources_searched = db.Column(db.Integer, default=0)
    successful_sources = db.Column(db.Integer, default=0)
    failed_sources = db.Column(db.Integer, default=0)
    processing_time = db.Column(db.Float)  # Processing time in seconds
    
    # Risk Assessment
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='low')
    threat_indicators = db.Column(db.JSON)  # Detected threat indicators
    
    # Metadata
    tags = db.Column(db.JSON)  # Tags for categorization
    notes = db.Column(db.Text)  # Analyst notes
    priority = db.Column(db.Integer, default=0)  # Priority level
    
    # Error Information
    error_message = db.Column(db.Text)
    retry_count = db.Column(db.Integer, default=0)
    last_retry = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    identifiers = db.relationship('OSINTIdentifierLink', backref='osint_result', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<OSINTResult {self.id}: {self.query[:50]} ({self.search_type.value})>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'query': self.query,
            'search_type': self.search_type.value if self.search_type else None,
            'status': self.status.value if self.status else None,
            'search_sources': self.search_sources,
            'search_parameters': self.search_parameters,
            'filters': self.filters,
            'results': self.results,
            'analysis': self.analysis,
            'summary': self.summary,
            'total_sources_searched': self.total_sources_searched,
            'successful_sources': self.successful_sources,
            'failed_sources': self.failed_sources,
            'processing_time': self.processing_time,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'threat_indicators': self.threat_indicators,
            'tags': self.tags,
            'notes': self.notes,
            'priority': self.priority,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'last_retry': self.last_retry.isoformat() if self.last_retry else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def update_status(self, status, error_message=None):
        """Update OSINT result status"""
        self.status = status
        self.updated_at = datetime.utcnow()
        
        if status == OSINTStatus.COMPLETED:
            self.completed_at = datetime.utcnow()
        
        if error_message:
            self.error_message = error_message
            
        db.session.commit()
    
    def update_results(self, results, analysis=None, summary=None):
        """Update search results and analysis"""
        self.results = results
        self.analysis = analysis
        self.summary = summary
        self.status = OSINTStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        db.session.commit()
    
    def update_metrics(self, total_sources, successful, failed, processing_time):
        """Update performance metrics"""
        self.total_sources_searched = total_sources
        self.successful_sources = successful
        self.failed_sources = failed
        self.processing_time = processing_time
        db.session.commit()
    
    def update_risk_assessment(self, risk_score, risk_level, threat_indicators=None):
        """Update risk assessment"""
        self.risk_score = risk_score
        self.risk_level = risk_level
        
        if threat_indicators:
            self.threat_indicators = threat_indicators
            
        db.session.commit()
    
    def add_tag(self, tag):
        """Add a tag to the OSINT result"""
        if not self.tags:
            self.tags = []
        
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from the OSINT result"""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def add_note(self, note):
        """Add a note to the OSINT result"""
        if self.notes:
            self.notes += f"\n{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        else:
            self.notes = f"{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}: {note}"
        db.session.commit()
    
    def increment_retry_count(self):
        """Increment retry count"""
        self.retry_count += 1
        self.last_retry = datetime.utcnow()
        db.session.commit()
    
    def is_completed(self):
        """Check if OSINT search is completed"""
        return self.status == OSINTStatus.COMPLETED
    
    def is_failed(self):
        """Check if OSINT search failed"""
        return self.status == OSINTStatus.FAILED
    
    def is_high_risk(self):
        """Check if OSINT result is high risk"""
        return self.risk_level in ['high', 'critical']
    
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
    
    def get_success_rate(self):
        """Calculate success rate"""
        if self.total_sources_searched > 0:
            return (self.successful_sources / self.total_sources_searched) * 100
        return 0 