"""
Shared constants for the application
"""

# Dictionary mapping object types to their model classes
# Import models here to avoid circular imports in other files
from models.thought import Thought
from models.passion import Passion
from models.delusion import Delusion
from models.interest import Interest
from models.funny import Funny
from models.project import Project  # Assuming Projects is a model class
from models.tale import Tale  # Assuming Tale is a model class

MIND_OBJECT_TYPES = {
    'thoughts': Thought,
    'passions': Passion,
    'delusions': Delusion,
    'interests': Interest,
    'tale': Tale,  # Assuming Tale is a model class
    'funnies': Funny,
    'projects': Project,  # Assuming projects are similar to passions
}

# Get just the keys as a list for validation
VALID_MIND_OBJECT_TYPES = list(MIND_OBJECT_TYPES.keys())

# Title configurations for each type
TITLE_CONFIG = {
    'thoughts': {
        'header': "Thoughts",
        'subheader': "Try and keep up with the randomness of my thoughts."
    },
    'passions': {
        'header': "Passions",
        'subheader': "Things I'm most passionate about and enjoy doing."
    },
    'delusions': {
        'header': "Delusions",
        'subheader': "Wild ideas and concepts that may or may not be true."
    },
    'interests': {
        'header': "Interests",
        'subheader': "Topics and subjects that catch my attention sometimes."
    },
    'funnies': {
        'header': "Funnies",
        'subheader': "Just a little help to get us all through the day."
    },
    'projects': {
        'header': "Projects",
        'subheader': "I deem these to be a worthy investment of my time."
    },
    'tales': {
        'header': "Tales",
        'subheader': "Tales tales, some short some tall some really tall."
    }
}