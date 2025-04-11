from .mindObjects import MindObject
from . import db

class Passion(MindObject):
    """
    Represents a passion - inherited from MindObject base class
    """
    __tablename__ = "Passions"
    
    # Passion-specific columns (if any)
    # intensity = db.Column(db.Integer, nullable=True)  # 1-10 scale
    # years_pursued = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<Passion {self.topic}: {self.subtopic}>"