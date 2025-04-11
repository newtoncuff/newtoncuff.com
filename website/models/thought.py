from .mindObjects import MindObject
from . import db

class Thought(MindObject):
    """
    Represents a thought - inherited from MindObject base class
    """
    __tablename__ = "Thoughts"
    
    # Thought-specific columns (if any)
    # depth = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<Thought {self.topic}: {self.subtopic}>"