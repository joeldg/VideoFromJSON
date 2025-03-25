"""Video processing utilities for social media platforms."""
import logging
from typing import Dict, List, Optional, Tuple

import moviepy.editor as mpy
from app.social_media import SocialMediaValidator

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Handles video processing operations for social media platforms."""

    # Platform-specific encoding settings
    ENCODING_PRESETS = {
        "tiktok": {
            "bitrate": "4000k",
            "audio_bitrate": "192k",
            "preset": "medium",
            "crf": 23,
            "max_muxing_queue_size": 1024
        },
        "instagram": {
            "bitrate": "3500k",
            "audio_bitrate": "192k",
            "preset": "medium",
            "crf": 23,
            "max_muxing_queue_size": 1024
        },
        "facebook": {
            "bitrate": "4000k",
            "audio_bitrate": "192k",
            "preset": "medium",
            "crf": 23,
            "max_muxing_queue_size": 1024
        },
        "youtube": {
            "bitrate": "8000k",
            "audio_bitrate": "384k",
            "preset": "slow",
            "crf": 18,
            "max_muxing_queue_size": 1024
        }
    }

    @staticmethod
    def get_encoding_settings(platform: str) -> Dict:
        """Get encoding settings for a platform."""
        return VideoProcessor.ENCODING_PRESETS.get(platform.lower(), {})

    @staticmethod
    def get_watermark_position(position: str):
        """Get watermark position function based on position string."""
        def bottom_right(t):
            return ("right", "bottom")
            
        def bottom_left(t):
            return ("left", "bottom")
            
        def top_right(t):
            return ("right", "top")
            
        def top_left(t):
            return ("left", "top")
            
        positions = {
            "bottom-right": bottom_right,
            "bottom-left": bottom_left,
            "top-right": top_right,
            "top-left": top_left
        }
        return positions.get(position, bottom_right)

    @staticmethod
    def add_watermark(
        video: mpy.VideoFileClip,
        text: str,
        position: str = "bottom-right",
        fontsize: int = 30,
        color: str = "white",
        opacity: float = 0.7
    ) -> mpy.VideoClip:
        """Add a watermark to the video."""
        # Get position function
        pos_func = VideoProcessor.get_watermark_position(position)

        # Create watermark text
        watermark = mpy.TextClip(
            text,
            fontsize=fontsize,
            color=color,
            opacity=opacity,
            method="caption"
        ).set_duration(video.duration)

        # Position watermark
        watermark = watermark.set_position(pos_func)

        # Combine with original video
        return mpy.CompositeVideoClip([video, watermark])

    @staticmethod
    def add_subtitles(
        video: mpy.VideoFileClip,
        subtitles: List[Dict],
        fontsize: int = 30,
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 2
    ) -> mpy.VideoClip:
        """Add subtitles to the video."""
        subtitle_clips = []
        
        for sub in subtitles:
            text = sub["text"]
            start_time = sub["start"]
            end_time = sub["end"]
            
            # Create subtitle text
            subtitle = mpy.TextClip(
                text,
                fontsize=fontsize,
                color=color,
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method="caption"
            ).set_duration(end_time - start_time)
            
            # Position subtitle at bottom center
            subtitle = subtitle.set_position(("center", "bottom"))
            
            # Set timing
            subtitle = subtitle.set_start(start_time)
            
            subtitle_clips.append(subtitle)
        
        # Combine with original video
        return mpy.CompositeVideoClip([video] + subtitle_clips)

    @staticmethod
    def adjust_audio(
        video: mpy.VideoFileClip,
        volume: float = 1.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0
    ) -> mpy.VideoClip:
        """Adjust audio properties of the video."""
        if video.audio is None:
            return video
            
        # Adjust volume
        if volume != 1.0:
            video = video.volumex(volume)
            
        # Add fade in/out
        if fade_in > 0:
            video = video.audio_fadein(fade_in)
        if fade_out > 0:
            video = video.audio_fadeout(fade_out)
            
        return video

    @staticmethod
    def add_transition(
        video: mpy.VideoFileClip,
        transition_type: str = "fade",
        duration: float = 1.0
    ) -> mpy.VideoClip:
        """Add transition effects to the video."""
        if transition_type == "fade":
            return video.fadein(duration).fadeout(duration)
        elif transition_type == "fade_black":
            return video.fadein(duration).fadeout(duration)
        elif transition_type == "fade_white":
            return video.fadein(duration).fadeout(duration)
        else:
            return video

    @staticmethod
    def resize_video(video_path: str, platform: str) -> Optional[str]:
        """Resize video to match platform requirements."""
        try:
            # Get target resolution
            target_res = SocialMediaValidator.get_target_resolution(platform)
            if not target_res:
                logger.error(f"Unsupported platform: {platform}")
                return None

            target_width, target_height = target_res

            # Load video
            video = mpy.VideoFileClip(video_path)
            
            # Calculate new dimensions while maintaining aspect ratio
            current_ratio = video.w / video.h
            target_ratio = target_width / target_height

            if current_ratio > target_ratio:
                # Video is wider than target
                new_width = target_width
                new_height = int(target_width / current_ratio)
                y_offset = (target_height - new_height) // 2
                x_offset = 0
            else:
                # Video is taller than target
                new_height = target_height
                new_width = int(target_height * current_ratio)
                x_offset = (target_width - new_width) // 2
                y_offset = 0

            # Resize video
            resized = video.resize(width=new_width, height=new_height)

            # Create black background
            background = mpy.ColorClip(
                size=(target_width, target_height),
                color=(0, 0, 0)
            ).set_duration(video.duration)

            # Position resized video on background
            final = mpy.CompositeVideoClip([
                background,
                resized.set_position((x_offset, y_offset))
            ])

            # Generate output path
            output_path = video_path.replace('.mp4', f'_{platform}.mp4')

            # Get platform-specific encoding settings
            encoding_settings = VideoProcessor.get_encoding_settings(platform)

            # Write output with platform-specific settings
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                bitrate=encoding_settings.get('bitrate'),
                audio_bitrate=encoding_settings.get('audio_bitrate'),
                preset=encoding_settings.get('preset'),
                ffmpeg_params=[
                    '-crf', str(encoding_settings.get('crf')),
                    '-max_muxing_queue_size', 
                    str(encoding_settings.get('max_muxing_queue_size'))
                ]
            )

            # Clean up
            video.close()
            final.close()

            return output_path

        except Exception as e:
            logger.error(f"Error resizing video: {str(e)}")
            return None

    @staticmethod
    def get_video_info(video_path: str) -> Optional[dict]:
        """Get video information including dimensions and duration."""
        try:
            video = mpy.VideoFileClip(video_path)
            info = {
                'width': video.w,
                'height': video.h,
                'duration': video.duration,
                'fps': video.fps,
                'audio_duration': video.audio.duration if video.audio else 0
            }
            video.close()
            return info
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            return None

    @staticmethod
    def validate_video_for_platform(
        video_path: str, 
        platform: str
    ) -> Tuple[bool, str]:
        """Validate video against platform requirements."""
        # Get video information
        info = VideoProcessor.get_video_info(video_path)
        if not info:
            return False, "Could not read video information"

        # Validate all specifications
        valid, msg = SocialMediaValidator.validate_video_specs(
            platform,
            info['width'],
            info['height'],
            info['duration'],
            info['audio_duration']
        )

        if not valid:
            return False, msg

        return True, "Video meets platform requirements"

    @staticmethod
    def process_video_for_platform(
        video_path: str, 
        platform: str,
        watermark: Optional[str] = None,
        subtitles: Optional[List[Dict]] = None,
        volume: float = 1.0,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
        transition: Optional[str] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """Process video for a specific platform with optional enhancements."""
        try:
            # Load video
            video = mpy.VideoFileClip(video_path)
            
            # Apply enhancements
            if watermark:
                video = VideoProcessor.add_watermark(video, watermark)
            
            if subtitles:
                video = VideoProcessor.add_subtitles(video, subtitles)
            
            video = VideoProcessor.adjust_audio(
                video, volume, fade_in, fade_out)
            
            if transition:
                video = VideoProcessor.add_transition(video, transition)
            
            # First validate the video
            valid, msg = VideoProcessor.validate_video_for_platform(
                video_path, platform)
            if not valid:
                video.close()
                return False, msg, None

            # Resize if needed
            resized_path = VideoProcessor.resize_video(video_path, platform)
            if not resized_path:
                video.close()
                return False, "Failed to resize video", None

            # Clean up
            video.close()

            return True, "Video processed successfully", resized_path
            
        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return False, f"Error processing video: {str(e)}", None 