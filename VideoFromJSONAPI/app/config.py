import logging
import os
import shutil
from datetime import datetime, timedelta
from typing import Any, Dict

import dotenv

# Load environment variables from .env file if not already set
dotenv.load_dotenv()


class Config:
    # Configuration
    API_KEY = os.getenv("API_KEY", "your_api_key_here")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "47235106-227579315fdd6311b7e7cbb7b")
    SUCCESS_WEBHOOK_URL = "https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b"
    ERROR_WEBHOOK_URL = "https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b"
    LOG_LEVEL = logging.DEBUG
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    REQUEST_ID_HEADER = "X-Request-ID"
    ENABLE_REQUEST_ID = True
    TEMP_FILE_CLEANUP_DAYS = 7  # Number of days to keep temporary files

    PRE_ROLL_VIDEO_PATH = "static/videos/pre_roll.mp4"
    POST_ROLL_VIDEO_PATH = "static/videos/post_roll.mp4"

    BACKGROUND_MUSIC_DIR = os.path.join("static", "testfiles", "background_music")
    SOUND_EFFECTS_DIR = os.path.join("static", "testfiles", "sound_effects")

    TEMP_VIDEO_DIR = "temp/temp_videos"  # Directory to store temporary video files
    TEMP_VIDEO_PATH = os.path.join(TEMP_VIDEO_DIR, "temp_video.mp4")

    # Ensure the temporary directory exists
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

    ALLOWED_FADE_EFFECTS = {
        "fade",
        "wipeleft",
        "wiperight",
        "wipeup",
        "wipedown",
        "slideleft",
        "slideright",
        "slideup",
        "slidedown",
        "circlecrop",
        "rectcrop",
        "distance",
        "fadeblack",
        "fadewhite",
        "radial",
        "smoothleft",
        "smoothright",
        "smoothup",
        "smoothdown",
        "circleopen",
        "circleclose",
        "vertopen",
        "vertclose",
        "horzopen",
        "horzclose",
        "dissolve",
        "pixelize",
        "diagtl",
        "diagtr",
        "diagbl",
        "diagbr",
        "hlslice",
        "hrslice",
        "vuslice",
        "vdslice",
        "hblur",
        "fadegrays",
        "wipetl",
        "wipetr",
        "wipebl",
        "wipebr",
        "squeezeh",
        "squeezev",
        # ...add any missing effects here...
    }

    TEMPLATES_DIR = os.path.join(
        os.path.dirname(__file__), "templates"
    )  # Correctly specify the templates directory

    SOCIAL_MEDIA_PRESETS = {
        "instagram": {
            "resolution": "1080x1080",
            "duration_limit": 60,
            "aspect_ratio": "1:1",
            "max_file_size": 100 * 1024 * 1024,  # 100MB
            "supported_formats": ["mp4"],
            "min_duration": 3,
            "max_audio_duration": 60
        },
        "tiktok": {
            "resolution": "1080x1920",
            "duration_limit": 60,
            "aspect_ratio": "9:16",
            "max_file_size": 50 * 1024 * 1024,  # 50MB
            "supported_formats": ["mp4"],
            "min_duration": 3,
            "max_audio_duration": 60
        },
        "facebook": {
            "resolution": "1920x1080",
            "duration_limit": 600,  # 10 minutes
            "aspect_ratio": "16:9",
            "max_file_size": 4 * 1024 * 1024 * 1024,  # 4GB
            "supported_formats": ["mp4"],
            "min_duration": 1,
            "max_audio_duration": 600
        },
        "youtube": {
            "resolution": "1920x1080",
            "duration_limit": 43200,  # 12 hours
            "aspect_ratio": "16:9",
            "max_file_size": 256 * 1024 * 1024 * 1024,  # 256GB
            "supported_formats": ["mp4"],
            "min_duration": 1,
            "max_audio_duration": 43200
        }
    }

    UPLOADS_DIR = "uploads"

    # Audio processing defaults
    DEFAULT_AUDIO_FADE_DURATION = 2.0  # seconds

    # Ensure background_music and sound_effects directories exist
    os.makedirs(BACKGROUND_MUSIC_DIR, exist_ok=True)
    os.makedirs(SOUND_EFFECTS_DIR, exist_ok=True)

    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # API Plans Configuration
    API_PLANS = {
        "free": {
            "name": "Free",
            "price": 0,
            "credits": 10,
            "rate_limit": 1,  # requests per minute
            "features": ["basic_video_creation", "720p_resolution"]
        },
        "starter": {
            "name": "Starter",
            "price": 19.99,
            "credits": 60,
            "rate_limit": 1,
            "features": ["basic_video_creation", "1080p_resolution", "watermark"]
        },
        "creator": {
            "name": "Creator",
            "price": 39.99,
            "credits": 150,
            "rate_limit": 1,
            "features": ["basic_video_creation", "1080p_resolution", "watermark", "custom_fonts"]
        },
        "pro": {
            "name": "Pro",
            "price": 79.99,
            "credits": 500,
            "rate_limit": 1,
            "features": ["basic_video_creation", "4k_resolution", "watermark", "custom_fonts", "priority_support"]
        }
    }

    # API Key Configuration
    API_KEYS: Dict[str, Dict[str, Any]] = {
        # Example local API key
        "your-api-key-here": {
            "name": "Development Key",
            "plan": "pro",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=365)).isoformat(),
            "is_active": True,
            "credits_used": 0,
            "credits_reset": (datetime.now() + timedelta(days=30)).isoformat(),
            "last_request": None
        }
    }
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
    
    # Supabase Table Names
    SUPABASE_API_KEYS_TABLE = "api_keys"
    
    # API Key Settings
    API_KEY_HEADER = "X-API-Key"
    API_KEY_LENGTH = 32
    API_KEY_EXPIRY_DAYS = 365  # Default expiry period
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 1  # requests per minute
    RATE_LIMIT_PERIOD = 60  # seconds
    
    # Video Processing
    MAX_SEGMENTS = 20
    MIN_SEGMENTS = 1
    DEFAULT_RESOLUTION = "1920x1080"
    DEFAULT_FPS = 30

    logging.debug("Config loaded successfully")
