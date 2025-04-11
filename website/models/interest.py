from .mindObjects import MindObject
from . import db

class Interest(MindObject):
    """
    Represents an interest - inherited from MindObject base class
    """
    __tablename__ = "Interests"
    
    # Interest-specific columns (if any)
    # level = db.Column(db.String(20), nullable=True)  # beginner, intermediate, expert
    
    def __repr__(self):
        return f"<Interest {self.topic}: {self.subtopic}>"