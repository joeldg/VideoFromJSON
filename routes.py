from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    render_template,
)
import threading
import os
import logging
from werkzeug.utils import secure_filename
from config import (
    API_KEY,
    pre_roll_video_path,
    post_roll_video_path,
    UPLOADS_DIR,
    ALLOWED_FADE_EFFECTS,
    SOCIAL_MEDIA_PRESETS,
)
from utils import (
    allowed_api_key,
    is_valid_directory_name,
    get_api_key,
    process_video,
    remove_temp_files,
    # ...other utility functions...
)

logger = logging.getLogger(__name__)

routes = Blueprint("routes", __name__)

video_status = {}
status_lock = threading.Lock()


@routes.route("/api/upload_image/<directory>", methods=["POST"])
def upload_image(directory):
    api_key = get_api_key(request)
    if not allowed_api_key(api_key):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if not is_valid_directory_name(directory):
        return jsonify({"error": "Invalid directory name"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    directory_path = os.path.join(UPLOADS_DIR, directory)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, secure_filename(file.filename))
    file.save(file_path)
    return jsonify({"status": "Image uploaded", "file_path": file_path}), 200


@routes.route("/api/creation", methods=["POST"])
def create_video_route():
    api_key = get_api_key(request)
    if not allowed_api_key(api_key):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        if data is None:
            raise ValueError("No JSON data received")

        segments = data.get("segments", [])
        zoom_pan = data.get("zoom_pan", False)
        fade_effect = data.get("fade_effect", "fade")
        audiogram = data.get("audiogram", {})
        watermark = data.get("watermark", {})
        background_music = data.get("background_music", None)
        resolution = data.get("resolution", "1920x1080")
        thumbnail = data.get("thumbnail", False)
        audio_enhancement = data.get("audio_enhancement", {})
        dynamic_text = data.get("dynamic_text", {})
        template = data.get("template", None)
        social_preset = data.get("social_preset", None)
        use_local_files = data.get("use_local_files", False)
        logger.debug(f"Received data: {data}")
    except Exception as e:
        logger.error(f"Invalid JSON format: {e}")
        return jsonify({"error": "Invalid JSON format"}), 400

    if not segments or not (1 <= len(segments) <= 20):
        logger.error("Number of segments must be between 1 and 20")
        return jsonify({"error": "Number of segments must be between 1 and 20"}), 400

    if fade_effect not in ALLOWED_FADE_EFFECTS:
        logger.error(f"Invalid fade effect: {fade_effect}")
        return jsonify({"error": "Invalid fade effect"}), 400

    if social_preset:
        preset = SOCIAL_MEDIA_PRESETS.get(social_preset)
        if preset:
            resolution = preset.get("resolution", resolution)
        else:
            logger.error(f"Invalid social media preset: {social_preset}")
            return jsonify({"error": "Invalid social media preset"}), 400

    video_id = str(uuid.uuid4())
    logger.info(f"Starting video processing with ID: {video_id}")
    with status_lock:
        video_status[video_id] = "Processing"

    thread = threading.Thread(
        target=process_video,
        args=(
            video_id,
            segments,
            zoom_pan,
            fade_effect,
            audiogram,
            watermark,
            background_music,
            resolution,
            thumbnail,
            audio_enhancement,
            dynamic_text,
            template,
            use_local_files,
        ),
    )
    thread.start()

    return jsonify({"status": "Processing started", "video_id": video_id}), 200


@routes.route("/api/status/<video_id>", methods=["GET"])
def get_video_status_route(video_id):
    status = video_status.get(video_id, "Unknown video ID")
    return jsonify({"video_id": video_id, "status": status})


@routes.route("/api/videos", methods=["GET"])
def list_videos():
    videos = os.listdir("static/videos")
    return jsonify({"videos": videos})


@routes.route("/api/videos/<video_id>", methods=["DELETE"])
def delete_video(video_id):
    video_path = os.path.join("static/videos", f"{video_id}.mp4")
    if os.path.exists(video_path):
        os.remove(video_path)
        return jsonify({"status": "Video deleted"}), 200
    else:
        return jsonify({"error": "Video not found"}), 404


@routes.route("/api/pre_roll", methods=["POST"])
def upload_pre_roll():
    api_key = get_api_key(request)
    if not allowed_api_key(api_key):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file:
        file.save(pre_roll_video_path)
        return jsonify({"status": "Pre-roll video uploaded"}), 200


@routes.route("/api/post_roll", methods=["POST"])
def upload_post_roll():
    api_key = get_api_key(request)
    if not allowed_api_key(api_key):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    if file:
        file.save(post_roll_video_path)
        return jsonify({"status": "Post-roll video uploaded"}), 200


@routes.route("/download/<filename>", methods=["GET"])
def download_filename(filename):
    safe_filename = secure_filename(filename)
    file_path = os.path.join("static/videos", safe_filename)
    if os.path.isfile(file_path):
        logger.info(f"Serving file: {safe_filename}")
        return send_from_directory("static/videos", safe_filename, as_attachment=True)
    else:
        logger.error(f"File not found: {safe_filename}")
        return jsonify({"error": "File not found"}), 404


@routes.route("/web")
def web_index():
    logger.debug("Rendering index.html")
    return render_template("index.html")


@routes.route("/web/upload_image")
def web_upload_image():
    logger.debug("Rendering upload_image.html")
    return render_template("upload_image.html")


@routes.route("/web/creation")
def web_creation():
    logger.debug("Rendering creation.html")
    return render_template("creation.html")


@routes.route("/web/status")
def web_status():
    logger.debug("Rendering status.html")
    return render_template("status.html")


@routes.route("/web/videos")
def web_videos():
    logger.debug("Rendering videos.html")
    return render_template("videos.html")


@routes.route("/web/pre_roll")
def web_pre_roll():
    logger.debug("Rendering pre_roll.html")
    return render_template("pre_roll.html")


@routes.route("/web/post_roll")
def web_post_roll():
    logger.debug("Rendering post_roll.html")
    return render_template("post_roll.html")


@routes.route("/health", methods=["GET"])
def health_check():
    return "GOOD"


@routes.route("/")
def default_route():
    return "<html><body><b>Hi!</b></body></html>"
