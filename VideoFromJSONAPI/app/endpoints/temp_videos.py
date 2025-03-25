from flask import send_from_directory, request, jsonify, Blueprint
import os
from app.config import Config

temp_videos_bp = Blueprint("temp_videos", __name__)


@temp_videos_bp.route("temp_videos/<filename>", methods=["GET"])
def serve_temp_video(filename):
    if "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {"filename": "str, required, name of the video file"},
                    "returns": {"file": "binary, video file content"},
                }
            ),
            200,
        )
    temp_video_directory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), Config.TEMP_VIDEO_DIR
    )
    return send_from_directory(temp_video_directory, filename)
