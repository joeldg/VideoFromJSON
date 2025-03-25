from flask import (
    jsonify,
    request,
    Blueprint,
    send_from_directory,
    # safe_join,  # Removed from here
)
from werkzeug.utils import safe_join  # Added safe_join from werkzeug.utils
from app.utils import *
import os
from app.endpoints.creation import video_status  # Import video_status
import logging

logger = logging.getLogger(__name__)  # Configure logger

status_bp = Blueprint("status", __name__)


@status_bp.route("status/<video_id>", methods=["GET"])
def get_video_status_route(video_id):
    if "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {
                        "video_id": "str, required, unique identifier of the video"
                    },
                    "returns": {
                        "video_id": "str, unique identifier",
                        "status": "str, status of the video processing",
                    },
                }
            ),
            200,
        )
    logger.debug("get_video_status_route called")  # Add this line for debugging
    status = video_status.get(video_id, "Unknown video ID")
    return jsonify({"video_id": video_id, "status": status}), 200


@status_bp.route("videos", methods=["GET"])
def list_videos():
    if "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {},
                    "returns": {"videos": "list of str, names of available videos"},
                }
            ),
            200,
        )
    videos = os.listdir("static/videos")
    return jsonify({"videos": videos})


@status_bp.route("videos/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    if request.method == "GET" and "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {
                        "video_id": "str, required, unique identifier of the video"
                    },
                    "returns": {
                        "status": "str, 'Video deleted'",
                        "error": "str, error message if any",
                    },
                }
            ),
            200,
        )
    video_path = os.path.join("static/videos", f"{video_id}.mp4")
    if os.path.exists(video_path):
        os.remove(video_path)
        return jsonify({"status": "Video deleted"}), 200
    else:
        return jsonify({"error": "Video not found"}), 404


def list_files_recursive(directory, max_depth, current_depth=0):
    files = {}
    if current_depth >= max_depth:
        return files
    for entry in os.scandir(directory):
        if entry.is_file():
            if "background_music" in entry.path:
                files.setdefault("background_music", []).append(
                    entry.path.replace("zstatic/testfiles/background_music/", "")
                )
            elif "sound_effects" in entry.path:
                files.setdefault("sound_effects", []).append(
                    entry.path.replace("sztatic/testfiles/sound_effects/", "")
                )
        elif entry.is_dir():
            nested_files = list_files_recursive(
                entry.path, max_depth, current_depth + 1
            )
            for key, value in nested_files.items():
                files.setdefault(key, []).extend(value)
    return files


@status_bp.route("testfiles", methods=["GET"])
def list_testfiles():
    if "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {},
                    "returns": {
                        "testfiles": {
                            "background_music": "list of str, names of background sound files",
                            "sound_effects": "list of str, names of sound effect files with subdirectories",
                        }
                    },
                }
            ),
            200,
        )
    testfiles = list_files_recursive(
        "/app/static/testfiles", max_depth=3  # Corrected path
    )
    return jsonify({"testfiles": testfiles})


@status_bp.route("testfiles/<path:filename>", methods=["GET"])
def get_testfile(filename):
    testfile_path = safe_join("static/testfiles", filename)
    if os.path.exists(testfile_path) and os.path.isfile(testfile_path):
        return send_from_directory("static/testfiles", filename), 200
    else:
        return jsonify({"error": "Test file not found"}), 404
