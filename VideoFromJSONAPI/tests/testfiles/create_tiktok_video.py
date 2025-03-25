"""Create a vertical test video for TikTok testing."""
from moviepy.editor import ColorClip, CompositeVideoClip, TextClip


def create_vertical_video():
    """Create a vertical test video for TikTok."""
    # Create a blue background
    background = ColorClip(
        size=(1080, 1920),  # Vertical format for TikTok
        color=(0, 0, 255)
    ).set_duration(10)

    # Create text overlay
    text = TextClip(
        "TikTok Test Video",
        fontsize=70,
        color='white',
        size=(1080, 1920),
        method='caption'
    ).set_duration(10)

    # Combine clips
    video = CompositeVideoClip([background, text])

    # Save video
    video.write_videofile(
        "tests/testfiles/test_video_vertical.mp4",
        fps=30,
        codec='libx264',
        audio=False
    )

    # Clean up
    video.close()


if __name__ == "__main__":
    create_vertical_video() 