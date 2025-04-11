import sys
sys.dont_write_bytecode = True

from flask import Flask, send_from_directory
from database import database_config
from models import db
from controllers import register_controllers

# Define the function to create and configure the app
def create_app():
    # Create a Flask application instance inside the factory function
    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Configure the database URI for SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = database_config.database_connection_uri
    
    # Disable SQLAlchemy's event system for tracking modifications to objects
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize the database with the Flask app
    db.init_app(app)

    # Register controllers (routes, blueprints)
    register_controllers(app)

    # Static file handling (Optional, only needed if you want to customize static serving behavior)
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)

    return app

# Create the app by calling create_app()
app = create_app()

# Run the application only if this file is executed directly
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
