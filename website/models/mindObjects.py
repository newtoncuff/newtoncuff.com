from . import db

class MindObject(db.Model):
    """
    Base class for mind-related objects like Delusions, Thoughts, Passions, etc.
    This is an abstract base class that shouldn't be instantiated directly.
    """
    __abstract__ = True  # This makes it an abstract base class
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Main topic fields
    topic = db.Column(db.String(50), nullable=False)
    topicDesc = db.Column(db.String(250), nullable=False)
    
    # Sub-topic fields
    subtopic = db.Column(db.String(50), nullable=True)
    subTopicDesc = db.Column(db.String(250), nullable=True)
    
    # Tags for categorization
    tag = db.Column(db.String(250), nullable=True)
    
    # Common methods for all mind objects
    def __repr__(self):
        """String representation of a mind object"""
        return f"<{self.__class__.__name__} {self.id}: {self.topic}>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary for API responses"""
        return {
            "id": self.id,
            "topic": self.topic,
            "topicDesc": self.topicDesc,
            "subtopic": self.subtopic or "",
            "subTopicDesc": self.subTopicDesc or "",
            "tag": self.tag or ""
        }
    
    @classmethod
    def get_all(cls):
        """Get all objects of this type"""
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        """Get an object by ID"""
        return cls.query.get(id)
    
    @classmethod
    def get_by_topic(cls, topic):
        """Get objects filtered by topic"""
        return cls.query.filter_by(topic=topic).all()
    
    @classmethod
    def search(cls, search_term):
        """Search for objects by topic or description"""
        return cls.query.filter(
            db.or_(
                cls.topic.ilike(f"%{search_term}%"),
                cls.topicDesc.ilike(f"%{search_term}%"),
                cls.subtopic.ilike(f"%{search_term}%"),
                cls.subTopicDesc.ilike(f"%{search_term}%"),
                cls.tag.ilike(f"%{search_term}%")
            )
        ).all()