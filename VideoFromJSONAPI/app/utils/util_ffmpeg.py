import subprocess
import logging

logger = logging.getLogger(__name__)


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
