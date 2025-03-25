"""Video creation endpoint."""
import logging
import threading
import uuid

from app.config import Config
from app.utils.util_rate_limit import rate_limiter
from app.utils.util_video import process_video
from flask import Blueprint, jsonify, request

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Importing creation blueprint")
creation_bp = Blueprint("creation", __name__)

# Define video_status and status_lock
video_status = {}
status_lock = threading.Lock()


@creation_bp.route("/creation", methods=["POST", "GET"])
def create_video():
    """
    Create a video from the provided JSON configuration.
    """
    # Handle GET request for endpoint info
    if request.method == "GET":
        return jsonify({
            "endpoint": "/creation",
            "method": "POST",
            "parameters": {
                "segments": "list, required, 1-20 items",
                "zoom_pan": "bool, optional, default False",
                "fade_effect": "str, optional, default 'fade'",
                "audiogram": "dict, optional",
                "watermark": "dict, optional",
                "background_music": "str, optional",
                "resolution": "str, optional, default '1920x1080'",
                "thumbnail": "bool, optional, default False",
                "audio_enhancement": "dict, optional",
                "dynamic_text": "dict, optional",
                "template": "str, optional",
                "social_preset": "str, optional",
                "use_local_files": "bool, optional, default False",
                "intro_music": "str, optional",
                "outro_music": "str, optional",
                "audio_filters": "dict, optional",
                "segment_audio_effects": "list, optional",
            },
            "example": {
                "body": {
                    "segments": [
                        {
                            "imageUrl": "https://example.com/image1.png",
                            "audioUrl": "https://example.com/audio1.mp3",
                            "volume": 0.8
                        }
                    ],
                    "zoom_pan": True,
                    "fade_effect": "wipeleft",
                    "resolution": "1280x720"
                }
            }
        }), 200

    # Check API key for POST requests
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return jsonify({
            "error": "Unauthorized",
            "message": "API key required"
        }), 401

    # Check rate limit and credits
    allowed, error = rate_limiter.check_rate_limit(api_key)
    if not allowed:
        return jsonify({
            "error": "Rate limit exceeded",
            "message": error
        }), 429

    allowed, error = rate_limiter.check_credits(api_key)
    if not allowed:
        return jsonify({
            "error": "Credit limit reached",
            "message": error
        }), 403

    # Check content type
    if request.content_type != "application/json":
        return jsonify({
            "error": "Unsupported Media Type",
            "message": "Content-Type must be application/json"
        }), 415

    # Parse request data
    data = request.get_json()
    if not data or "body" not in data:
        return jsonify({
            "error": "Invalid JSON format",
            "message": "Missing required field: body"
        }), 400

    # Generate a unique video ID
    video_id = str(uuid.uuid4())

    # Extract parameters from request body with defaults
    body = data["body"]
    segments = body.get("segments", [])
    zoom_pan = body.get("zoom_pan", False)
    fade_effect = body.get("fade_effect", "fade")
    audiogram = body.get("audiogram")
    watermark = body.get("watermark")
    background_music = body.get("background_music")
    resolution = body.get("resolution", "1920x1080")
    thumbnail = body.get("thumbnail", False)
    audio_enhancement = body.get("audio_enhancement")
    dynamic_text = body.get("dynamic_text")
    template = body.get("template")
    use_local_files = body.get("use_local_files", False)
    intro_music = body.get("intro_music")
    outro_music = body.get("outro_music")
    audio_filters = body.get("audio_filters")
    segment_audio_effects = body.get("segment_audio_effects")

    # Validate segments
    if not segments or not isinstance(segments, list):
        return jsonify({
            "error": "Invalid segments",
            "message": "Segments must be a non-empty list"
        }), 400

    if len(segments) > 20:
        return jsonify({
            "error": "Too many segments",
            "message": "Maximum 20 segments allowed"
        }), 400

    # Initialize video status
    with status_lock:
        video_status[video_id] = "Processing"

    # Start video processing in a separate thread
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
            video_status,
            status_lock,
            intro_music,
            outro_music,
            audio_filters,
            segment_audio_effects,
        ),
    )
    thread.daemon = True
    thread.start()

    # Consume a credit
    rate_limiter.use_credit(api_key)

    # Get credit information
    credit_info = Config.API_KEYS.get(api_key, {})
    credits_used = credit_info.get('credits_used', 0)
    credits_total = 60 if credit_info.get('plan', '').lower() == 'starter' else 10  # Default to free tier
    credits_remaining = credits_total - credits_used

    return jsonify({
        'message': 'Video processing started',
        'video_id': video_id,
        'status': 'Processing',
        'credits': {
            'plan': credit_info.get('plan', 'Free').title(),
            'credits_used': credits_used,
            'credits_remaining': credits_remaining,
            'credits_total': credits_total,
            'credits_reset': credit_info.get('credits_reset')
        }
    }), 202


@creation_bp.route("/api/create_video_with_audio_enhancement", methods=["POST", "GET"])
def create_video_with_audio_enhancement():
    """Create a video with audio enhancement."""
    logger.debug("test_create_video_with_audio_enhancement route called")
    if request.method == "GET" and "info" in request.args:
        return jsonify({
            "parameters": {
                # Parameters specific to this route
            },
            "returns": {"message": "str, test message"},
        }), 200
    return jsonify({"message": "Test create_video_with_audio_enhancement route"}), 200
