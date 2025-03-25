from flask import Blueprint, request, jsonify, current_app
import logging
import os
from werkzeug.utils import secure_filename
from app.utils.util_auth import validate_api_key  # Import validate_api_key directly

logger = logging.getLogger(__name__)  # Configure logger

management_bp = Blueprint("management", __name__)


@management_bp.route("upload_pre_roll", methods=["POST", "GET"])
def upload_pre_roll():
    logger.debug("upload_pre_roll route called")  # Add this line for debugging
    if request.method == "GET" and "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {"file": "file, required"},
                    "returns": {
                        "status": "str, 'Pre-roll video uploaded'",
                        "file_path": "str, path to the uploaded pre-roll video",
                    },
                }
            ),
            200,
        )
    if not validate_api_key(request):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(
        current_app.config["PRE_ROLL_VIDEO_PATH"], secure_filename(file.filename)
    )
    file.save(file_path)
    return jsonify({"status": "Pre-roll video uploaded", "file_path": file_path}), 200


@management_bp.route("upload_post_roll", methods=["POST", "GET"])
def upload_post_roll():
    logger.debug("upload_post_roll route called")  # Add this line for debugging
    if request.method == "GET" and "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {"file": "file, required"},
                    "returns": {
                        "status": "str, 'Post-roll video uploaded'",
                        "file_path": "str, path to the uploaded post-roll video",
                    },
                }
            ),
            200,
        )
    if not validate_api_key(request):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(
        current_app.config["POST_ROLL_VIDEO_PATH"], secure_filename(file.filename)
    )
    file.save(file_path)
    return jsonify({"status": "Post-roll video uploaded", "file_path": file_path}), 200


@management_bp.route("/management", methods=["GET", "POST"])
def manage():
    pass
