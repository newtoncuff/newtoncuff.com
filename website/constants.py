"""
Shared constants for the application
"""

# Dictionary mapping object types to their model classes
# Import models here to avoid circular imports in other files
from models.thought import Thought
from models.passion import Passion
from models.delusion import Delusion
from models.interest import Interest

MIND_OBJECT_TYPES = {
    'thoughts': Thought,
    'passions': Passion,
    'delusions': Delusion,
    'interests': Interest
}

# Get just the keys as a list for validation
VALID_MIND_OBJECT_TYPES = list(MIND_OBJECT_TYPES.keys())

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