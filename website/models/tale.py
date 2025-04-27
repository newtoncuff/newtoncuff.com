from . import db
from datetime import datetime

class Tale(db.Model):
    """
    Model for storing tales related to mind objects.
    Tales are stories, experiences, or reflections about specific mind objects.
    """
    __tablename__ = 'Tales'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # References to the associated mind object
    mindObjectType = db.Column(db.String(50), nullable=False, 
                             comment='Type of mind object (Thoughts, Passions, Skills, Projects)')
    mindObjectTypeId = db.Column(db.Integer, nullable=False,
                               comment='ID of the associated mind object')
    
    # Content fields
    topicTitle = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(255), nullable=True)
    talltale = db.Column(db.Text, nullable=False)
    
    # Optional user-defined fields for flexibility
    userDefined1 = db.Column(db.String(255), nullable=True)
    userDefined2 = db.Column(db.String(255), nullable=True)
    userDefined3 = db.Column(db.String(255), nullable=True)
    userDefined4 = db.Column(db.String(255), nullable=True)
    userDefined5 = db.Column(db.String(255), nullable=True)
        
    def __repr__(self):
        """String representation of a tale"""
        return f"<Tale {self.id}: {self.topicTitle or 'Untitled'} ({self.mindObjectType}/{self.mindObjectTypeId})>"
    
    def to_dict(self):
        """Convert the model instance to a dictionary for API responses"""
        return {
            "id": self.id,
            "mindObjectType": self.mindObjectType,
            "mindObjectTypeId": self.mindObjectTypeId,
            "topicTitle": self.topicTitle,
            "date": self.date.isoformat() if self.date else None,
            "location": self.location,
            "talltale": self.talltale,
            "userDefined1": self.userDefined1,
            "userDefined2": self.userDefined2,
            "userDefined3": self.userDefined3,
            "userDefined4": self.userDefined4,
            "userDefined5": self.userDefined5
        }
    
    @classmethod
    def get_all(cls):
        """Get all tales"""
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
    def get_by_mindObjectTypeId(cls, mindObjectTypeId):
        """Get all tales with the given mindObjectTypeId"""
        db.session.expire_all()
        # Use filter_by without the all() first
        query = cls.query.filter_by(mindObjectTypeId=mindObjectTypeId)
        # Force a fresh execution
        return query.all()
    
    @classmethod
    def get_by_object(cls, object_type, object_id):
        """Get all tales for a specific mind object"""
        db.session.expire_all()
        # Chain the methods correctly
        query = cls.query.filter_by(
            mindObjectType=object_type,
            mindObjectTypeId=object_id
        ).order_by(cls.date.desc())
        # Force a fresh execution
        return query.all()
    
    @classmethod
    def search(cls, search_term):
        """Search for tales by content"""
        db.session.expire_all()
        # Chain the methods correctly
        query = cls.query.filter(
            db.or_(
                cls.topicTitle.ilike(f"%{search_term}%"),
                cls.location.ilike(f"%{search_term}%"),
                cls.talltale.ilike(f"%{search_term}%")
            )
        )
        # Force a fresh execution
        return query.all()
    
    @classmethod
    def create(cls, mind_object_type, mind_object_id, talltale, **kwargs):
        """
        Create a new tale with the given parameters.
        
        Args:
            mind_object_type (str): The type of mind object (e.g., 'passions', 'thoughts')
            mind_object_id (int): The ID of the mind object
            talltale (str): The content of the tale
            **kwargs: Additional fields like topicTitle, date, location, etc.
        
        Returns:
            Tale: The newly created tale instance
        """
        tale = cls(
            mindObjectType=mind_object_type,
            mindObjectTypeId=mind_object_id,
            talltale=talltale,
            **kwargs
        )
        db.session.add(tale)
        db.session.commit()
        return tale
    
    def update(self, **kwargs):
        """
        Update the tale with the given parameters.
        
        Args:
            **kwargs: Fields to update
            
        Returns:
            Tale: The updated tale instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        db.session.commit()
        return self
    
    def delete(self):
        """
        Delete the tale.
        
        Returns:
            bool: True if the deletion was successful
        """
        db.session.delete(self)
        db.session.commit()
        return True