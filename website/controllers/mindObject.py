from flask import Blueprint, render_template, jsonify, request, current_app, make_response
from constants import MIND_OBJECT_TYPES, TITLE_CONFIG
from database.database_schema import query_schema, connect_to_database
from datetime import datetime
from redis_cache import cached, RedisCache

# Create a blueprint with dynamic URL prefix
mind_object_controller = Blueprint('mind_object', __name__)

# Use the imported constants
OBJECT_TYPES = MIND_OBJECT_TYPES

"""<-----Method Docstring
Handles the request to display the index page for a specific mind object type.
Args:
    object_type (str): The type of the mind object to display. Expected to be in lowercase.
Returns:
    Response: A rendered HTML template with the list of objects and their details if the object type is valid.
    Tuple: A tuple containing an error message and a 404 status code if the object type is invalid.
Behavior:
    - Logs the access to the mind object index.
    - Converts the provided object type to lowercase for consistency.
    - Validates the object type against a predefined list of valid types (OBJECT_TYPES).
    - Retrieves the title configuration for the object type, including header and subheader.
    - Fetches all objects of the specified type using the corresponding model class.
    - Formats the objects into a list of dictionaries for rendering.
    - Renders the 'navigation/index.html' template with the formatted data and title information.
    - Returns the rendered template as a response.
Raises:
    KeyError: If the object type is not found in the OBJECT_TYPES dictionary.
"""
@mind_object_controller.route('/<object_type>/')
@cached(timeout=300)  # Cache the response for 5 minutes
def index(object_type):

    # Add a log message at the start
    current_app.logger.info(f"Accessing mind object index for {object_type} - not from cache")

    # expecting the object_type to be in lowercase
    # so lets Convert to lowercase for consistency
    object_type = object_type.lower()

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
            "mindObjectType": object_type,
        })
    
    # Pass both the data and the object type
    template = render_template('navigation/index.html', 
                          cards=formatted_cards,
                          objectType=object_type,
                          mindObjectType=object_type,  # Fix this to pass the actual type
                          titleHeader=title_header, 
                          titleSubHeader=title_subheader)
    response = make_response(template)
    
    return response

"""<-----Method Docstring
Retrieve and format data for a specified object type.
This function fetches all objects of the specified type, converts them 
into a list of dictionaries, and formats the data for card display.
Args:
    object_type (str): The type of object to retrieve. Must be a valid 
                        key in the OBJECT_TYPES dictionary.
Returns:
    Response: A Flask JSON response containing either:
                - A list of formatted card dictionaries if the object type is valid.
                - An error message with a 404 status code if the object type is invalid.
Raises:
    KeyError: If the object_type is not found in the OBJECT_TYPES dictionary.
Example:
    >>> response = get_data("example_type")
    >>> response.json
    [
        {
            "id": 1,
            "title": "Example Topic",
            "content": "Description of the topic",
            "subtopic": "Example Subtopic",
            "subtopicDesc": "Description of the subtopic",
            "tag": "example_tag"
        },
        ...
    ]
"""
@mind_object_controller.route('/<object_type>/data')
def get_data(object_type):
    
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

"""<-----Method Docstring
Handles the creation of a new tale in the database.
Args:
    object_type (str): The type of the object for which the tale is being created.
Returns:
    Response: A Flask JSON response containing the result of the operation.
                - On success: Returns a JSON object with success status, message, 
                the ID of the newly created tale, and the tale data (HTTP 201).
                - On failure: Returns a JSON object with an error message and 
                appropriate HTTP status code.
Raises:
    Exception: If an unexpected error occurs during the process.
Process:
    1. Logs the incoming request for debugging purposes.
    2. Validates that the request contains JSON data.
    3. Checks for the presence of required fields in the JSON payload.
    4. Connects to the database and starts a transaction.
    5. Inserts the tale data into the database.
    6. Commits the transaction and returns the ID of the newly created tale.
    7. Handles database errors, including schema issues and duplicate entries.
    8. Rolls back the transaction and logs errors if any issues occur.
    9. Closes the database connection after the operation.
Notes:
    - The function expects the following fields in the JSON payload:
        'mindObjectTypeId', 'talltale'.
    - Optional fields include 'topicTitle', 'date', and 'location'.
    - If 'date' is not provided, the current UTC timestamp is used.
    - Uses parameterized queries to prevent SQL injection.
"""
@mind_object_controller.route('/<object_type>/addTale', methods=['POST'])
def create_tale(object_type):
    
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

"""<-----Method Docstring
Retrieve and return a list of all routes defined in the `mind_object_controller`.
This function iterates through the URL map of the `mind_object_controller` to extract
details about each route, including its endpoint, allowed HTTP methods, and the route path.
The collected route information is returned as a JSON response.
Returns:
    flask.Response: A JSON response containing a list of dictionaries, where each dictionary
    represents a route with the following keys:
        - "endpoint" (str): The name of the endpoint associated with the route.
        - "methods" (list): A list of HTTP methods allowed for the route.
        - "route" (str): The URL pattern of the route.
"""
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