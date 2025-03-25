from flask import Flask
from .routes import routes
from .config import DevelopmentConfig  # Import the desired configuration class
import logging

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__, template_folder=config_class.TEMPLATES_DIR)  # Set template_folder
    app.config.from_object(config_class)

    # Set up logging based on configuration
    logging.basicConfig(level=getattr(logging, app.config['LOG_LEVEL']))
    logger = logging.getLogger(__name__)

    app.register_blueprint(routes)

    @app.context_processor
    def inject_api_base_url():
        return {'api_base_url': app.config['API_BASE_URL']}  # Inject API_BASE_URL into templates

    return app
    return app

# This file can be empty or contain initialization code for the app package
# ...existing code...

# This file can be empty or contain initialization code for the app package
# ...existing code...