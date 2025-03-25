from flask import jsonify, Blueprint, request
import random
from app.utils import *
import requests
import logging
import os
from dotenv import load_dotenv  # Import load_dotenv to load environment variables

random_data_bp = Blueprint("random_data", __name__)


logger = logging.getLogger(__name__)  # Ensure logger is correctly configured

# Load environment variables from .env file
load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY")  # Get PIXABAY_API_KEY from environment
ALLOWED_FADE_EFFECTS = os.getenv("ALLOWED_FADE_EFFECTS", "fade_in,fade_out").split(
    ","
)  # Get ALLOWED_FADE_EFFECTS from environment with default value
SOCIAL_MEDIA_PRESETS = {
    preset.split(":")[0]: preset.split(":")[1]
    for preset in os.getenv(
        "SOCIAL_MEDIA_PRESETS", "facebook:1080x1080,instagram:1080x1080"
    ).split(",")
}  # Get SOCIAL_MEDIA_PRESETS from environment with default value


@random_data_bp.route("generate_random_data", methods=["GET"])
def generate_random_data_route():
    if "info" in request.args:
        return (
            jsonify(
                {
                    "parameters": {},
                    "returns": {
                        "segments": "list, randomly generated segments",
                        "zoom_pan": "bool, randomly generated",
                        "fade_effect": "str, randomly selected fade effect",
                        "audiogram": "dict, randomly generated audiogram settings",
                        "watermark": "dict, randomly generated watermark settings",
                        "background_music": "str, path to background music",
                        "resolution": "str, randomly selected resolution",
                        "thumbnail": "bool, randomly selected",
                        "audio_enhancement": "dict, randomly generated audio enhancements",
                        "dynamic_text": "dict, randomly generated dynamic text settings",
                        "template": "str, randomly selected template",
                        "social_preset": "str, randomly selected social media preset",
                        "use_local_files": "bool, randomly selected",
                        "audio_filters": "dict, randomly generated audio filters",
                        "segment_audio_effects": "list, randomly selected audio effects",
                        "intro_music": "str, path to intro music",
                        "outro_music": "str, path to outro music",
                    },
                }
            ),
            200,
        )
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


# ...existing code...


def generate_random_segments():
    try:
        segments = []
        num_segments = random.randint(1, 5)
        for _ in range(num_segments):
            segments.append(
                {
                    "imageUrl": get_random_pixabay_image(),
                    "audioUrl": get_random_main_audio(),
                }
            )
        return segments
    except Exception as e:
        logger.error(f"Error in generate_random_segments: {e}")
        return []


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


def get_random_main_audio():
    sound_effects_dir = os.path.join("static", "testfiles", "main_audio")
    files = os.listdir(sound_effects_dir)
    if files:
        return "/static/testfiles/main_audio/" + random.choice(files)
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
    return random.choice(ALLOWED_FADE_EFFECTS)


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
