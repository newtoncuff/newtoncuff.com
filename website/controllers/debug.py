from flask import Blueprint, jsonify, current_app, make_response

debug_controller = Blueprint('debug', __name__)

@debug_controller.route('/debug/headers')
def test_headers():
    """Test endpoint that always adds headers"""
    # Create a simple response
    response = make_response("Check your browser's network tab for headers")
    
    # Add headers explicitly - these should always appear
    response.headers['X-Test-Header'] = 'This is a test header'
    response.headers['X-Cache-Status'] = 'DEBUG'
    response.headers['X-Cache'] = 'DEBUG'
    response.headers['X-Cache-Hit'] = 'false'
    
    # Log what we're doing
    current_app.logger.info("Debug endpoint: Adding test headers to response")
    current_app.logger.info(f"Headers being set: {dict(response.headers)}")
    
    return response