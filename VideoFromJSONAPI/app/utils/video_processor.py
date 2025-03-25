# Import necessary utilities from utils.py
from .utils import (
    download_file,
    process_video,
    remove_temp_files,
    # ...other imports...
)


class VideoProcessor:
    def __init__(self, segments, options=None):
        self.segments = segments
        self.options = options or {}

    def process(self):
        # Use process_video function from utils.py
        video_id = self.options.get("video_id", "default_id")
        # ...existing code...
        output_path = process_video(
            video_id=video_id,
            segments=self.segments,
            zoom_pan=self.options.get("zoom_pan"),
            fade_effect=self.options.get("fade_effect"),
            audiogram=self.options.get("audiogram"),
            watermark=self.options.get("watermark"),
            background_music=self.options.get("background_music"),
            resolution=self.options.get("resolution"),
            thumbnail=self.options.get("thumbnail"),
            audio_enhancement=self.options.get("audio_enhancement"),
            dynamic_text=self.options.get("dynamic_text"),
            template=self.options.get("template"),
            use_local_files=self.options.get("use_local_files"),
            video_status={},  # Pass appropriate status dictionary
            status_lock=None,  # Pass appropriate lock
            intro_music=self.options.get("intro_music"),
            outro_music=self.options.get("outro_music"),
            audio_filters=self.options.get("audio_filters"),
            segment_audio_effects=self.options.get("segment_audio_effects"),
        )
        # ...existing code...
        return output_path

    # Remove merge_segments method if process_video handles merging
    # ...existing code...


def handle_video_upload(file, directory):
    """
    Handles the upload of a video file to the specified directory.
    """
    try:
        save_path = os.path.join("static/uploads", directory)
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, file.filename))
        logger.debug(f"Video uploaded to {save_path}")
        return "Video uploaded", 200
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        return "Upload failed", 500


def handle_image_upload(file, directory):
    """
    Handles the upload of an image file to the specified directory.
    """
    try:
        save_path = os.path.join("static/uploads", directory)
        os.makedirs(save_path, exist_ok=True)
        file.save(os.path.join(save_path, file.filename))
        logger.debug(f"Image uploaded to {save_path}")
        return "Image uploaded", 200
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return "Upload failed", 500
