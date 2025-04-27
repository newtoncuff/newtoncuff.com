from flask import Blueprint, render_template, jsonify, request
from constants import MIND_OBJECT_TYPES, TITLE_CONFIG
from database.database_schema import query_schema, connect_to_database
from datetime import datetime
import base64

# Create a blueprint with dynamic URL prefix
tale_controller = Blueprint('tale', __name__)

@tale_controller.route('/<string:topicTitle>/Tales/<string:data>')
@tale_controller.route('/<string:topicTitle>/Tales/')
def index(topicTitle, data=None):
    """Render the tales page for the specified topic"""

    # Check if data is provided via URL
    if data:
        try:
            # Decode the base64 data
            decoded = base64.b64decode(data.encode()).decode()
            parts = decoded.split('|')
            if len(parts) != 3:
                raise ValueError("Invalid data format")
                
            mindObjectType = parts[0]
            encoded_topic = parts[1].capitalize()
            mindObjectTypeId = int(parts[2])
        except (ValueError, IndexError):
            return "Invalid URL format", 404
    else:
        # No data provided, try to look up the object by topicTitle
        mindObjectType = None
        mindObjectTypeId = None
    
    # Check if we're retrieving all tales or tales for a specific object
    if not mindObjectType or not mindObjectTypeId:
        # Retrieve all tales
        model_class = MIND_OBJECT_TYPES.get("tale")
        all_objects = model_class.get_all()  # Assuming you have a get_all method
        
        # Use a generic header for all tales
        title_header = "All Tales"
        title_subheader = "A collection of all tales across all mind objects"
        
        # Since we don't have a specific record, we'll set it to None
        record = None
    else:
        # Validate object type
        if mindObjectType not in MIND_OBJECT_TYPES:
            return jsonify({"error": "Invalid object type"}), 400
        
        # Get the model class for the specified mindObjectType
        model_class = MIND_OBJECT_TYPES.get(mindObjectType)

        # Fetch the specific object by ID using the model class
        record = model_class.get_by_id(id=mindObjectTypeId)
        if not record:
            return jsonify({"error": f"Record with ID {mindObjectTypeId} not found"}), 404

        # Fetch tales for this specific object
        tale_model = MIND_OBJECT_TYPES.get("tale")
        all_objects = tale_model.get_by_mindObjectTypeId(mindObjectTypeId)
        
        # Set headers based on the record
        title_header = record.topic
        title_subheader = record.topicDesc

    # Check if all_objects is None
    if all_objects is None:
        all_objects = []  # Initialize to empty list if None

    # Format the object data
    formatted_cards = []
    for obj in all_objects:
        card = obj.to_dict()
        formatted_cards.append({
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

    # Log the count of formatted_cards for debugging
    print(f"Debug: Number of formatted cards: {len(formatted_cards)}")

    # Pass both the data and the object type
    return render_template('navigation/taleIndex.html', 
                        cards=formatted_cards,  # Changed from [formatted_cards] to formatted_cards
                        objectType=mindObjectType or "all",  # Use "all" when mindObjectType is None
                        mindObjectType=mindObjectType or "all",  # Same here
                        titleHeader=title_header, 
                        titleSubHeader=title_subheader)

@tale_controller.route('/Tales')
def all_tales():
    """Render a page showing all tales"""
    # Just call the index function with None for both params
    return index(None, None)