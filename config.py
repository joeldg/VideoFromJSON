import os
import dotenv
import logging

# Load environment variables from .env file if not already set
dotenv.load_dotenv()

# Configuration
API_KEY = os.getenv("API_KEY", "{INSERT API KEY HERE}}")
SUCCESS_WEBHOOK_URL = "https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b"
ERROR_WEBHOOK_URL = "https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b"
LOG_LEVEL = logging.DEBUG

pre_roll_video_path = "static/videos/pre_roll.mp4"
post_roll_video_path = "static/videos/post_roll.mp4"

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
}

TEMPLATES_DIR = "templates"  # Directory to store video templates
SOCIAL_MEDIA_PRESETS = {
    "instagram": {"resolution": "1080x1080", "duration_limit": 60},
    "tiktok": {"resolution": "1080x1920", "duration_limit": 60},
    "youtube": {"resolution": "1920x1080", "duration_limit": None},
    # ...add more presets as needed...
}

UPLOADS_DIR = "uploads"
