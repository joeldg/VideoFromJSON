import json  # Add this import at the top

from flask import (
    Blueprint,
    request,
    jsonify,
    send_from_directory,
    render_template,
)
import threading
import os
import uuid
import logging
from werkzeug.utils import secure_filename
from app.config import Config
from app.utils import *
import random
import requests
from flask import redirect, url_for
from app.config import Config

logger = logging.getLogger(__name__)

routes = Blueprint("routes", __name__)

video_status = {}
status_lock = threading.Lock()

# Ensure temporary directories exist
os.makedirs("temp_images", exist_ok=True)
os.makedirs("temp_audios", exist_ok=True)

pre_roll_video_path = Config.PRE_ROLL_VIDEO_PATH
post_roll_video_path = Config.POST_ROLL_VIDEO_PATH
UPLOADS_DIR = Config.UPLOADS_DIR
ALLOWED_FADE_EFFECTS = Config.ALLOWED_FADE_EFFECTS
SOCIAL_MEDIA_PRESETS = Config.SOCIAL_MEDIA_PRESETS
TEMP_VIDEO_DIR = Config.TEMP_VIDEO_DIR


@routes.route("/api/upload_image/<directory>", methods=["POST"])
def upload_image(directory):
    logger.debug("upload_image route called")  # Add this line for debugging
    if not validate_api_key(request):
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
    logger.info("create_video_route called")  # Add this line for debugging
    logger.info(f"Request Headers: {request.headers}")  # Add this line for debugging
    logger.info(f"Content-Type: {request.content_type}")  # Add this line for debugging
    if not validate_api_key(request):
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    if request.content_type != "application/json":
        logger.error("Unsupported Media Type: Content-Type must be application/json")
        return (
            jsonify(
                {
                    "error": "Unsupported Media Type: Content-Type must be application/json"
                }
            ),
            415,
        )

    try:
        # Log the raw data received
        raw_data = request.get_data(as_text=True)
        logger.debug(f"Raw data received: {raw_data}")

        data = request.get_json()
        if data is None:
            raise ValueError("No JSON data received")

        logger.debug(f"JSON data parsed: {data}")

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

        # New parameters for audio enhancements
        intro_music = data.get("intro_music", None)
        outro_music = data.get("outro_music", None)
        audio_filters = data.get("audio_filters", {})
        segment_audio_effects = data.get("segment_audio_effects", [])

    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        return jsonify({"error": "Invalid JSON format."}), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred."}), 500

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
            video_status,  # Pass video_status
            status_lock,  # Pass status_lock
            intro_music,  # Pass new parameters
            outro_music,
            audio_filters,
            segment_audio_effects,
        ),
    )
    thread.start()

    # Removed the immediate temp_video_path check to allow asynchronous processing

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
    logger.debug("upload_pre_roll route called")  # Add this line for debugging
    if not validate_api_key(request):
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
    logger.debug("upload_post_roll route called")  # Add this line for debugging
    if not validate_api_key(request):
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
    file_path = os.path.join("/static/videos", safe_filename)
    if os.path.isfile(file_path):
        logger.info(f"Serving file: {safe_filename}")
        return send_from_directory("/static/videos", safe_filename, as_attachment=True)
    else:
        logger.error(f"File not found: {safe_filename}")
        return jsonify({"error": "File not found"}), 404


@routes.route("/health", methods=["GET"])
def health_check():
    return "GOOD"


@routes.route("/")
def default_route():
    return "<html><body><b>Hi!</b></body></html>"


@routes.route("/temp_videos/<filename>", methods=["GET"])
def serve_temp_video(filename):
    temp_video_directory = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), TEMP_VIDEO_DIR
    )
    return send_from_directory(temp_video_directory, filename)


# Remove or comment out the generate_random_video route
# @routes.route("/web/generate_random_video", methods=["GET", "POST"])
# def generate_random_video():
#     if request.method == "POST":
#         return jsonify({"error": "POST method not allowed. Please use GET."}), 405
#
#     # ...existing GET request handling code...


def get_random_pixabay_image():
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": "nature",
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": 200,
    }
    response = requests.get(url, params=params)
    data = response.json()
    hits = data.get("hits", [])
    if hits:
        image = random.choice(hits)
        return image["webformatURL"]
    else:
        return "https://picsum.photos/800/600"


def get_random_pixabay_video(max_duration=30):
    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": "intro",
        "video_type": "film",
        "orientation": "horizontal",
        "per_page": 50,
    }
    response = requests.get(url, params=params)
    data = response.json()
    hits = data.get("hits", [])
    videos = [hit for hit in hits if hit["duration"] <= max_duration]
    if videos:
        video = random.choice(videos)
        return video["videos"]["medium"]["url"]
    else:
        return ""


def get_random_sound_effect():
    sound_effects_dir = os.path.join("static", "testfiles", "sound_effects")
    files = os.listdir(sound_effects_dir)
    if files:
        return "/static/testfiles/sound_effects/" + random.choice(files)
    else:
        return ""


def get_random_background_music():
    try:
        music_dir = os.path.join("static", "testfiles", "background_music")
        files = os.listdir(music_dir)
        if files:
            selected_file = random.choice(files)
            return "/static/testfiles/background_music/" + selected_file
        else:
            logger.warning("No background music files available")
            return ""
    except Exception as e:
        logger.error(f"Error in get_random_background_music: {e}")
        return ""


@routes.route("/api/generate_random_data", methods=["GET"])
def generate_random_data_route():
    try:
        random_data = {
            "segments": generate_random_segments(),
            "zoom_pan": generate_random_zoom_pan(),
            "fade_effect": get_random_fade_effect(),
            "audiogram": generate_random_audiogram(),
            "watermark": generate_random_watermark(),
            "background_music": get_random_background_music(),
            "resolution": get_random_resolution(),
            "thumbnail": generate_random_thumbnail(),
            "audio_enhancement": generate_random_audio_enhancement(),
            "dynamic_text": generate_random_dynamic_text(),
            "template": generate_random_template(),
            "social_preset": get_random_social_preset(),
            "use_local_files": generate_random_use_local_files(),
            "audio_filters": generate_random_audio_filters(),
            "segment_audio_effects": generate_random_segment_audio_effects(),
            "intro_music": generate_random_intro_music(),
            "outro_music": generate_random_outro_music(),
        }
        logger.debug(f"Random data generated: {random_data}")
        return jsonify(random_data), 200
    except Exception as e:
        logger.error(f"Error generating random data: {e}")
        return jsonify({"error": "Failed to generate random data"}), 500


def generate_random_segments():
    try:
        segments = []
        num_segments = random.randint(1, 5)
        for _ in range(num_segments):
            segments.append(
                {
                    "imageUrl": get_random_pixabay_image(),
                    "audioUrl": get_random_sound_effect(),
                }
            )
        return segments
    except Exception as e:
        logger.error(f"Error in generate_random_segments: {e}")
        return []


def generate_random_zoom_pan():
    return random.choice([True, False])


def generate_random_audiogram():
    return {"enabled": random.choice([True, False]), "style": get_random_filter()}


def generate_random_watermark():
    return {
        "text": get_random_text(),
        "position": random.choice(
            ["top-left", "top-right", "bottom-left", "bottom-right"]
        ),
    }


def generate_random_thumbnail():
    return random.choice([True, False])


def generate_random_audio_enhancement():
    return {
        "noise_reduction": random.choice([True, False]),
        "equalization": random.choice(["flat", "bass_boost", "treble_boost"]),
    }


def generate_random_dynamic_text():
    return {
        "text": get_random_dynamic_text(),
        "animation": random.choice(["fade", "slide", "none"]),
    }


def generate_random_template():
    return random.choice(["default", "modern", "classic"])


def generate_random_use_local_files():
    return random.choice([True, False])


def generate_random_audio_filters():
    return {
        "bass_boost": random.choice([True, False]),
        "treble_boost": random.choice([True, False]),
        "reverb": random.choice([True, False]),
    }


def generate_random_segment_audio_effects():
    effects = ["echo", "reverb", "distortion", "chorus"]
    return random.sample(effects, k=random.randint(0, len(effects)))


def generate_random_intro_music():
    return get_random_background_music()


def generate_random_outro_music():
    return get_random_background_music()


def get_random_fade_effect():
    return random.choice(list(ALLOWED_FADE_EFFECTS))


def get_random_resolution():
    return random.choice(["1920x1080", "1280x720", "3840x2160"])


def get_random_social_preset():
    return random.choice(list(SOCIAL_MEDIA_PRESETS.keys()))


def get_random_filter():
    # Define available audiogram styles
    return random.choice(["style1", "style2", "style3"])  # Replace with actual styles


def get_random_text():
    texts = ["Sample Text 1", "Sample Text 2", "Sample Text 3"]
    return random.choice(texts)


def get_random_dynamic_text():
    dynamic_texts = ["Dynamic Text 1", "Dynamic Text 2", "Dynamic Text 3"]
    return random.choice(dynamic_texts)
