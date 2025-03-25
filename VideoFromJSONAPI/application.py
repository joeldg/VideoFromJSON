import logging
import os
import shutil
import uuid
from datetime import datetime, timedelta

from app.config import Config
from app.endpoints import allroutes
from app.utils import *
from flask import Flask, jsonify, request, url_for

#  from werkzeug.debug import DebuggedApplication

logger = logging.getLogger(__name__)
logger.debug("Importing application.py")

logger.setLevel("DEBUG")
logging.basicConfig(level=Config.LOG_LEVEL)

logger.debug("Creating Flask app instance")
app = Flask(__name__)

app.config.from_object(Config)
app.debug = Config.DEBUG
logger.debug(f"Flask app configured with debug mode: {Config.DEBUG}")

# Request ID middleware
@app.before_request
def before_request():
    if Config.ENABLE_REQUEST_ID:
        request_id = request.headers.get(Config.REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.request_id = request_id
        logger.info(
            f"Request started: {request_id} - {request.method} {request.path}"
        )

@app.after_request
def after_request(response):
    if Config.ENABLE_REQUEST_ID:
        request_id = getattr(request, 'request_id', None)
        if request_id:
            logger.info(
                f"Request completed: {request_id} - Status: {response.status_code}"
            )
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not found", "message": str(error)}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error", "message": str(error)}), 500

@app.errorhandler(400)
def bad_request_error(error):
    return jsonify({"error": "Bad request", "message": str(error)}), 400

@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"error": "Forbidden", "message": str(error)}), 403

# Cleanup function for temporary files
def cleanup_temp_files():
    """Remove temporary files older than TEMP_FILE_CLEANUP_DAYS days"""
    cutoff_date = datetime.now() - timedelta(days=Config.TEMP_FILE_CLEANUP_DAYS)
    temp_dirs = [
        Config.TEMP_VIDEO_DIR,
        "temp/temp_images",
        "temp/temp_audios"
    ]
    
    for temp_dir in temp_dirs:
        if not os.path.exists(temp_dir):
            continue
            
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime < cutoff_date:
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filepath}")
            except Exception as e:
                logger.error(f"Error cleaning up {filepath}: {str(e)}")

app.register_blueprint(allroutes, url_prefix="/api")

directories = [
    "static/videos",
    "templates",
    "temp/temp_videos",
    "temp/temp_images",
    "temp/temp_audios",
    Config.TEMP_VIDEO_DIR,
    Config.UPLOADS_DIR,
]
for directory in directories:
    os.makedirs(directory, exist_ok=True)


def runme():
    logger.debug("Running application on port 5000")
    # Run cleanup before starting the server
    cleanup_temp_files()
    app.run(host="0.0.0.0", port=5000)


app_instance = app
logger.debug("app_instance created successfully")
application = app_instance  # Export the Flask app as 'application'
# TODO remove when no longer needed (and import above.)
# application = DebuggedApplication(application, evalex=True)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@application.route("/site-map")
def site_map():
    links = []
    for rule in application.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return links


if __name__ == "__main__":
    logger.debug("Running application")
    runme()
