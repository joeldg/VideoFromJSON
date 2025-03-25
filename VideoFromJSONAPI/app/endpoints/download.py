from flask import send_from_directory, Blueprint, request, abort, current_app
from app.utils.util_auth import validate_api_key
import logging
from werkzeug.utils import secure_filename
import os
from flask import jsonify

logger = logging.getLogger(__name__)  # Ensure logger is correctly configured

download_bp = Blueprint("download", __name__)


@download_bp.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    if "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {
                        "filename": "str, required, name of the file to download"
                    },
                    "returns": {
                        "file": "binary, the requested file",
                        "error": "str, error message if file not found",
                    },
                }
            ),
            200,
        )
    safe_filename = secure_filename(filename)
    file_path = os.path.join("static/videos", safe_filename)
    if os.path.isfile(file_path):
        logger.info(f"Serving file: {safe_filename}")
        return send_from_directory("static/videos", safe_filename, as_attachment=True)
    else:
        logger.error(f"File not found: {safe_filename}")
        return jsonify({"error": "File not found"}), 404


@download_bp.route("/api/download/<video_filename>", methods=["GET"])
def download_video(video_filename):
    logger.debug(f"Download request for video: {video_filename}")
    videos_dir = os.path.join(current_app.root_path, "static/videos")
    file_path = os.path.join(videos_dir, video_filename)

    if os.path.exists(file_path):
        logger.debug(f"Serving video file: {file_path}")
        return send_from_directory(
            directory=videos_dir, filename=video_filename, as_attachment=False
        )
    else:
        logger.error(f"Video file not found: {file_path}")
        abort(404, description="Video file not found")
