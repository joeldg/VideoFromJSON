"""VideoFromJSON app package."""
from app.config import Config
from app.endpoints import api_keys, creation
from flask import Flask
from flask_cors import CORS


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(creation.bp)
    app.register_blueprint(api_keys.api_keys_bp)
    
    return app
