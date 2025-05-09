from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, List, Any
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlalchemy import MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from database.database_config import database_connection_uri

# Create engine here to avoid circular imports
engine = create_engine(database_connection_uri)

# Create an APIRouter
router = APIRouter(
    prefix="/mind-objects",
    tags=["Mind Objects"],
    responses={404: {"description": "Not found"}},
)

# Models
class MindObjectBase(SQLModel):
    topic: str = Field(..., max_length=50, description="The main topic")
    topicDesc: str = Field(..., max_length=250, description="Description of the topic")
    subtopic: Optional[str] = Field(None, max_length=50, description="Optional subtopic")
    subTopicDesc: Optional[str] = Field(None, max_length=250, description="Description of the subtopic")
    tag: Optional[str] = Field(None, max_length=250, description="Tags for categorization")
    hasTales: bool = Field(False, description="Whether this object has associated tales")

class MindObjectCreate(MindObjectBase):
    tableName: str = Field(..., description="The table to insert into (Passions, Expertise, etc.)")

# Service functions
def create_mind_object(item: MindObjectCreate) -> Dict[str, Any]:
    """Create a new mind object in the database"""
    try:
        # Get the table structure using reflection
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if the requested table exists
        if item.tableName not in metadata.tables:
            raise HTTPException(status_code=404, detail=f"Table '{item.tableName}' not found")
        
        # Get the table
        table = metadata.tables[item.tableName]
        
        # Create the data dictionary for insertion
        data = {
            "topic": item.topic,
            "topicDesc": item.topicDesc,
            "hasTales": item.hasTales
        }
        
        # Add optional fields if provided
        if item.subtopic:
            data["subtopic"] = item.subtopic
        if item.subTopicDesc:
            data["subTopicDesc"] = item.subTopicDesc
        if item.tag:
            data["tag"] = item.tag
            
        # Insert into the table
        with engine.begin() as conn:
            result = conn.execute(table.insert().values(**data))
            new_id = result.inserted_primary_key[0]
            
        # Return success response
        return {
            "status": "success",
            "message": f"Created new {item.tableName} record with ID {new_id}",
            "id": new_id,
            "table": item.tableName,
            "data": {k: v for k, v in data.items()}
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def get_all_mind_objects(table_name: str) -> Dict[str, Any]:
    """Get all mind objects from a table"""
    try:
        # Get the table structure using reflection
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if the requested table exists
        if table_name not in metadata.tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get the table
        table = metadata.tables[table_name]
        
        # Query all records
        with engine.connect() as conn:
            result = conn.execute(table.select())
            records = [dict(row) for row in result]
            
        # Return all records
        return {
            "status": "success",
            "table": table_name,
            "count": len(records),
            "data": records
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def get_mind_object_by_id(table_name: str, id: int) -> Dict[str, Any]:
    """Get a specific mind object by ID"""
    try:
        # Get the table structure using reflection
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if the requested table exists
        if table_name not in metadata.tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get the table
        table = metadata.tables[table_name]
        
        # Query the specific record
        with engine.connect() as conn:
            query = table.select().where(table.c.id == id)
            result = conn.execute(query)
            record = result.first()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Record with ID {id} not found in {table_name}")
            
            # Convert to dict
            record_dict = dict(record)
            
        # Return the record
        return {
            "status": "success",
            "table": table_name,
            "id": id,
            "data": record_dict
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def update_mind_object(table_name: str, id: int, item: MindObjectCreate) -> Dict[str, Any]:
    """Update an existing mind object"""
    try:
        # Get the table structure using reflection
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if the requested table exists
        if table_name not in metadata.tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
            
        # Verify table_name matches the one in the request body
        if table_name != item.tableName:
            raise HTTPException(status_code=400, 
                detail=f"Table name mismatch. URL: '{table_name}', Body: '{item.tableName}'")
        
        # Get the table
        table = metadata.tables[table_name]
        
        # Check if the record exists
        with engine.connect() as conn:
            check_query = table.select().where(table.c.id == id)
            result = conn.execute(check_query)
            record = result.first()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Record with ID {id} not found in {table_name}")
        
        # Create the data dictionary for update
        data = {
            "topic": item.topic,
            "topicDesc": item.topicDesc,
            "hasTales": item.hasTales
        }
        
        # Add optional fields if provided
        if item.subtopic:
            data["subtopic"] = item.subtopic
        if item.subTopicDesc:
            data["subTopicDesc"] = item.subTopicDesc
        if item.tag:
            data["tag"] = item.tag
            
        # Update the record
        with engine.begin() as conn:
            update_query = table.update().where(table.c.id == id).values(**data)
            conn.execute(update_query)
            
        # Return success response
        return {
            "status": "success",
            "message": f"Successfully updated record with ID {id} in {table_name}",
            "id": id,
            "table": table_name,
            "data": data
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def delete_mind_object(table_name: str, id: int) -> Dict[str, Any]:
    """Delete a mind object by ID"""
    try:
        # Get the table structure using reflection
        metadata = MetaData()
        metadata.reflect(bind=engine)
        
        # Check if the requested table exists
        if table_name not in metadata.tables:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        # Get the table
        table = metadata.tables[table_name]
        
        # Check if the record exists before deleting
        with engine.connect() as conn:
            # Query to check if record exists
            check_query = table.select().where(table.c.id == id)
            result = conn.execute(check_query)
            record = result.first()
            
            if not record:
                raise HTTPException(status_code=404, detail=f"Record with ID {id} not found in {table_name}")
            
            # Delete the record
            delete_query = table.delete().where(table.c.id == id)
            delete_result = conn.execute(delete_query)
            conn.commit()  # Explicitly commit the transaction
            
        # Return success response
        return {
            "status": "success",
            "message": f"Successfully deleted record with ID {id} from {table_name}",
            "id": id,
            "table": table_name
        }
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
