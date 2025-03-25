"""Common test fixtures and configuration for VideoFromJSONAPI tests."""
import os
import shutil
import tempfile

import pytest
from app.config import Config
from app.endpoints import allroutes
from flask import Flask


@pytest.fixture
def app():
    """Create and configure a new Flask app instance for each test."""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    # Create a temporary directory for test files
    temp_dir = tempfile.mkdtemp()
    app.config['TEMP_VIDEO_DIR'] = os.path.join(temp_dir, 'temp_videos')
    app.config['UPLOADS_DIR'] = os.path.join(temp_dir, 'uploads')
    
    # Create necessary directories
    os.makedirs(app.config['TEMP_VIDEO_DIR'], exist_ok=True)
    os.makedirs(app.config['UPLOADS_DIR'], exist_ok=True)
    
    app.register_blueprint(allroutes, url_prefix="/api")
    
    yield app
    
    # Cleanup temporary directory after tests
    shutil.rmtree(temp_dir)


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner for the Flask app."""
    return app.test_cli_runner()


@pytest.fixture
def sample_video_data():
    """Provide sample video creation data for tests."""
    return {
        "segments": [
            {
                "duration": 5,
                "type": "image",
                "source": "https://example.com/image.jpg",
                "transition": "fade"
            }
        ],
        "background_music": "test_background.mp3",
        "output_format": "mp4"
    }


@pytest.fixture
def mock_pixabay_response():
    """Provide mock Pixabay API response for tests."""
    return {
        "hits": [
            {
                "id": 123,
                "previewURL": "https://example.com/preview.jpg",
                "videos": {
                    "medium": {
                        "url": "https://example.com/video.mp4"
                    }
                }
            }
        ]
    } 