"""Social media platform validation and formatting utilities."""
from typing import Dict, Optional, Tuple

from app.config import Config


class SocialMediaValidator:
    """Validator for social media platform requirements."""

    @staticmethod
    def get_platform_specs(platform: str) -> Optional[Dict]:
        """Get specifications for a given platform."""
        return Config.SOCIAL_MEDIA_PRESETS.get(platform.lower())

    @staticmethod
    def validate_duration(platform: str, duration: float) -> Tuple[bool, str]:
        """Validate video duration for the platform."""
        specs = SocialMediaValidator.get_platform_specs(platform)
        if not specs:
            return False, f"Unsupported platform: {platform}"

        max_duration = specs.get("duration_limit")
        if max_duration is None:
            return True, ""

        if duration > max_duration:
            return False, f"Duration exceeds {max_duration} seconds for {platform}"
        return True, ""

    @staticmethod
    def validate_resolution(platform: str, width: int, height: int) -> Tuple[bool, str]:
        """Validate video resolution for the platform."""
        specs = SocialMediaValidator.get_platform_specs(platform)
        if not specs:
            return False, f"Unsupported platform: {platform}"

        target_resolution = specs.get("resolution")
        if not target_resolution:
            return True, ""

        target_width, target_height = map(int, target_resolution.split("x"))
        
        # Allow for small variations in resolution
        width_tolerance = 0.1  # 10% tolerance
        height_tolerance = 0.1  # 10% tolerance
        
        width_diff = abs(width - target_width) / target_width
        height_diff = abs(height - target_height) / target_height
        
        if (width_diff > width_tolerance or height_diff > height_tolerance):
            msg = (f"Resolution {width}x{height} does not match {platform} "
                  f"requirements ({target_resolution})")
            return False, msg
        
        return True, ""

    @staticmethod
    def validate_audio(platform: str, audio_duration: float) -> Tuple[bool, str]:
        """Validate audio duration for the platform."""
        specs = SocialMediaValidator.get_platform_specs(platform)
        if not specs:
            return False, f"Unsupported platform: {platform}"

        max_duration = specs.get("duration_limit")
        if max_duration is None:
            return True, ""

        if audio_duration > max_duration:
            msg = f"Audio duration exceeds {max_duration} seconds for {platform}"
            return False, msg
        return True, ""

    @staticmethod
    def get_target_resolution(platform: str) -> Optional[Tuple[int, int]]:
        """Get target resolution for a platform."""
        specs = SocialMediaValidator.get_platform_specs(platform)
        if not specs:
            return None

        resolution = specs.get("resolution")
        if not resolution:
            return None

        width, height = map(int, resolution.split("x"))
        return width, height

    @staticmethod
    def get_max_duration(platform: str) -> Optional[float]:
        """Get maximum allowed duration for a platform."""
        specs = SocialMediaValidator.get_platform_specs(platform)
        if not specs:
            return None
        return specs.get("duration_limit")

    @staticmethod
    def validate_video_specs(platform: str, width: int, height: int, 
                           duration: float, audio_duration: float) -> Tuple[bool, str]:
        """Validate all video specifications for a platform."""
        # Check resolution
        valid_res, res_msg = SocialMediaValidator.validate_resolution(
            platform, width, height)
        if not valid_res:
            return False, res_msg

        # Check duration
        valid_dur, dur_msg = SocialMediaValidator.validate_duration(
            platform, duration)
        if not valid_dur:
            return False, dur_msg

        # Check audio
        valid_audio, audio_msg = SocialMediaValidator.validate_audio(
            platform, audio_duration)
        if not valid_audio:
            return False, audio_msg

        return True, "Video specifications valid for platform" 