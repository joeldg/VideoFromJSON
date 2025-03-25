"""Unit tests for video processing utilities."""
from unittest.mock import MagicMock, patch

import pytest
from app.video_processor import VideoProcessor


@pytest.fixture
def sample_video_info():
    """Provide sample video information for tests."""
    return {
        'width': 1920,
        'height': 1080,
        'duration': 30,
        'fps': 30,
        'audio_duration': 30
    }


def test_get_video_info(sample_video_info):
    """Test getting video information."""
    with patch('moviepy.editor.VideoFileClip') as mock_video:
        # Setup mock video
        mock_video_instance = MagicMock()
        mock_video_instance.w = sample_video_info['width']
        mock_video_instance.h = sample_video_info['height']
        mock_video_instance.duration = sample_video_info['duration']
        mock_video_instance.fps = sample_video_info['fps']
        mock_video_instance.audio = MagicMock()
        mock_video_instance.audio.duration = sample_video_info['audio_duration']
        mock_video.return_value = mock_video_instance

        # Test getting video info
        info = VideoProcessor.get_video_info('test.mp4')
        assert info == sample_video_info

        # Test error handling
        mock_video.side_effect = Exception("Test error")
        info = VideoProcessor.get_video_info('test.mp4')
        assert info is None


def test_validate_video_for_platform(sample_video_info):
    """Test video validation for different platforms."""
    with patch('app.video_processor.VideoProcessor.get_video_info') as mock_info:
        mock_info.return_value = sample_video_info

        # Test TikTok validation
        valid, msg = VideoProcessor.validate_video_for_platform(
            'test.mp4', 'tiktok')
        assert not valid
        assert "Resolution" in msg

        # Test Instagram validation
        valid, msg = VideoProcessor.validate_video_for_platform(
            'test.mp4', 'instagram')
        assert not valid
        assert "Resolution" in msg

        # Test Facebook validation
        valid, msg = VideoProcessor.validate_video_for_platform(
            'test.mp4', 'facebook')
        assert valid
        assert "Video meets platform requirements" in msg

        # Test error handling
        mock_info.return_value = None
        valid, msg = VideoProcessor.validate_video_for_platform(
            'test.mp4', 'facebook')
        assert not valid
        assert "Could not read video information" in msg


def test_resize_video():
    """Test video resizing functionality."""
    with patch('moviepy.editor.VideoFileClip') as mock_video, \
         patch('moviepy.editor.ColorClip') as mock_color, \
         patch('moviepy.editor.CompositeVideoClip') as mock_composite:
        
        # Setup mock video
        mock_video_instance = MagicMock()
        mock_video_instance.w = 1920
        mock_video_instance.h = 1080
        mock_video_instance.duration = 30
        mock_video.return_value = mock_video_instance

        # Setup mock color clip
        mock_color_instance = MagicMock()
        mock_color.return_value = mock_color_instance

        # Setup mock composite
        mock_composite_instance = MagicMock()
        mock_composite.return_value = mock_composite_instance

        # Test resizing for TikTok
        output_path = VideoProcessor.resize_video('test.mp4', 'tiktok')
        assert output_path == 'test_tiktok.mp4'

        # Test error handling
        mock_video.side_effect = Exception("Test error")
        output_path = VideoProcessor.resize_video('test.mp4', 'tiktok')
        assert output_path is None


def test_process_video_for_platform(sample_video_info):
    """Test complete video processing workflow."""
    with patch('app.video_processor.VideoProcessor.get_video_info') as mock_info, \
         patch('app.video_processor.VideoProcessor.resize_video') as mock_resize:
        
        # Test successful processing
        mock_info.return_value = sample_video_info
        mock_resize.return_value = 'test_facebook.mp4'
        
        success, msg, output_path = VideoProcessor.process_video_for_platform(
            'test.mp4', 'facebook')
        assert success
        assert "Video processed successfully" in msg
        assert output_path == 'test_facebook.mp4'

        # Test validation failure
        mock_info.return_value = {
            'width': 1080,
            'height': 1920,
            'duration': 30,
            'fps': 30,
            'audio_duration': 30
        }
        success, msg, output_path = VideoProcessor.process_video_for_platform(
            'test.mp4', 'facebook')
        assert not success
        assert "Resolution" in msg
        assert output_path is None

        # Test resize failure
        mock_info.return_value = sample_video_info
        mock_resize.return_value = None
        success, msg, output_path = VideoProcessor.process_video_for_platform(
            'test.mp4', 'facebook')
        assert not success
        assert "Failed to resize video" in msg
        assert output_path is None 