import logging
import os
import shutil
import subprocess
# Fix for PIL.Image.ANTIALIAS deprecation
from io import BytesIO

import librosa
import matplotlib.pyplot as plt
import moviepy.video.fx.all as vfx
import numpy as np
import requests
from app.config import Config
from moviepy.editor import \
    ColorClip  # Import ColorClip for placeholder audiogram
from moviepy.editor import ImageClip  # Added import for ImageClip
from moviepy.editor import afx  # Import audio effects module
from moviepy.editor import (AudioFileClip, CompositeAudioClip,
                            CompositeVideoClip, TextClip, VideoClip,
                            VideoFileClip, concatenate_audioclips,
                            concatenate_videoclips)
from PIL import Image
from PIL import Image as PILImage

from .util_file import download_file

if not hasattr(Image, "ANTIALIAS"):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from matplotlib.backends.backend_agg import \
    FigureCanvasAgg as FigureCanvas  # For rendering plots to images

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)


def fetch_resource(url):
    logger.error(f"Fetching resource from URL: {url}")
    local_path = os.path.join(Config.ROOT_DIR + "/", url.lstrip("/"))
    if os.path.exists(local_path):
        logger.error(f"Local path exists: {local_path}")
        with open(local_path, "rb") as f:

            class Response:
                status_code = 200
                content = f.read()

        return Response()
    else:
        logger.error(f"Local path does not exist: {local_path}")
        parsed_url = requests.utils.urlparse(url)
        if parsed_url.scheme not in ["http", "https"]:
            logger.warn(f"Local_path not found: {local_path}")
            logger.warn(f"Invalid URL scheme for resource: {url}")
            raise ValueError(f"Invalid URL scheme for resource: {url}")
        return requests.get(url)


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
    logger.error(f"Starting process_video for video_id: {video_id}")
    try:
        logger.error(f"Processing video {video_id}")

        # Initialize list for video clips
        clips = []

        # Ensure segments is a list of dictionaries
        if not isinstance(segments, list):
            segments = [segments]
        
        for idx, segment in enumerate(segments):
            logger.error(f"Processing segment {idx+1}/{len(segments)}: {segment}")
            if isinstance(segment, str):
                # If segment is a string, treat it as an image URL
                image_url = segment
                audio_url = None
                text = ""
            else:
                # If segment is a dictionary, extract the values
                image_url = segment.get("imageUrl")
                audio_url = segment.get("audioUrl")
                text = segment.get("text", "")
            filter_effect = segment.get("filter", "none")

            # Remove or comment out the faulty debug statement
            # logger.error(f"Segment {idx+1} duration: {duration} seconds")

            # Download image
            image_response = fetch_resource(image_url)
            if image_response.status_code != 200:
                logger.warn(f"Failed to download image from {image_url}")
                continue
            image_path = f"temp/temp_images/{video_id}_{idx}.jpg"
            os.makedirs("temp/temp_images", exist_ok=True)
            with open(image_path, "wb") as img_file:
                img_file.write(image_response.content)
            logger.error(f"Downloaded image to {image_path}")

            # Download audio
            audio_response = fetch_resource(audio_url)
            if audio_response.status_code != 200:
                logger.warn(f"Failed to download audio from {audio_url}")
                continue
            audio_path = f"temp/temp_audios/{video_id}_{idx}.mp3"
            os.makedirs("temp/temp_audios", exist_ok=True)
            with open(audio_path, "wb") as aud_file:
                aud_file.write(audio_response.content)
            logger.error(f"Downloaded audio to {audio_path}")

            # Load audio clip
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            logger.error(
                f"Original audio clip {idx+1} duration: {audio_duration} seconds"
            )

            # Determine max_duration if provided
            # set duration to the lesser of audio duration and max_duration
            max_duration = segment.get("max_duration", None)
            if max_duration is not None:
                logger.error(f"Segment {idx+1} max_duration: {max_duration} seconds")
                # Use the lesser of audio duration and max_duration
                duration = min(audio_duration, max_duration)
            else:
                duration = audio_duration
            logger.error(f"Segment {idx+1} final duration: {duration} seconds")

            # Adjust audio clip duration if needed
            if audio_duration > duration:
                # Trim the audio to match the duration
                audio_duration = duration
                audio_clip = audio_clip.subclip(0, duration)
                logger.error(f"Trimmed audio clip {idx+1} to {duration} seconds")
            # No need to loop audio if it's shorter than duration, since duration == audio_duration

            # Create video clip with image and set duration to match audio duration
            image_clip = ImageClip(image_path).set_duration(audio_duration)
            logger.debug(f"Set image clip duration to {audio_duration} seconds")

            # Apply zoom and pan if enabled
            if zoom_pan:
                image_clip = image_clip.fx(
                    vfx.resize, 1.1
                )  # Changed from vfx.zoom_in to vfx.resize
                logger.debug("Applied zoom and pan effect")

            # Generate audiogram if requested
            if audiogram:
                # Placeholder function for generating audiogram clip
                audiogram_clip = generate_audiogram_clip(
                    audio_clip, audiogram_settings=audiogram
                )
                image_clip = CompositeVideoClip([image_clip, audiogram_clip])
                logger.debug("Added audiogram overlay to video clip")

            # Set audio to the video clip
            video_clip = image_clip.set_audio(audio_clip)

            # Apply fade effects if any
            if fade_effect != "none":
                video_clip = video_clip.crossfadein(1).crossfadeout(1)
                logger.debug(f"Applied fade effects to segment {idx+1}")

            # Add to clips list
            clips.append(video_clip)

        if not clips:
            logger.warn("No valid segments to process.")
            with status_lock:
                video_status[video_id] = "Error: No valid segments."
            return

        # Concatenate all clips with crossfade effect
        final_video = concatenate_videoclips(clips, method="compose")
        logger.debug("Concatenated video clips with compose method")

        # Set fps for the final video
        fps = 24  # You can choose a different fps if needed
        final_video.fps = fps

        # Add background music with volume at 40%
        logger.error("*********** Background music ***********")
        if background_music:
            logger.error(os.path.join(Config.ROOT_DIR, background_music))
            logger.debug("Adding background music with 40% volume")
            bg_audio_path = os.path.join(
                Config.ROOT_DIR, background_music
            )  # Use os.path.join for path
            bg_audio = AudioFileClip(bg_audio_path.lstrip("/")).volumex(
                0.4
            )  # Set volume to 40%
            video_audio = final_video.audio
            final_audio = CompositeAudioClip([video_audio, bg_audio])
            final_video = final_video.set_audio(final_audio)
            logger.debug("Background music added to final video")

        # Set resolution
        try:
            width, height = map(int, resolution.lower().split("x"))
            final_video = final_video.resize(newsize=(width, height))
            logger.error(f"Set video resolution to {(width, height)}.")
        except ValueError as e:
            logger.warn(f"Invalid resolution format '{resolution}': {e}")
            raise ValueError(f"Invalid resolution format '{resolution}': {e}")

        # Add watermark if requested
        if watermark:
            watermark_text = watermark.get("text", "")
            watermark_position = watermark.get("position", "bottom")
            watermark_font_size = watermark.get("font_size", 24)
            watermark_color = watermark.get("color", "white")
            watermark_opacity = watermark.get("opacity", 0.5)
            
            # Create watermark clip without opacity first
            watermark_clip = TextClip(
                watermark_text,
                font_size=watermark_font_size,
                color=watermark_color
            ).set_position(watermark_position).set_duration(final_video.duration)
            
            # Set opacity after creation
            watermark_clip = watermark_clip.set_opacity(watermark_opacity)
            
            # Composite watermark with video
            final_video = CompositeVideoClip([final_video, watermark_clip])
            logger.debug("Added watermark to final video")

        # Export the final video with specified fps
        output_path = os.path.join("static/videos", f"{video_id}.mp4")
        final_video.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=fps
        )
        logger.info(f"Video processing completed for ID: {video_id}")

        with status_lock:
            video_status[video_id] = "Completed"

    except Exception as e:
        logger.warn(f"Exception in process_video: {e}")
        logger.warn(f"Error processing video {video_id}: {e}")
        with status_lock:
            video_status[video_id] = "Error"
    finally:
        logger.error("Cleaning up temporary files.")
        # Clean up temporary files
        try:
            shutil.rmtree("temp/temp_images")
            shutil.rmtree("temp/temp_audios")
            logger.error("Cleaned up temporary files.")
        except Exception as cleanup_error:
            logger.warn(f"Error during cleanup: {cleanup_error}")


def generate_audiogram_clip(audio_clip, audiogram_settings):
    # Load audio data from the audio clip's filename
    audio_path = audio_clip.filename  # Get the path to the audio file
    y, sr = librosa.load(
        audio_path, sr=None
    )  # Load audio data with original sampling rate

    # Audiogram settings with defaults
    width = int(audiogram_settings.get("width", 640))
    height = int(audiogram_settings.get("height", 100))
    color = audiogram_settings.get("color", "yellow")
    background_color = audiogram_settings.get("background_color", "black")
    gamma = float(audiogram_settings.get("gamma", 0.2))  # Default gamma is 0.2
    position = audiogram_settings.get("position", ("center", "bottom"))
    opacity = float(audiogram_settings.get("opacity", 0.7))
    fps = int(
        audiogram_settings.get("fps", 24)
    )  # Frames per second for the audiogram clip

    duration = audio_clip.duration
    total_frames = int(duration * fps)

    # Normalize audio data
    y = y / np.max(np.abs(y))

    # Prepare the time axis for the entire audio clip
    time_axis = np.linspace(0, duration, num=len(y))

    # Function to generate frames for the audiogram animation
    def make_frame(t):
        current_sample = int(t * sr)
        window_size = int(sr / fps)  # Number of samples per frame
        start = max(current_sample - window_size, 0)
        end = current_sample

        # Slice the audio data for the current frame
        y_frame = y[start:end]
        time_frame = time_axis[start:end]

        # Create waveform plot
        fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
        fig.patch.set_facecolor(background_color)
        ax.plot(time_frame, y_frame, color=color, linewidth=1)
        ax.set_xlim(t - (1.0 / fps), t)
        ax.set_ylim(-1, 1)
        ax.axis("off")
        plt.tight_layout(pad=0)

        # Adjust background gamma (brightness)
        fig.patch.set_alpha(gamma)

        # Save plot to buffer
        buffer = BytesIO()
        plt.savefig(buffer, format="png")  # Change format to 'png'
        buffer.seek(0)
        plt.close(fig)

        # Read the buffer and convert to numpy array
        image = PILImage.open(buffer)
        frame = np.array(image)

        # Ensure frame is in the correct color format
        if frame.shape[2] == 4:  # If RGBA, convert to RGB
            frame = frame[:, :, :3]

        return frame

    # Create the animated audiogram clip
    audiogram_clip = VideoClip(make_frame, duration=duration).set_fps(fps)
    audiogram_clip = audiogram_clip.set_position(position)
    audiogram_clip = audiogram_clip.set_opacity(opacity)

    return audiogram_clip


def merge_audio_files(audio_files, output_path):
    logger.error(f"Merging audio files: {audio_files} into {output_path}")
    dir_name = os.path.dirname(output_path)
    audio_list_path = os.path.join(dir_name, "audio_list.txt")
    with open(audio_list_path, "w") as f:
        for audio in audio_files:
            abs_audio_path = os.path.abspath(audio)
            f.write(f"file '{abs_audio_path}'\n")

    logger.error(f"Created audio list file for ffmpeg: {audio_list_path}")

    try:
        logger.error("Running ffmpeg for merging audio files.")
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
        logger.error(f"Merged audio files into {output_path}")
    except subprocess.CalledProcessError as e:
        logger.warn(f"ffmpeg error during audio merging: {e}")
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
    logger.error(f"Merging audio tracks into {output_path}")
    """
    Merges segment audio files with optional background, intro, and outro music.
    """
    # Ensure output_path is provided
    if not output_path:
        logger.error("Output path not provided for merge_audio_tracks.")
        raise ValueError("Output path for merged audio must be specified")

    # Initialize audio clips list
    audio_clips = []

    # Add intro music if available
    if intro_music:
        logger.error("Adding intro music.")
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


def generate_thumbnail(video_path, thumbnail_path):
    logger.error(f"Generating thumbnail for {video_path} at {thumbnail_path}")
    try:
        logger.error("Running ffmpeg for thumbnail generation.")
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
        logger.error(f"Generated thumbnail for {video_path} at {thumbnail_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during thumbnail generation: {e}")
        raise
