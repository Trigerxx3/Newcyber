"""
User models for both platform users and system users
"""
import enum
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.base import BaseModel
from datetime import datetime

class SystemUserRole(enum.Enum):
    """Enum for system user roles"""
    ADMIN = 'Admin'
    ANALYST = 'Analyst'

# Platform Users (suspects from social media)
class User(BaseModel):
    """User model for platform users (suspects)"""
    __tablename__ = 'users'
    
    # Foreign key
    source_id = db.Column(db.Integer, db.ForeignKey('sources.id'), nullable=False, index=True)
    
    # User information
    platform_user_id = db.Column(db.String(255), index=True)
    username = db.Column(db.String(255), index=True)
    full_name = db.Column(db.String(255))
    bio = db.Column(db.Text)
    
    # Flags
    is_flagged = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    content = db.relationship('Content', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    case_links = db.relationship('UserCaseLink', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username or "Unknown"} ({self.platform_user_id or "No ID"})>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        data = super().to_dict()
        data['source'] = self.source.to_dict() if self.source else None
        return data
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_flagged(cls):
        """Get all flagged users"""
        return cls.query.filter_by(is_flagged=True).all()
    
    def flag_user(self):
        """Flag this user"""
        self.is_flagged = True
        db.session.commit()
    
    def unflag_user(self):
        """Unflag this user"""
        self.is_flagged = False
        db.session.commit()

# System Users (analysts, admins)
class SystemUser(BaseModel):
    """System user model for authentication"""
    __tablename__ = 'system_users'
    
    # User credentials
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User information
    role = db.Column(db.Enum(SystemUserRole), nullable=False, default=SystemUserRole.ANALYST)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<SystemUser {self.username} ({self.role.value})>'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        db.session.commit()
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert model to dictionary"""
        data = super().to_dict()
        data['role'] = self.role.value if self.role else None
        data['last_login'] = self.last_login.isoformat() if self.last_login else None
        
        if not include_sensitive:
            data.pop('password_hash', None)
        
        return data
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_active_users(cls):
        """Get all active users"""
        return cls.query.filter_by(is_active=True).all()
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == SystemUserRole.ADMIN
