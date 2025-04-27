from .mindObjects import MindObject
from . import db

class Project(MindObject):
    """
    Represents a passion - inherited from MindObject base class
    """
    __tablename__ = "Projects"
    
    # Project-specific columns (if any)
    # intensity = db.Column(db.Integer, nullable=True)  # 1-10 scale
    # years_pursued = db.Column(db.Integer, nullable=True)
    
    def __repr__(self):
        return f"<Project {self.topic}: {self.subtopic}>"