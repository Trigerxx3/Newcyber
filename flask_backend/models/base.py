"""
Base model with common functionality
"""
from datetime import datetime
from extensions import db
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import event

class BaseModel(db.Model):
    """Base model class with common fields and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the model to the database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model from the database"""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Update model attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def to_dict(self):
        """Convert model to dictionary"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif hasattr(value, 'value'):  # For Enum types
                value = value.value
            result[column.name] = value
        return result
    
    @classmethod
    def create(cls, **kwargs):
        """Create a new instance and save it to the database"""
        instance = cls(**kwargs)
        return instance.save()
    
    @classmethod
    def get_by_id(cls, id):
        """Get instance by ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_or_404(cls, id):
        """Get instance by ID or raise 404"""
        return cls.query.get_or_404(id)


# Event listener to automatically update updated_at
@event.listens_for(BaseModel, 'before_update', propagate=True)
def receive_before_update(mapper, connection, target):
    """Update updated_at timestamp before update"""
    target.updated_at = datetime.utcnow()
