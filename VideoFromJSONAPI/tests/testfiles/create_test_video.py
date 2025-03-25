"""Create a test video for subtitle testing."""
from moviepy.editor import ColorClip, CompositeVideoClip, TextClip


def create_landscape_video():
    """Create a landscape test video for YouTube."""
    # Create a blue background
    background = ColorClip(
        size=(1920, 1080),
        color=(0, 0, 255)
    ).set_duration(10)

    # Create text overlay
    text = TextClip(
        "Test Video",
        fontsize=70,
        color='white',
        size=(1920, 1080),
        method='caption'
    ).set_duration(10)

    # Combine clips
    video = CompositeVideoClip([background, text])

    # Save video
    video.write_videofile(
        "tests/testfiles/test_video.mp4",
        fps=30,
        codec='libx264',
        audio=False
    )

    # Clean up
    video.close()


if __name__ == "__main__":
    create_landscape_video() 