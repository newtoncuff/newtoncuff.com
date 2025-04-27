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

    hasTales = db.Column(db.Boolean, default=False)  # Indicates if the object has tales associated with it
    
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
            "tag": self.tag or "",
            "hasTales": "true" if self.hasTales else "false"  # Convert to "true" or "false" string
        }
    
    @classmethod
    def get_all(cls):
        """Get all objects of this type"""
        db.session.expire_all()
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, id):
        """Get a tale by ID"""
        db.session.expire_all()
        result = cls.query.get(id)
        if result:
            # Explicitly refresh this object from the database
            db.session.refresh(result)
        return result
    
    @classmethod
    def get_by_topic(cls, topic):
        """Get objects filtered by topic"""
        db.session.expire_all()
        query = cls.query.filter_by(topic=topic)
        # Force a fresh execution
        return query.all()
    
    @classmethod
    def search(cls, search_term):
        db.session.expire_all()
        """Search for objects by topic or description"""
        return cls.query.all().filter(
            db.or_(
                cls.topic.ilike(f"%{search_term}%"),
                cls.topicDesc.ilike(f"%{search_term}%"),
                cls.subtopic.ilike(f"%{search_term}%"),
                cls.subTopicDesc.ilike(f"%{search_term}%"),
                cls.tag.ilike(f"%{search_term}%")
            )
        ).all()