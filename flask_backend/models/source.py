"""
Source model for social media sources
"""
import enum
from extensions import db
from models.base import BaseModel
from datetime import datetime

class PlatformType(enum.Enum):
    """Enum for platform types"""
    TELEGRAM = 'Telegram'
    INSTAGRAM = 'Instagram'
    WHATSAPP = 'WhatsApp'
    FACEBOOK = 'Facebook'
    TWITTER = 'Twitter'
    TIKTOK = 'TikTok'
    UNKNOWN = 'Unknown'

class SourceType(enum.Enum):
    """Enum for source types"""
    CHANNEL = 'Channel'
    GROUP = 'Group'
    PROFILE = 'Profile'

class Source(BaseModel):
    """Source model for social media sources"""
    __tablename__ = 'sources'
    
    # Source information
    platform = db.Column(db.Enum(PlatformType), nullable=False)
    source_handle = db.Column(db.String(255), unique=True, nullable=False, index=True)
    source_name = db.Column(db.String(255))
    source_type = db.Column(db.Enum(SourceType))
    
    # Scraping information
    last_scraped_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    scraping_enabled = db.Column(db.Boolean, default=True, nullable=False)
    
    # Metadata
    description = db.Column(db.Text)
    follower_count = db.Column(db.Integer)
    
    # Relationships
    users = db.relationship('User', backref='source', lazy='dynamic', cascade='all, delete-orphan')
    content = db.relationship('Content', backref='source', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Source {self.source_handle} ({self.platform.value if self.platform else "Unknown"})'
    
    def to_dict(self):
        """Convert model to dictionary"""
        data = super().to_dict()
        data['platform'] = self.platform.value if self.platform else None
        data['source_type'] = self.source_type.value if self.source_type else None
        data['last_scraped_at'] = self.last_scraped_at.isoformat() if self.last_scraped_at else None
        return data
    
    @classmethod
    def get_by_handle(cls, handle):
        """Get source by handle"""
        return cls.query.filter_by(source_handle=handle).first()
    
    @classmethod
    def get_by_platform(cls, platform):
        """Get sources by platform"""
        if isinstance(platform, str):
            platform = PlatformType(platform)
        return cls.query.filter_by(platform=platform).all()
    
    @classmethod
    def get_active(cls):
        """Get all active sources"""
        return cls.query.filter_by(is_active=True).all()
    
    def update_scraping_info(self):
        """Update last scraped timestamp"""
        self.last_scraped_at = datetime.utcnow()
        db.session.commit()
    
    def toggle_active(self):
        """Toggle active status"""
        self.is_active = not self.is_active
        db.session.commit()
        return self.is_active
