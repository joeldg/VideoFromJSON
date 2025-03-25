from flask import Blueprint, request, jsonify
import logging
import os
from werkzeug.utils import secure_filename
from app.config import Config
from app.utils.util_auth import validate_api_key
from app.utils.util_auth import is_valid_directory_name

logger = logging.getLogger(__name__)  # Ensure logger is correctly configured

upload_bp = Blueprint("upload", __name__)


# Upload Video
@upload_bp.route("upload_video/<category>", methods=["POST", "GET"])
def upload_video(category):
    logger.debug("upload_video route called")
    if request.method == "GET" and "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {
                        "category": "str, required, type of video upload (pre_roll, post_roll, segment)",
                        "file": "file, required",
                    },
                    "returns": {
                        "status": "str, 'Video uploaded'",
                        "file_path": "str, path to the uploaded video",
                    },
                }
            ),
            200,
        )
    if not validate_api_key(request):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if not is_valid_directory_name(category):
        logger.error(f"Invalid category name: {category}")
        return jsonify({"error": "Invalid category name"}), 400

    if "file" not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    directory_path = os.path.join(Config.UPLOADS_DIR, "video", category)
    if not os.path.exists(directory_path):
        logger.debug(f"Directory does not exist. Creating: {directory_path}")
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
    else:
        logger.debug(f"Directory already exists: {directory_path}")

    file_path = os.path.join(directory_path, secure_filename(file.filename))
    logger.debug(f"Saving file to: {file_path}")
    file.save(file_path)
    logger.info(f"Video uploaded successfully: {file_path}")
    return jsonify({"status": "Video uploaded", "file_path": file_path}), 200


# Upload Audio
@upload_bp.route("upload_audio/<category>", methods=["POST", "GET"])
def upload_audio(category):
    logger.debug("upload_audio route called")
    if request.method == "GET" and "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {
                        "category": "str, required, type of audio upload (main_audio, background_music, sound_effects, intro, outtro, segment)",
                        "file": "file, required",
                    },
                    "returns": {
                        "status": "str, 'Audio uploaded'",
                        "file_path": "str, path to the uploaded audio",
                    },
                }
            ),
            200,
        )
    if not validate_api_key(request):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if not is_valid_directory_name(category):
        logger.error(f"Invalid category name: {category}")
        return jsonify({"error": "Invalid category name"}), 400

    if "file" not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    directory_path = os.path.join(Config.UPLOADS_DIR, "audio", category)
    if not os.path.exists(directory_path):
        logger.debug(f"Directory does not exist. Creating: {directory_path}")
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")
    else:
        logger.debug(f"Directory already exists: {directory_path}")

    file_path = os.path.join(directory_path, secure_filename(file.filename))
    logger.debug(f"Saving file to: {file_path}")
    file.save(file_path)
    logger.info(f"Audio uploaded successfully: {file_path}")
    return jsonify({"status": "Audio uploaded", "file_path": file_path}), 200


# Upload Image
@upload_bp.route("upload_image/<category>", methods=["POST", "GET"])
def upload_image(category):
    logger.error("upload_image route called")
    if request.method == "GET" and "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {
                        "category": "str, required, type of image upload (segment, watermark, thumbnail)",
                        "file": "file, required",
                    },
                    "returns": {
                        "status": "str, 'Image uploaded'",
                        "file_path": "str, path to the uploaded image",
                    },
                }
            ),
            200,
        )
    if not validate_api_key(request):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if not is_valid_directory_name(category):
        logger.error(f"Invalid category name: {category}")
        return jsonify({"error": "Invalid category name"}), 400

    if "file" not in request.files:
        logger.error("No file part in the request")
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400

    directory_path = os.path.join(Config.UPLOADS_DIR, "image", category)
    if not os.path.exists(directory_path):
        logger.error(f"Directory does not exist. Creating: {directory_path}")
        os.makedirs(directory_path, exist_ok=True)
        logger.error(f"Created directory: {directory_path}")
    else:
        logger.error(f"Directory already exists: {directory_path}")

    file_path = os.path.join(directory_path, secure_filename(file.filename))
    logger.error(f"Saving file to: {file_path}")
    file.save(file_path)
    logger.error(f"Image uploaded successfully: {file_path}")
    return jsonify({"status": "Image uploaded", "file_path": file_path}), 200
