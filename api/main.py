from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import Response
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, create_engine
from pytz import timezone, utc
import json

# Import from database config
from database.database_config import database_connection_uri



# Create app
app = FastAPI(
    title="Newton Cuff API",
    description="API for managing Newton Cuff website content",
    version="1.0.0"
)

# Dependency: Get the session
def get_session():
    with Session(engine) as session:
        yield session

@app.get("/api_alive")
def api_alive(pretty: bool = True):
    """Returns the current local time in the US/Central timezone."""
    try:
        # Get current UTC time
        utc_time = datetime.now(utc)
        
        # Convert to US/Central timezone
        central = timezone('US/Central')
        central_time = utc_time.astimezone(central)
        formatted_time = central_time.strftime('%Y-%m-%d %H:%M:%S')
        
        response_data = {"current_datetime": formatted_time}
        
        if pretty:
            formatted_json = json.dumps(response_data, indent=4)
            return Response(content=formatted_json, media_type="application/json")
        else:
            return response_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/db_alive")
def db_alive(pretty: bool = True):
    """Connects to the MySQL database and executes a raw SQL query."""
    try:
        query = "SELECT NOW() AS current_datetime;"
        
        # Timezone conversion logic
        central = timezone('US/Central')
        
        with engine.connect() as connection:
            result = connection.execute(text(query))
            records = [dict(row) for row in result]
            for record in records:
                # Check if already a datetime object
                if isinstance(record['current_datetime'], datetime):
                    dt_obj = record['current_datetime']
                else:
                    # Parse string to datetime
                    dt_obj = datetime.strptime(record['current_datetime'], '%Y-%m-%d %H:%M:%S')
                
                # Localize and convert timezone
                if dt_obj.tzinfo is None:
                    dt_obj = utc.localize(dt_obj)
                
                # Convert to central time
                central_time = dt_obj.astimezone(central)
                record['current_datetime'] = central_time.strftime('%Y-%m-%d %H:%M:%S')

        # Get the formatted time from the updated record
        formatted_time = records[0]['current_datetime']
        
        response_data = {"database_time": formatted_time}
        
        if pretty:
            formatted_json = json.dumps(response_data, indent=4)
            return Response(content=formatted_json, media_type="application/json")
        else:
            return response_data
    except SQLAlchemyError as e:
        return {"error": str(e)}
    
# Mind Object API Routes
# Import models and services from mindObject
from models.mindObject import (
    MindObjectCreate, 
    create_mind_object,
    get_all_mind_objects,
    get_all_mind_object_types,
    get_mind_object_by_id,
    update_mind_object,
    delete_mind_object,
    engine  # Import the engine from mindObject.py
)

@app.post("/create_mindObject")
async def create_mindObject(item: MindObjectCreate):
    """Creates a new record in the specified mind object table."""
    return create_mind_object(item)

@app.get("/getAll_mindObject_types")
async def getAll_mindObject_types():
    """Retrieves all mind object types from dastabase metadata."""
    return get_all_mind_object_types()

@app.get("/getAll_mindObjects/{table_name}")
async def getAll_mindObjects(table_name: str):
    """Retrieves all records from the specified mind object table."""
    return get_all_mind_objects(table_name)

@app.get("/get_mindObject_by_id/{table_name}/{id}")
async def get_mindObject_by_id(table_name: str, id: int):
    """Retrieves a specific record from the specified mind object table by ID."""
    return get_mind_object_by_id(table_name, id)

@app.put("/update_mindObject/{table_name}/{id}")
async def update_mindObject(table_name: str, id: int, item: MindObjectCreate):
    """Updates a record in the specified mind object table by ID."""
    return update_mind_object(table_name, id, item)

@app.delete("/delete_mindObject/{table_name}/{id}")
async def delete_mindObject(table_name: str, id: int):
    """Deletes a record from the specified mind object table by ID."""
    return delete_mind_object(table_name, id)
# END Mind Object API Routes

# Tale API Routes
# Import models and services from tale
from models.tale import (
    Tale,
    create,
    get_all,
    get_by_id,
    get_by_mindobject,
    update,
    delete
)

@app.post("/create_tale")
async def create_tale(tale: Tale, session: Session = Depends(get_session)):
    """Creates a new tale record linked to a mind object."""
    return create(tale, session)

@app.get("/getAll_tales")
async def getAll_tale(session: Session = Depends(get_session)):
    """Retrieves all tale records."""
    tales = get_all(session)
    tales_list = [
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
        } for tale in tales
    ]
    return {"status": "success", "count": len(tales_list), "data": tales_list}

@app.get("/get_tale_by_id/{tale_id}")
async def get_by_id(tale_id: int, session: Session = Depends(get_session)):
    """Retrieves a specific tale by ID."""
    return get_by_id(tale_id, session)

@app.put("/update_tale/{tale_id}")
async def api_update_tale(tale_id: int, tale: Tale, session: Session = Depends(get_session)):
    """Updates a tale record."""
    return update(tale_id, tale, session)

@app.delete("/delete_tale/{tale_id}")
async def api_delete_tale(tale_id: int, session: Session = Depends(get_session)):
    """Deletes a tale record."""
    return delete(tale_id, session)

@app.get("/get_tale_by_mindObject/{mindObjectType}/{mindObjectTypeId}")
async def api_get_tales_by_mind_object(mindObjectType: str, mindObjectTypeId: int, session: Session = Depends(get_session)):
    return get_by_mindobject(mindObjectType, mindObjectTypeId, session)

# END Tale API Routes
