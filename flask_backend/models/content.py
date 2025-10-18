"""
Content model for analyzed social media content
"""
from extensions import db
from models.base import BaseModel
from datetime import datetime
import enum

class ContentType(enum.Enum):
    """Enum for content types"""
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    VIDEO = 'VIDEO'
    AUDIO = 'AUDIO'
    DOCUMENT = 'DOCUMENT'
    LINK = 'LINK'
    
class ContentStatus(enum.Enum):
    """Enum for content status"""
    PENDING = 'PENDING'
    ANALYZED = 'ANALYZED'
    REVIEWING = 'REVIEWING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'

class RiskLevel(enum.Enum):
    """Enum for risk levels"""
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class Content(BaseModel):
    """Content model for analyzed data"""
    __tablename__ = 'content'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False, index=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # Basic Information
    title = db.Column(db.String(500))
    text = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(1000))
    author = db.Column(db.String(200))
    content_type = db.Column(db.Enum(ContentType), nullable=False, default=ContentType.TEXT)
    
    # Analysis Results
    risk_level = db.Column(db.Enum(RiskLevel), default=RiskLevel.LOW, nullable=False)
    status = db.Column(db.Enum(ContentStatus), default=ContentStatus.PENDING, nullable=False)
    keywords = db.Column(db.JSON)  # Array of detected keywords
    analysis_summary = db.Column(db.Text)
    analysis_data = db.Column(db.JSON)  # Detailed analysis results
    suspicion_score = db.Column(db.Integer, default=0)  # Suspicion score (0-100)
    intent = db.Column(db.String(50), default='Unknown')  # Detected intent (Selling, Buying, Informational, Unknown)
    is_flagged = db.Column(db.Boolean, default=False)  # Whether content is flagged for review
    
    # Metadata
    language = db.Column(db.String(10), default='en')
    word_count = db.Column(db.Integer)
    character_count = db.Column(db.Integer)
    sentiment_score = db.Column(db.Float)
    confidence_score = db.Column(db.Float)
    
    # Processing Information
    processing_time = db.Column(db.Float)  # Processing time in seconds
    analysis_version = db.Column(db.String(50))  # Version of analysis algorithm used
    last_analyzed = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    detections = db.relationship('Detection', backref='content', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Content {self.id}: {self.title[:50] if self.title else "No title"}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'source_id': self.source_id,
            'created_by_id': self.created_by_id,
            'title': self.title,
            'text': self.text,
            'url': self.url,
            'author': self.author,
            'content_type': self.content_type.value if self.content_type else None,
            'risk_level': self.risk_level.value if self.risk_level else None,
            'status': self.status.value if self.status else None,
            'keywords': self.keywords,
            'analysis_summary': self.analysis_summary,
            'analysis_data': self.analysis_data,
            'suspicion_score': self.suspicion_score,
            'intent': self.intent,
            'is_flagged': self.is_flagged,
            'language': self.language,
            'word_count': self.word_count,
            'character_count': self.character_count,
            'sentiment_score': self.sentiment_score,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'analysis_version': self.analysis_version,
            'last_analyzed': self.last_analyzed.isoformat() if self.last_analyzed else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def update_analysis(self, analysis_data, risk_level=None, keywords=None, summary=None, 
                       suspicion_score=None, intent=None, is_flagged=None):
        """Update content analysis results"""
        self.analysis_data = analysis_data
        self.last_analyzed = datetime.utcnow()
        self.status = ContentStatus.ANALYZED
        
        if risk_level:
            self.risk_level = risk_level
        if keywords:
            self.keywords = keywords
        if summary:
            self.analysis_summary = summary
        if suspicion_score is not None:
            self.suspicion_score = suspicion_score
        if intent:
            self.intent = intent
        if is_flagged is not None:
            self.is_flagged = is_flagged
            
        db.session.commit()
    
    def add_keyword(self, keyword):
        """Add a keyword to the content"""
        if not self.keywords:
            self.keywords = []
        
        if keyword not in self.keywords:
            self.keywords.append(keyword)
            db.session.commit()
    
    def remove_keyword(self, keyword):
        """Remove a keyword from the content"""
        if self.keywords and keyword in self.keywords:
            self.keywords.remove(keyword)
            db.session.commit()
    
    def get_keywords_string(self):
        """Get keywords as comma-separated string"""
        if self.keywords:
            return ', '.join(self.keywords)
        return ''
    
    def get_text_preview(self, length=200):
        """Get text preview"""
        if self.text:
            return self.text[:length] + '...' if len(self.text) > length else self.text
        return ''
    
    def calculate_metrics(self):
        """Calculate text metrics"""
        if self.text:
            self.word_count = len(self.text.split())
            self.character_count = len(self.text)
            db.session.commit()
    
    def is_high_risk(self):
        """Check if content is high risk"""
        return self.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def is_analyzed(self):
        """Check if content has been analyzed"""
        return self.status == ContentStatus.ANALYZED 