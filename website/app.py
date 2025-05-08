# This is to prevent python from writing .pyc files to __pycache__ directories
import sys
sys.dont_write_bytecode = True

from flask import Flask, send_from_directory, current_app
from database import database_config
from models import db
from controllers import register_controllers

import base64

"""<-----Method Docstring
Factory function to create and configure a Flask application instance.
This function initializes the Flask app with necessary configurations, 
extensions, and routes. It also sets up the database and Redis configurations.
Returns:
    Flask: A configured Flask application instance.
"""
def create_app():

    # Create a Flask application instance inside the factory function
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Configure the database URI for SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = database_config.database_connection_uri
    
    # Disable SQLAlchemy's event system for tracking modifications to objects
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Use the correct Redis host from Docker Compose
    app.config['REDIS_URL'] = 'redis://redis:6379/0'

    # Initialize extensions
    init_extensions(app)
    
    # Initialize the database with the Flask app
    db.init_app(app)

    # Register controllers (routes, blueprints)
    register_controllers(app)

    # Static file handling (Optional, only needed if you want to customize static serving behavior)
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)

    return app

"""<-----Method Docstring
Initializes the extensions for the Flask application.
This method sets up the database and Redis cache for the given Flask app.
It initializes the database using SQLAlchemy and establishes a connection
to Redis. Logs are generated to indicate the success or failure of the Redis
connection.
Args:
    app (Flask): The Flask application instance to initialize extensions for.
Returns:
    None
"""
def init_extensions(app):
    
    db.init_app(app)
    
    # Initialize Redis
    with app.app_context():
        from redis_cache import init_redis
        redis_components = init_redis(app)
        
        # You can access components like this
        redis_client = redis_components['get_redis']()
        if redis_client:
            app.logger.info("Redis connected successfully")
        else:
            app.logger.warning("Redis connection failed")

# Create the app by calling create_app()
app = create_app()

"""<-----Method Docstring
Encodes the given data into a Base64-encoded string.

Args:
    data (str or bytes): The input data to encode. If a string is provided, 
                            it will be encoded to bytes before Base64 encoding.

Returns:
    str: The Base64-encoded representation of the input data.

Raises:
    TypeError: If the input data is not of type str or bytes.
"""
# Register custom filters
@app.template_filter('b64encode')
def b64encode_filter(data):
    
    if isinstance(data, str):
        return base64.b64encode(data.encode()).decode()
    return base64.b64encode(data).decode()

"""<-----Method Docstring
Logs the headers of a given HTTP response object using the application's logger.

Args:
    response (Response): The HTTP response object whose headers are to be logged.

Returns:
    Response: The same HTTP response object passed as input.
"""
@app.after_request
def log_response_headers(response):
    
    current_app.logger.info(f"Response headers before return: {dict(response.headers)}")
    return response

# Run the application only if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
