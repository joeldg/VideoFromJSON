import os
import requests
import subprocess
import logging
import threading
from werkzeug.utils import secure_filename
from config import (
    API_KEY,
    SUCCESS_WEBHOOK_URL,
    ERROR_WEBHOOK_URL,
    ALLOWED_FADE_EFFECTS,
    TEMPLATES_DIR,
    pre_roll_video_path,
    post_roll_video_path,
)

logger = logging.getLogger(__name__)


def allowed_api_key(key):
    return key == API_KEY


def is_valid_directory_name(name):
    return re.match(r"^[a-z0-9]+$", name) is not None


def get_api_key(request):
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        api_key = request.form.get("api_key")
    return api_key


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
):
    try:
        video_status[video_id] = "Processing"
        # Ensure the output directory exists
        output_dir = "static/videos"
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir}")

        temp_dir = f"temp/{video_id}"
        os.makedirs(temp_dir, exist_ok=True)
        logger.debug(f"Created directory {temp_dir}")
        image_files = []
        audio_files = []
        durations = []

        # Download files and get durations
        for index, segment in enumerate(segments):
            if use_local_files:
                image_path = segment["imageUrl"]
                audio_path = segment["audioUrl"]
            else:
                image_url = segment["imageUrl"]
                audio_url = segment["audioUrl"]
                image_path = os.path.join(temp_dir, f"image_{index}.png")
                audio_path = os.path.join(temp_dir, f"audio_{index}.mp3")
                download_file(image_url, image_path)
                download_file(audio_url, audio_path)

            volume = segment.get("volume", 1.0)  # Default volume is 1.0
            text = segment.get("text", "")  # Text overlay
            video_filter = segment.get("filter", "")  # Video filter

            # Adjust audio volume
            adjusted_audio_path = os.path.join(temp_dir, f"adjusted_audio_{index}.mp3")
            adjust_audio_volume(audio_path, adjusted_audio_path, volume)

            duration = get_audio_duration(adjusted_audio_path)
            durations.append(duration)
            image_files.append(image_path)
            audio_files.append(adjusted_audio_path)

            logger.debug(
                f"Downloaded and processed segment {index}: image={image_path}, audio={adjusted_audio_path}, duration={duration}, volume={volume}, text={text}, filter={video_filter}"
            )

        if template:
            template_path = os.path.join(TEMPLATES_DIR, template)
            if not os.path.exists(template_path):
                raise Exception(f"Template not found: {template}")
            logger.debug(f"Using template: {template_path}")
            # TODO Implement template processing logic here

        # Apply audio enhancements
        for audio_file in audio_files:
            enhance_audio(audio_file, audio_enhancement)

        # Create video
        video_path = f"static/videos/{video_id}.mp4"
        create_video_from_segments(
            image_files,
            audio_files,
            durations,
            video_path,
            temp_dir,
            zoom_pan,
            fade_effect,
            audiogram,
            watermark,
            background_music,
            resolution,
            text,
            video_filter,
        )
        logger.info(f"Video created successfully: {video_path}")

        # Add dynamic text overlays
        if dynamic_text:
            temp_video_with_text_path = os.path.join(
                temp_dir, "temp_video_with_text.mp4"
            )
            apply_dynamic_text_overlay(
                temp_video_path, dynamic_text, temp_video_with_text_path
            )
            temp_video_path = temp_video_with_text_path

        # Generate thumbnail if requested
        if thumbnail:
            thumbnail_path = f"static/videos/{video_id}_thumbnail.png"
            generate_thumbnail(video_path, thumbnail_path)
            logger.info(f"Thumbnail created successfully: {thumbnail_path}")

        # Trigger success webhook
        requests.post(
            SUCCESS_WEBHOOK_URL, json={"video_url": f"/videos/{video_id}.mp4"}
        )
        logger.info(f"Success webhook triggered for video ID: {video_id}")
        with status_lock:
            video_status[video_id] = "Completed"
    except Exception as e:
        logger.error(f"Error processing video ID {video_id}: {e}")
        # Trigger error webhook
        requests.post(ERROR_WEBHOOK_URL, json={"error": str(e)}, timeout=5)
        with status_lock:
            video_status[video_id] = "Failed"
    finally:
        # Clean up
        remove_temp_files(temp_dir)
        logger.debug(f"Removed temporary files for video ID: {video_id}")


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
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)
        logger.debug(f"Downloaded file from {url} to {path}")
    except requests.RequestException as e:
        logger.error(f"Error downloading file from {url}: {e}")
        raise


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
