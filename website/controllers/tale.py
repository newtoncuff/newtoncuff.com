from flask import Blueprint, render_template, jsonify, request
from constants import MIND_OBJECT_TYPES, TITLE_CONFIG
from database.database_schema import query_schema, connect_to_database
from datetime import datetime
import base64

# Create a blueprint with dynamic URL prefix
tale_controller = Blueprint('tale', __name__)

@tale_controller.route('/<string:topicTitle>/Tales/<string:data>')
def index(topicTitle, data):
    """Render the tales page for the specified topic"""

    try:
        # Decode the base64 data
        decoded = base64.b64decode(data.encode()).decode()
        parts = decoded.split('|')
        if len(parts) != 3:
            raise ValueError("Invalid data format")
            
        mindObjectType = parts[0]
        topicTitle = parts[1].capitalize()
        mindObjectTypeId = int(parts[2])
    except (ValueError, IndexError):
        return "Invalid URL format", 404
    
    # If mindObjectTypeId isn't provided, try to look it up by topic title
    if not mindObjectTypeId:
        # You'll need a function to look up the ID based on the title
        # This depends on your data structure
        for object_type, model in MIND_OBJECT_TYPES.items():
            if object_type != 'tale':  # Skip tales model
                # Find objects matching this topic title
                objects = model.query.filter_by(topic=topicTitle).all()
                if objects:
                    # Use the first matching object
                    mindObjectType = object_type
                    mindObjectTypeId = objects[0].id
                    break
    
    if not mindObjectTypeId:
        return jsonify({"error": "Topic not found"}), 404

    # Validate object type
    if mindObjectType not in MIND_OBJECT_TYPES:
        return jsonify({"error": "Invalid object type"}), 400
    
    # Get the model class for the specified mindObjectType
    model_class = MIND_OBJECT_TYPES.get(mindObjectType)

    # Fetch the specific object by ID using the model class
    record = model_class.get_by_id(id=mindObjectTypeId)

    # Fetch the specific object by ID
    model_class = MIND_OBJECT_TYPES.get("tale")
    all_objects = model_class.get_by_mindObjectTypeId(mindObjectTypeId)

    # Format the object data
    formatted_cards = []
    for obj in all_objects:
        card = obj.to_dict()
        formatted_cards = ({
            "id": card["id"],
            "mindObjectType": card["mindObjectType"],
            "mindObjectTypeId": card["mindObjectTypeId"],
            "topicTitle": card["topicTitle"],
            # change the date format to a more readable one
            "date": datetime.strptime(card["date"], "%Y-%m-%dT%H:%M:%S").strftime("%A %B %d %Y"),
            "location": card["location"],
            "talltale": card["talltale"],
            "userDefined1": card["userDefined1"],
            "userDefined2": card["userDefined2"],
            "userDefined3": card["userDefined3"],
            "userDefined4": card["userDefined4"],
            "userDefined5": card["userDefined5"],  # Assuming this is part of the object model
        })

    # Pass both the data and the object type
    return render_template('navigation/taleIndex.html', 
                          cards=[formatted_cards],
                          objectType=mindObjectType,
                          mindObjectType=mindObjectType,  # Pass the actual type
                          titleHeader=record.topic, 
                          titleSubHeader=record.topicDesc,)