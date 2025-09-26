"""
Link table between cases and content items
"""
from extensions import db
from models.base import BaseModel


class CaseContentLink(BaseModel):
    __tablename__ = 'case_content_links'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False, index=True)

    # Simple uniqueness to prevent duplicate links
    __table_args__ = (
        db.UniqueConstraint('case_id', 'content_id', name='uq_case_content'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'content_id': self.content_id,
            'created_at': self.created_at.isoformat() if getattr(self, 'created_at', None) else None,
        }


