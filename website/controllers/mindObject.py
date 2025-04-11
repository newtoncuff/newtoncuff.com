from flask import Blueprint, render_template, jsonify, request
from models.thought import Thought
from models.passion import Passion
from models.delusion import Delusion
from models.interest import Interest

# Create a blueprint with dynamic URL prefix
mind_object_controller = Blueprint('mind_object', __name__)

# Dictionary mapping object types to their model classes
OBJECT_TYPES = {
    'thoughts': Thought,
    'passions': Passion,
    'delusions': Delusion,
    'interests': Interest
}

# Title configurations for each type
TITLE_CONFIG = {
    'thoughts': {
        'header': "Thoughts",
        'subheader': "Try and keep up with the random thoughts that invade my head and lead to the randomness that ensues."
    },
    'passions': {
        'header': "Passions",
        'subheader': "Things I'm passionate about and enjoy doing."
    },
    'delusions': {
        'header': "Delusions",
        'subheader': "Wild ideas and concepts that may or may not be realistic."
    },
    'interests': {
        'header': "Interests",
        'subheader': "Topics and subjects that catch my attention."
    }
}

@mind_object_controller.route('/<object_type>/')
def index(object_type):
    """Render the index page for the specified object type"""
    if object_type not in OBJECT_TYPES:
        return "Invalid object type", 404
    
    # Get title configuration for this object type
    title_config = TITLE_CONFIG.get(object_type, {})
    title_header = title_config.get('header', object_type.capitalize())
    title_subheader = title_config.get('subheader', "")
    
    # Render template with dynamic title and content
    return render_template('navigation/index.html', 
                          mindObjectType=title_header,
                          titleHeader=title_header, 
                          titleSubHeader=title_subheader, 
                          content=f"This is the content for the {title_header} page")

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