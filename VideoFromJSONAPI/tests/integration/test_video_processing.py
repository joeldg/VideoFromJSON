"""Integration tests for video processing with actual video files."""
import os
import shutil
from pathlib import Path

import pytest
from app.video_processor import VideoProcessor


@pytest.fixture(scope="module")
def test_video_dir():
    """Create and return a temporary directory for test videos."""
    test_dir = Path("tests/test_videos")
    test_dir.mkdir(exist_ok=True)
    yield test_dir
    # Cleanup after tests
    shutil.rmtree(test_dir)


@pytest.fixture(scope="module")
def sample_video(test_video_dir):
    """Create a sample video for testing."""
    from moviepy.editor import (ColorClip, CompositeVideoClip, TextClip,
                                VideoFileClip)

    # Create a simple test video
    duration = 5
    width, height = 1920, 1080
    
    # Create background
    background = ColorClip(
        size=(width, height),
        color=(0, 0, 255)  # Blue background
    ).set_duration(duration)
    
    # Create text overlay
    text = TextClip(
        "Test Video",
        fontsize=70,
        color='white',
        size=(width, height),
        method='caption'
    ).set_duration(duration)
    
    # Combine clips
    video = CompositeVideoClip([background, text])
    
    # Save video
    output_path = test_video_dir / "sample.mp4"
    video.write_videofile(
        str(output_path),
        fps=30,
        codec='libx264',
        audio_codec='aac'
    )
    
    # Clean up
    video.close()
    
    return str(output_path)


def test_process_video_for_tiktok(sample_video):
    """Test processing a video for TikTok."""
    success, msg, output_path = VideoProcessor.process_video_for_platform(
        sample_video, "tiktok")
    
    assert success
    assert os.path.exists(output_path)
    
    # Verify output video properties
    info = VideoProcessor.get_video_info(output_path)
    assert info is not None
    assert info['width'] == 1080
    assert info['height'] == 1920
    assert info['duration'] <= 60


def test_process_video_for_instagram(sample_video):
    """Test processing a video for Instagram."""
    success, msg, output_path = VideoProcessor.process_video_for_platform(
        sample_video, "instagram")
    
    assert success
    assert os.path.exists(output_path)
    
    # Verify output video properties
    info = VideoProcessor.get_video_info(output_path)
    assert info is not None
    assert info['width'] == 1080
    assert info['height'] == 1080
    assert info['duration'] <= 60


def test_process_video_for_facebook(sample_video):
    """Test processing a video for Facebook."""
    success, msg, output_path = VideoProcessor.process_video_for_platform(
        sample_video, "facebook")
    
    assert success
    assert os.path.exists(output_path)
    
    # Verify output video properties
    info = VideoProcessor.get_video_info(output_path)
    assert info is not None
    assert info['width'] == 1920
    assert info['height'] == 1080
    assert info['duration'] <= 600


def test_process_video_for_youtube(sample_video):
    """Test processing a video for YouTube."""
    success, msg, output_path = VideoProcessor.process_video_for_platform(
        sample_video, "youtube")
    
    assert success
    assert os.path.exists(output_path)
    
    # Verify output video properties
    info = VideoProcessor.get_video_info(output_path)
    assert info is not None
    assert info['width'] == 1920
    assert info['height'] == 1080
    assert info['duration'] <= 43200


def test_process_video_invalid_platform(sample_video):
    """Test processing a video for an invalid platform."""
    success, msg, output_path = VideoProcessor.process_video_for_platform(
        sample_video, "invalid_platform")
    
    assert not success
    assert "Unsupported platform" in msg
    assert output_path is None


def test_process_video_nonexistent_file():
    """Test processing a nonexistent video file."""
    success, msg, output_path = VideoProcessor.process_video_for_platform(
        "nonexistent.mp4", "tiktok")
    
    assert not success
    assert "Could not read video information" in msg
    assert output_path is None 