from fastapi import HTTPException, Depends
from typing import Optional, Dict, List, Any
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from database.database_config import database_connection_uri
from sqlalchemy import inspect

# Models
class Tale(SQLModel, table=True):  # Add table=True here
    __tablename__ = "Tales"  # Explicitly specify the table name
    
    id: Optional[int] = Field(default=None, primary_key=True)
    mindObjectType: str = Field(..., max_length=50)
    mindObjectTypeId: int = Field(...)
    topicTitle: Optional[str] = Field(None, max_length=255)
    date: datetime = Field(default_factory=datetime.utcnow)
    location: Optional[str] = Field(None, max_length=255)
    talltale: str = Field(..., sa_column_kwargs={"type_": "LONGTEXT"})
    userDefined1: Optional[str] = Field(None, max_length=255)
    userDefined2: Optional[str] = Field(None, max_length=255)
    userDefined3: Optional[str] = Field(None, max_length=255)
    userDefined4: Optional[str] = Field(None, max_length=255)
    userDefined5: Optional[str] = Field(None, max_length=255)

# Create engine here to avoid circular imports
engine = create_engine(database_connection_uri)
SQLModel.metadata.create_all(engine)

# Dependency: Get the session
def get_session():
    with Session(engine) as session:
        yield session

# CRUD Functions
def create(tale: Tale, session: Session = Depends(get_session)) -> Dict[str, Any]:
    try:
        # Check if mindObjectType is a valid table in the database - FIX HERE
        inspector = inspect(engine)
        if not inspector.has_table(tale.mindObjectType):
            raise HTTPException(status_code=400, detail=f"Invalid mindObjectType: {tale.mindObjectType} is not a valid table")

        # Rest of your function remains the same
        # Dynamically construct the query to check if the record exists
        query = f"SELECT 1 FROM {tale.mindObjectType} WHERE id = :id LIMIT 1"
        result = session.execute(query, {"id": tale.mindObjectTypeId}).fetchone()
        
        if not result:
            raise HTTPException(status_code=400, detail=f"No record found in {tale.mindObjectType} with id {tale.mindObjectTypeId}")

        session.add(tale)
        session.commit()
        session.refresh(tale)

        # Update the hasTales column in the linked record
        #update_query = f"UPDATE {tale.mindObjectType} SET hasTales = 1 WHERE id = :id"
        #session.execute(update_query, {"id": tale.mindObjectTypeId})
        #session.commit()

        # Convert to dict
        tale_data = {
            "id": tale.id,
            "mindObjectType": tale.mindObjectType,
            "mindObjectTypeId": tale.mindObjectTypeId,
            "topicTitle": tale.topicTitle,
            "date": tale.date.isoformat() if tale.date else None,
            "location": tale.location,
            "talltale": tale.talltale,
            "userDefined1": tale.userDefined1,
            "userDefined2": tale.userDefined2,
            "userDefined3": tale.userDefined3,
            "userDefined4": tale.userDefined4,
            "userDefined5": tale.userDefined5
        }
        
        return {
            "status": "success",
            "id": tale.id,
            "data": tale_data
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def get_all(session: Session = Depends(get_session)):
    tales = session.exec(select(Tale)).all()
    return tales

def get_by_id(tale_id: int, session: Session = Depends(get_session)) -> Dict[str, Any]:
    try:
        # Query the tale by ID
        tale = session.get(Tale, tale_id)
        
        # Check if tale exists
        if not tale:
            raise HTTPException(status_code=404, detail=f"Tale with ID {tale_id} not found")
        
        # Convert to dict
        tale_data = {
            "id": tale.id,
            "mindObjectType": tale.mindObjectType,
            "mindObjectTypeId": tale.mindObjectTypeId,
            "topicTitle": tale.topicTitle,
            "date": tale.date.isoformat() if tale.date else None,
            "location": tale.location,
            "talltale": tale.talltale,
            "userDefined1": tale.userDefined1,
            "userDefined2": tale.userDefined2,
            "userDefined3": tale.userDefined3,
            "userDefined4": tale.userDefined4,
            "userDefined5": tale.userDefined5
        }
        
        return {
            "status": "success",
            "id": tale_id,
            "data": tale_data
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
def get_by_mindobject(mindObjectType: str, mindObjectTypeId: int, session: Session = Depends(get_session)) -> List[Dict[str, Any]]:
    try:
        # Check if mindObjectType is a valid table in the database
        if not engine.dialect.has_table(engine, mindObjectType):
            raise HTTPException(status_code=400, detail=f"Invalid mindObjectType: {mindObjectType} is not a valid table")

        # Query tales by mindObjectType and mindObjectTypeId
        query = select(Tale).where(
            Tale.mindObjectType == mindObjectType,
            Tale.mindObjectTypeId == mindObjectTypeId
        )
        tales = session.exec(query).all()

        # Convert each tale to a dictionary
        tales_data = [
            {
                "id": tale.id,
                "mindObjectType": tale.mindObjectType,
                "mindObjectTypeId": tale.mindObjectTypeId,
                "topicTitle": tale.topicTitle,
                "date": tale.date.isoformat() if tale.date else None,
                "location": tale.location,
                "talltale": tale.talltale,
                "userDefined1": tale.userDefined1,
                "userDefined2": tale.userDefined2,
                "userDefined3": tale.userDefined3,
                "userDefined4": tale.userDefined4,
                "userDefined5": tale.userDefined5
            }
            for tale in tales
        ]

        return tales_data

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def update(tale_id: int, tale_update: Tale, session: Session = Depends(get_session)) -> Dict[str, Any]:
    try:
        # Get the tale by ID
        tale = session.get(Tale, tale_id)
        
        # Check if tale exists
        if not tale:
            raise HTTPException(status_code=404, detail=f"Tale with ID {tale_id} not found")
        
        # Update tale attributes
        tale.mindObjectType = tale_update.mindObjectType
        tale.mindObjectTypeId = tale_update.mindObjectTypeId
        tale.topicTitle = tale_update.topicTitle
        tale.date = tale_update.date
        tale.location = tale_update.location
        tale.talltale = tale_update.talltale
        tale.userDefined1 = tale_update.userDefined1
        tale.userDefined2 = tale_update.userDefined2
        tale.userDefined3 = tale_update.userDefined3
        tale.userDefined4 = tale_update.userDefined4
        tale.userDefined5 = tale_update.userDefined5
        
        # Commit the changes
        session.add(tale)
        session.commit()
        session.refresh(tale)
        
        # Convert to dict for response
        tale_data = {
            "id": tale.id,
            "mindObjectType": tale.mindObjectType,
            "mindObjectTypeId": tale.mindObjectTypeId,
            "topicTitle": tale.topicTitle,
            "date": tale.date.isoformat() if tale.date else None,
            "location": tale.location,
            "talltale": tale.talltale,
            "userDefined1": tale.userDefined1,
            "userDefined2": tale.userDefined2,
            "userDefined3": tale.userDefined3,
            "userDefined4": tale.userDefined4,
            "userDefined5": tale.userDefined5
        }
        
        return {
            "status": "success",
            "message": f"Successfully updated tale with ID {tale_id}",
            "id": tale_id,
            "data": tale_data
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def delete(tale_id: int, session: Session = Depends(get_session)) -> Dict[str, Any]:
    try:
        # Get the tale by ID
        tale = session.get(Tale, tale_id)
        
        # Check if tale exists
        if not tale:
            raise HTTPException(status_code=404, detail=f"Tale with ID {tale_id} not found")
        
        # Delete the tale
        session.delete(tale)
        session.commit()

        # Check if there are any remaining tales with the same mindObjectType and mindObjectTypeId
        query = select(Tale).where(
            Tale.mindObjectType == tale.mindObjectType,
            Tale.mindObjectTypeId == tale.mindObjectTypeId
        )
        remaining_tales = session.exec(query).all()

        # If no remaining tales are found, update the hasTales column to 0
        if not remaining_tales:
            update_query = f"UPDATE {tale.mindObjectType} SET hasTales = 0 WHERE id = :id"
            session.execute(update_query, {"id": tale.mindObjectTypeId})
            session.commit()
        
        return {
            "status": "success",
            "message": f"Successfully deleted tale with ID {tale_id}",
            "id": tale_id
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")