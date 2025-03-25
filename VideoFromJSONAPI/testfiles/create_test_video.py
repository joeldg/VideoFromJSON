"""Create test videos for testing."""
import logging

from moviepy.editor import ColorClip, CompositeVideoClip, TextClip

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_square_video():
    """Create a square test video for Instagram."""
    output_path = "tests/testfiles/test_video_square.mp4"
    width = 1080
    height = 1080
    duration = 10
    fps = 30
    
    # Create a white background
    background = ColorClip(
        (width, height),
        color=(255, 255, 255),
        duration=duration
    )
    
    # Add text
    text = TextClip(
        "Test Square Video",
        fontsize=70,
        color="black",
        size=(width, height)
    ).set_duration(duration)
    
    # Composite the clips
    final_clip = CompositeVideoClip([background, text.set_position("center")])
    final_clip.write_videofile(output_path, fps=fps)
    logger.info(f"Created square test video at {output_path}") 