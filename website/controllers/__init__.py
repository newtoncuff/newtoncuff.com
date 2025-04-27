# Register all blueprints here
def register_controllers(app):
    from controllers.main import main_controller
    from controllers.mindObject import mind_object_controller
    from controllers.admin import admin_controller
    from controllers.tale import tale_controller
    
    app.register_blueprint(main_controller)
    app.register_blueprint(mind_object_controller)
    app.register_blueprint(admin_controller)
    app.register_blueprint(tale_controller)