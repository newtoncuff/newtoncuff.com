from flask import Blueprint, render_template, jsonify, request
from constants import MIND_OBJECT_TYPES, TITLE_CONFIG
from database.database_schema import query_schema, connect_to_database
from datetime import datetime

# Create a blueprint with dynamic URL prefix
mind_object_controller = Blueprint('mind_object', __name__)

# Use the imported constants
OBJECT_TYPES = MIND_OBJECT_TYPES

@mind_object_controller.route('/<object_type>/')
def index(object_type):
    """Render the index page for the specified object type"""
    if object_type not in OBJECT_TYPES:
        return "Invalid object type", 404
    
    # Get title configuration for this object type
    title_config = TITLE_CONFIG.get(object_type, {})
    title_header = title_config.get('header', object_type.capitalize())
    title_subheader = title_config.get('subheader', "")
    
    # Prefetch the data
    model_class = OBJECT_TYPES[object_type]
    all_objects = model_class.get_all()
    
    formatted_cards = []
    for obj in all_objects:
        card = obj.to_dict()
        formatted_cards.append({
            "id": card["id"],
            "title": card["topic"],
            "content": card["topicDesc"],
            "subtopic": card["subtopic"],
            "subtopicDesc": card["subTopicDesc"],
            "tag": card["tag"],
            "hasTales": card["hasTales"],  # Assuming this is part of the object model
        })
    


    # Pass both the data and the object type
    return render_template('navigation/index.html', 
                          cards=formatted_cards,
                          objectType=object_type,
                          mindObjectType=object_type,  # Fix this to pass the actual type
                          titleHeader=title_header, 
                          titleSubHeader=title_subheader)

@mind_object_controller.route('/<object_type>/data')
def get_data(object_type):
    """Get data for the specified object type"""
    if object_type not in OBJECT_TYPES:
        return jsonify({'error': 'Invalid object type'}), 404
    
    # Get the appropriate model class
    model_class = OBJECT_TYPES[object_type]
    
    # Get all objects of this type
    all_objects = model_class.get_all()
    
    # Convert to list of dictionaries
    cards = [obj.to_dict() for obj in all_objects]
    
    # Format data for card display
    formatted_cards = []
    for card in cards:
        formatted_cards.append({
            "id": card["id"],
            "title": card["topic"],
            "content": card["topicDesc"],
            "subtopic": card["subtopic"],
            "subtopicDesc": card["subTopicDesc"],
            "tag": card["tag"]
        })
    
    return jsonify(formatted_cards)

@mind_object_controller.route('/<object_type>/addTale', methods=['POST'])
def create_tale(object_type):
    """Create a new tale for a specific mind object"""
    try:
        # Log the request for debugging
        print(f"Received tale creation request for object_type: {object_type}")
        
        # Check if request has JSON data
        if not request.is_json:
            print("Request doesn't contain JSON data")
            return jsonify({'error': 'Request must be JSON'}), 400
        
        # Get the JSON data
        data = request.json
        print(f"Received data: {data}")
        
        # Confirm all required fields are present
        required_fields = ['mindObjectTypeId', 'talltale']
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Connect to the database
        engine = connect_to_database()
        connection = engine.connect()

        try:
            # Start a transaction
            transaction = connection.begin()
            
            # Prepare the data for insertion
            mind_object_type = data.get('mindObjectType', object_type)
            mind_object_type_id = data.get('mindObjectTypeId')
            topic_title = data.get('topicTitle', '')
            date_value = data.get('date') or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            location = data.get('location', '')
            talltale = data.get('talltale', '')
            
            # Log the data for debugging
            print(f"Attempting to insert data with values: {mind_object_type}, {mind_object_type_id}, {topic_title}, {date_value}, {location}, {talltale}")
            
            # Insert the tale into the database - use %s placeholders instead of named parameters
            query = """
                INSERT INTO Tales (mindObjectType, mindObjectTypeId, topicTitle, date, location, talltale)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Execute the query with parameters as a tuple in the correct order
            result = connection.execute(query, (
                mind_object_type, 
                mind_object_type_id,
                topic_title,
                date_value,
                location,
                talltale
            ))
            transaction.commit()
            
            # Get the ID of the newly inserted tale
            new_tale_id = result.lastrowid
            
            # Recreate tale_data for response
            tale_data = {
                'mindObjectType': mind_object_type,
                'mindObjectTypeId': mind_object_type_id,
                'topicTitle': topic_title,
                'date': date_value,
                'location': location,
                'talltale': talltale
            }
            
            # Return a success response
            return jsonify({
                'success': True,
                'message': f'Tale successfully created for {object_type} with ID {mind_object_type_id}',
                'id': new_tale_id,
                'data': tale_data
            }), 201  # 201 Created status
            
        except Exception as e:
            # Roll back the transaction if there's an error
            if 'transaction' in locals():
                transaction.rollback()
            
            # Log the full error details
            print(f"Database error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Return a more specific error if possible
            if "Unknown column" in str(e):
                return jsonify({'error': f'Database schema error: {str(e)}'}), 500
            elif "Duplicate entry" in str(e):
                return jsonify({'error': 'A tale with this information already exists'}), 409
            else:
                return jsonify({'error': f'Failed to save tale to the database: {str(e)}'}), 500
                
        finally:
            # Always close the connection
            connection.close()
        
    except Exception as e:
        print(f"Error in create_tale: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@mind_object_controller.route('/routes')
def debug_routes():
    routes = []
    for rule in mind_object_controller.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "route": str(rule)
        })
    return jsonify(routes)