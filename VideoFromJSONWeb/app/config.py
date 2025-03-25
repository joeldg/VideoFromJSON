import logging
import os
import dotenv
import shutil

# Load environment variables from .env file if not already set
dotenv.load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "your_default_secret_key")
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
    PORT = int(os.environ.get("PORT", 5000))  # Added PORT variable
    API_BASE_URL = os.environ.get(
        "API_BASE_URL", "http://localhost"
    )  # Added API_BASE_URL
    # Add other general configuration options here

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

    SOCIAL_MEDIA_PRESETS = {
        "instagram": {"resolution": "1080x1080", "duration_limit": 60},
        "tiktok": {"resolution": "1080x1920", "duration_limit": 60},
        "youtube": {"resolution": "1920x1080", "duration_limit": None},
        # ...add more presets as needed...
    }


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    TEMPLATES_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    )  # Updated to point to the project root 'templates' directory
    # Add development-specific configurations here


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"
    # Add production-specific configurations here

    API_KEY = os.getenv("API_KEY", "your_api_key_here")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "47235106-227579315fdd6311b7e7cbb7b")
    SUCCESS_WEBHOOK_URL = "https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b"
    ERROR_WEBHOOK_URL = "https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b"

    PRE_ROLL_VIDEO_PATH = "static/videos/pre_roll.mp4"
    POST_ROLL_VIDEO_PATH = "static/videos/post_roll.mp4"

    BACKGROUND_MUSIC_DIR = os.path.join("static", "testfiles", "background_music")
    SOUND_EFFECTS_DIR = os.path.join("static", "testfiles", "sound_effects")

    TEMP_VIDEO_DIR = "temp/temp_videos"  # Directory to store temporary video files
    TEMP_VIDEO_PATH = os.path.join(TEMP_VIDEO_DIR, "temp_video.mp4")

    # Ensure the temporary directory exists
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)

    TEMPLATES_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "templates"
    )  # Adjusted to point to the project root's templates

    UPLOADS_DIR = "uploads"

    # Audio processing defaults
    DEFAULT_AUDIO_FADE_DURATION = 2.0  # seconds

    # Ensure background_music and sound_effects directories exist
    os.makedirs(BACKGROUND_MUSIC_DIR, exist_ok=True)
    os.makedirs(SOUND_EFFECTS_DIR, exist_ok=True)

    logging.debug("Config loaded successfully")
