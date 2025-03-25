import os
import re
import requests
import subprocess
import logging
import threading
import time
import shutil
import hashlib
from werkzeug.utils import secure_filename
from config import (
    API_KEY,
    PIXABAY_API_KEY,
    SUCCESS_WEBHOOK_URL,
    ERROR_WEBHOOK_URL,
    ALLOWED_FADE_EFFECTS,
    TEMPLATES_DIR,
    pre_roll_video_path,
    post_roll_video_path,
)
from moviepy.editor import (
    AudioFileClip,
    VideoFileClip,
    concatenate_videoclips,  # Ensure concatenate_videoclips is imported
    concatenate_audioclips,  # Ensure concatenate_audioclips is imported
)

logger = logging.getLogger(__name__)
video_status = {}
# Initialize the lock
status_lock = threading.Lock()

CACHE_DIR = "cache"  # Directory to store cached files
CACHE_DURATION = 72 * 3600  # Cache duration in seconds (72 hours)


def validate_api_key(request):
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"API Key from headers: {api_key}")  # Add this line for debugging
    if not api_key and request.is_json:
        api_key = request.get_json().get("api_key")
        logger.debug(f"API Key from JSON: {api_key}")  # Add this line for debugging
    if not api_key:
        api_key = request.form.get("api_key")
        logger.debug(f"API Key from form: {api_key}")  # Add this line for debugging
    if not api_key:
        api_key = request.args.get("api_key")
        logger.debug(f"API Key from args: {api_key}")  # Add this line for debugging
    logger.debug(
        f"API Key being validated: {api_key == API_KEY}"
    )  # Add this line for debugging
    return api_key == API_KEY


def is_valid_directory_name(name):
    return re.match(r"^[a-z0-9]+$", name) is not None


def check_ffmpeg():
    """Verify that FFmpeg is installed and accessible."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.debug("FFmpeg is installed and accessible.")
    except subprocess.CalledProcessError:
        logger.error("FFmpeg is not installed or not found in system PATH.")
        raise EnvironmentError(
            "FFmpeg is required for video processing but is not installed or not found in system PATH."
        )


import subprocess
import traceback
from config import TEMP_VIDEO_DIR, TEMP_VIDEO_PATH
import requests  # Import requests for downloading images


def process_video(
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
    video_status,  # Ensure this parameter is accepted
    status_lock,  # Ensure this parameter is accepted
    intro_music,  # Added parameter
    outro_music,  # Added parameter
    audio_filters,  # Added parameter
    segment_audio_effects,  # Added parameter
):
    try:
        logger.debug(f"Processing video {video_id}")

        # Initialize list for video clips
        clips = []

        for idx, segment in enumerate(segments):
            logger.debug(f"Processing segment {idx+1}/{len(segments)}")
            image_url = segment.get("imageUrl")
            audio_url = segment.get("audioUrl")
            text = segment.get("text", "")
            filter_effect = segment.get("filter", "none")
            duration = segment.get("duration", 3)

            # Download image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                logger.error(f"Failed to download image from {image_url}")
                continue
            image_path = f"temp_images/{video_id}_{idx}.jpg"
            os.makedirs("temp_images", exist_ok=True)
            with open(image_path, "wb") as img_file:
                img_file.write(image_response.content)
            logger.debug(f"Downloaded image to {image_path}")

            # Download audio
            audio_response = requests.get(audio_url)
            if audio_response.status_code != 200:
                logger.error(f"Failed to download audio from {audio_url}")
                continue
            audio_path = f"temp_audios/{video_id}_{idx}.mp3"
            os.makedirs("temp_audios", exist_ok=True)
            with open(audio_path, "wb") as aud_file:
                aud_file.write(audio_response.content)
            logger.debug(f"Downloaded audio to {audio_path}")

            # Create video clip with image and audio
            video_clip = VideoFileClip(image_path).set_duration(duration)
            audio_clip = AudioFileClip(audio_path).subclip(0, duration)
            video_clip = video_clip.set_audio(audio_clip)

            # Apply filter if any
            if filter_effect != "none":
                video_clip = video_clip.fx(getattr(VideoFileClip, filter_effect), 1)

            # Add to clips list
            clips.append(video_clip)

        if not clips:
            logger.error("No valid segments to process.")
            with status_lock:
                video_status[video_id] = "Error: No valid segments."
            return

        # Concatenate all clips
        final_video = concatenate_videoclips(clips, method="compose")
        logger.debug("Concatenated all video clips.")

        # Add background music if provided
        if background_music:
            bg_audio = AudioFileClip(background_music).volumex(0.5)
            final_video = final_video.set_audio(bg_audio)
            logger.debug("Added background music.")

        # Set resolution
        final_video = final_video.resize(newsize=resolution)
        logger.debug(f"Set video resolution to {resolution}.")

        # Export the final video
        output_path = os.path.join("static/videos", f"{video_id}.mp4")
        final_video.write_videofile(output_path, codec="libx264", audio_codec="aac")
        logger.info(f"Video processing completed for ID: {video_id}")

        with status_lock:
            video_status[video_id] = "Completed"

    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}")
        with status_lock:
            video_status[video_id] = "Error"
    finally:
        # Clean up temporary files
        try:
            shutil.rmtree("temp_images")
            shutil.rmtree("temp_audios")
            logger.debug("Cleaned up temporary files.")
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")


def adjust_audio_volume(input_path, output_path, volume):
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-filter:a",
                f"volume={volume}",
                output_path,
            ],
            check=True,
        )
        logger.debug(f"Adjusted audio volume for {input_path} to {volume}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during audio volume adjustment: {e}")
        raise


def download_file(url, path):
    """
    Downloads a file from a URL to the given path, with caching for 72 hours.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Use a hash of the URL as the cache filename to handle files with the same name from different URLs
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    filename = os.path.basename(url)
    cache_filename = f"{url_hash}_{filename}"
    cache_path = os.path.join(CACHE_DIR, cache_filename)

    # Check if the file exists in the cache and is fresh
    if os.path.exists(cache_path):
        file_age = time.time() - os.path.getmtime(cache_path)
        if file_age < CACHE_DURATION:
            # Copy the cached file to the desired path
            shutil.copy(cache_path, path)
            return
        else:
            # Remove stale cache file
            os.remove(cache_path)

    # Download the file since it's not cached or is stale
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(cache_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        # Copy the file to the desired path
        shutil.copy(cache_path, path)
    else:
        raise Exception(f"Failed to download file: {url}")


def clean_cache():
    """
    Removes files from the cache directory that are older than the cache duration.
    """
    if not os.path.exists(CACHE_DIR):
        return
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(file_path):
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > CACHE_DURATION:
                os.remove(file_path)


def get_audio_duration(path):
    result = subprocess.run(
        [
            "ffprobe",
            "-i",
            path,
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=p=0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    duration_str = result.stdout.decode("utf-8").strip()
    duration = float(duration_str)
    logger.debug(f"Got audio duration for {path}: {duration}")
    return duration


def create_video_from_segments(
    images,
    audios,
    durations,
    output_path,
    temp_dir,
    zoom_pan,
    fade_effect,
    audiogram,
    watermark,
    background_music,
    resolution,
    text,
    video_filter,
    segment_audio_effects=None,  # New parameter
):
    temp_video_path = os.path.join(temp_dir, "temp_video.mp4")
    inputs = []
    filter_complex_parts = []
    filter_index = 0
    num_inputs = len(images)
    prev_stream = None

    # Define common frame rate
    common_fps = "25"

    # Add inputs and scale them to the same resolution and frame rate
    for i, image in enumerate(images):
        inputs.extend(["-loop", "1", "-t", str(durations[i]), "-i", image])
        input_label = f"[{filter_index}:v]"
        scaled_label = f"[v{filter_index}]"
        # Scale and set fps for the input image
        filter_complex_parts.append(
            f"{input_label} scale={resolution},fps={common_fps} {scaled_label}"
        )
        filter_index += 1

        if prev_stream is None:
            # First input
            prev_stream = scaled_label
        else:
            # Apply xfade between prev_stream and current scaled_label
            xfade_label = f"[xfade{filter_index}]"
            offset = sum(durations[:i])  # Calculate offset based on durations
            filter_complex_parts.append(
                f"{prev_stream}{scaled_label} xfade=transition={fade_effect}:duration=1:offset={offset} {xfade_label}"
            )
            prev_stream = xfade_label  # Update prev_stream for the next iteration

    # Handle pre-roll video if it exists
    if os.path.exists(pre_roll_video_path):
        inputs.extend(["-i", pre_roll_video_path])
        pre_roll_label = f"[{filter_index}:v]"
        filter_index += 1
        # Scale and set fps for pre-roll
        filter_complex_parts.append(
            f"{pre_roll_label} scale={resolution},fps={common_fps} [scaled_pre]"
        )
        # Transition from pre-roll to first image
        filter_complex_parts.insert(
            0,
            f"[scaled_pre]{prev_stream} xfade=transition={fade_effect}:duration=1:offset=0 [xfade_pre]",
        )
        prev_stream = "[xfade_pre]"

    # Apply any final filters (e.g., format conversion)
    final_label = "[v]"
    filter_complex_parts.append(f"{prev_stream} format=yuv420p {final_label}")

    filter_complex = "; ".join(filter_complex_parts)

    # Build FFmpeg command
    ffmpeg_command = ["ffmpeg", "-y"]
    ffmpeg_command.extend(inputs)
    ffmpeg_command.extend(
        ["-filter_complex", filter_complex, "-map", final_label, temp_video_path]
    )

    try:
        subprocess.run(ffmpeg_command, check=True)
        logger.debug("Video created successfully with ffmpeg")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during video creation: {e}")
        raise

    # Apply per-segment audio effects
    for i, audio in enumerate(audios):
        effects = segment_audio_effects[i] if segment_audio_effects else {}
        apply_audio_effects(audio, effects)

    # ...existing code to merge audio and finalize video...


def merge_audio_files(audio_files, output_path):
    dir_name = os.path.dirname(output_path)
    audio_list_path = os.path.join(dir_name, "audio_list.txt")
    with open(audio_list_path, "w") as f:
        for audio in audio_files:
            abs_audio_path = os.path.abspath(audio)
            f.write(f"file '{abs_audio_path}'\n")

    logger.debug(f"Created audio list file for ffmpeg: {audio_list_path}")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                audio_list_path,
                "-c",
                "copy",
                output_path,
            ],
            check=True,
        )
        logger.debug(f"Merged audio files into {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during audio merging: {e}")
        raise


def remove_temp_files(path):
    if os.path.exists(path):
        subprocess.run(["rm", "-rf", path], check=True)
        logger.debug(f"Removed temporary files at {path}")
    else:
        logger.debug(f"No temporary files to remove at {path}")


def generate_thumbnail(video_path, thumbnail_path):
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-ss",
                "00:00:01.000",
                "-vframes",
                "1",
                thumbnail_path,
            ],
            check=True,
        )
        logger.debug(f"Generated thumbnail for {video_path} at {thumbnail_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during thumbnail generation: {e}")
        raise


def enhance_audio(audio_path, enhancement_params):
    try:
        filters = []
        if "noise_reduction" in enhancement_params:
            nr_level = enhancement_params["noise_reduction"]
            filters.append(f"arnndn=m={nr_level}")
        if "equalization" in enhancement_params:
            eq_settings = enhancement_params["equalization"]
            filters.append(f"equalizer={eq_settings}")
        if not filters:
            return  # No enhancements requested

        filter_str = ",".join(filters)
        enhanced_audio_path = audio_path.replace(".mp3", "_enhanced.mp3")

        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-af", filter_str, enhanced_audio_path],
            check=True,
        )
        os.replace(enhanced_audio_path, audio_path)
        logger.debug(f"Enhanced audio: {audio_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during audio enhancement: {e}")
        raise


def apply_dynamic_text_overlay(video_path, dynamic_text_params, output_path):
    try:
        text = dynamic_text_params.get("text", "")
        position = dynamic_text_params.get("position", "10:10")
        font_size = dynamic_text_params.get("font_size", 24)
        color = dynamic_text_params.get("color", "white")
        start_time = dynamic_text_params.get("start_time", 0)
        end_time = dynamic_text_params.get("end_time", None)

        drawtext_filter = f"drawtext=text='{text}':x={position.split(':')[0]}:y={position.split(':')[1]}:fontsize={font_size}:fontcolor={color}"
        if end_time:
            duration = end_time - start_time
            drawtext_filter += f":enable='between(t,{start_time},{end_time})'"
        else:
            drawtext_filter += f":enable='gte(t,{start_time})'"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-vf",
                drawtext_filter,
                "-codec:a",
                "copy",
                output_path,
            ],
            check=True,
        )
        logger.debug(f"Applied dynamic text overlay: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during dynamic text overlay: {e}")
        raise


def merge_audio_tracks(
    segment_audio_files,
    background_music=None,
    intro_music=None,
    outro_music=None,
    output_path=None,
    duration=None,
    loop_background=False,
    fade_out_background=True,
):
    """
    Merges segment audio files with optional background, intro, and outro music.
    """
    # Ensure output_path is provided
    if not output_path:
        raise ValueError("Output path for merged audio must be specified")

    # Initialize audio clips list
    audio_clips = []

    # Add intro music if available
    if intro_music:
        audio_clips.append(intro_music)

    # Add segment audio files
    for audio_file in segment_audio_files:
        if os.path.exists(audio_file):
            audio_clip = AudioFileClip(audio_file)
            audio_clips.append(audio_clip)
        else:
            print(f"Segment audio file not found: {audio_file}")

    # Add background music if available
    if background_music:
        # ...code to handle background music, looping, and fading...
        pass

    # Add outro music if available
    if outro_music:
        audio_clips.append(outro_music)

    # Merge all audio clips
    if audio_clips:
        final_audio = concatenate_audioclips(audio_clips)
        final_audio.write_audiofile(output_path)
    else:
        raise Exception("No audio clips available to merge")


def apply_audio_effects(audio_path, effects):
    """Applies effects to a single audio file."""  # Use ffmpeg or moviepy to apply effects like volume, fade in/out    # ...code to apply effects...


import json
import logging

logger = logging.getLogger(__name__)


def validate_json(json_data):
    try:
        parsed = json.loads(json_data)
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"JSON validation error: {e}")
        return None


# ...existing code...

import os
import requests
import logging

logger = logging.getLogger(__name__)

# Define the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ...existing code...


def download_file(url):
    """
    Download a file from the given URL.
    If the URL is a local path (starts with /static/), read the file directly from the filesystem.
    Otherwise, download it using HTTP.
    """
    if url.startswith("/static/"):
        # Construct the absolute file path
        file_path = os.path.join(BASE_DIR, url.lstrip("/"))
        if not os.path.isfile(file_path):
            logger.error(f"Local file not found: {file_path}")
            return None
        try:
            with open(file_path, "rb") as f:
                logger.debug(f"Successfully read local file: {file_path}")
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read local file {file_path}: {e}")
            return None
    else:
        # Handle external URLs
        try:
            response = requests.get(url)
            response.raise_for_status()
            logger.debug(f"Successfully downloaded file from URL: {url}")
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to download file from {url}: {e}")
            return None


# ...existing code...


def process_video(
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
    intro_music=None,
    outro_music=None,
    audio_filters=None,
    segment_audio_effects=None,
):
    # ...existing processing code...

    # Handle background music
    if background_music:
        bg_music_content = download_file(background_music)
        if bg_music_content is None:
            logger.error("Background music could not be loaded.")
            with status_lock:
                video_status[video_id] = "Failed: Background music load error"
            return

    # Handle sound effects
    for segment in segments:
        audio_url = segment.get("audioUrl")
        if audio_url:
            audio_content = download_file(audio_url)
            if audio_content is None:
                logger.error(f"Sound effect {audio_url} could not be loaded.")
                with status_lock:
                    video_status[video_id] = "Failed: Sound effect load error"
                return

    # ...rest of the processing code...


def generate_random_intro_music():
    # Implement logic to select or generate intro music
    return ""


def generate_random_outro_music():
    # Implement logic to select or generate outro music
    return ""


def generate_random_audio_filters():
    # Implement logic to generate audio filters
    return {}


def generate_random_segment_audio_effects():
    # Implement logic to generate audio effects for segments
    return []


# ...existing code...

import shutil
import logging

logger = logging.getLogger(__name__)


def is_valid_directory_name(directory_name):
    # Validate directory name to prevent directory traversal
    if "/" in directory_name or "\\" in directory_name:
        logger.warning(f"Invalid directory name detected: {directory_name}")
        return False
    return True


def process_video(
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
):
    try:
        logger.info(f"Processing video ID: {video_id}")
        # Implement video processing logic using moviepy or other libraries
        # This is a placeholder for actual processing
        # Update video_status as processing progresses

        with status_lock:
            video_status[video_id] = "Completed"

        logger.info(f"Video processing completed for ID: {video_id}")
    except Exception as e:
        logger.error(f"Error processing video ID {video_id}: {e}")
        with status_lock:
            video_status[video_id] = "Failed"


def remove_temp_files(temp_dir):
    try:
        shutil.rmtree(temp_dir)
        logger.debug(f"Temporary files removed from {temp_dir}")
    except Exception as e:
        logger.error(f"Error removing temporary files from {temp_dir}: {e}")


# ...additional utility functions as needed...


def get_random_filter():
    # Define available audiogram styles
    return random.choice(["style1", "style2", "style3"])  # Replace with actual styles


def get_random_text():
    texts = ["Sample Text 1", "Sample Text 2", "Sample Text 3"]
    return random.choice(texts)


def get_random_dynamic_text():
    dynamic_texts = ["Dynamic Text 1", "Dynamic Text 2", "Dynamic Text 3"]
    return random.choice(dynamic_texts)


# ...additional utility functions as needed...
