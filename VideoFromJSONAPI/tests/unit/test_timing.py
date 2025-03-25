"""Unit tests for video timing verification."""
import os
import unittest

from moviepy.editor import AudioFileClip, VideoFileClip


class TestVideoTiming(unittest.TestCase):
    """Test cases for video timing verification."""

    def setUp(self):
        """Set up test environment."""
        self.test_video = "tests/testfiles/timing_test.mp4"
        self.segment_duration = 5  # Each segment should be 5 seconds
        self.total_duration = 15  # Total video should be 15 seconds

    def test_video_duration(self):
        """Test that the video has the correct total duration."""
        with VideoFileClip(self.test_video) as video:
            self.assertEqual(video.duration, self.total_duration)

    def test_segment_timings(self):
        """Test that each segment has the correct duration and timing."""
        with VideoFileClip(self.test_video) as video:
            # Check each segment
            for i in range(1, 4):
                start_time = (i - 1) * self.segment_duration
                end_time = i * self.segment_duration
                
                # Extract segment
                segment = video.subclip(start_time, end_time)
                
                # Check duration
                self.assertEqual(
                    segment.duration,
                    self.segment_duration,
                    f"Segment {i} duration incorrect"
                )
                
                # Check if segment has audio
                self.assertIsNotNone(
                    segment.audio,
                    f"Segment {i} has no audio"
                )
                
                # Check audio duration
                self.assertEqual(
                    segment.audio.duration,
                    self.segment_duration,
                    f"Segment {i} audio duration incorrect"
                )

    def test_background_music(self):
        """Test that background music is present and has correct duration."""
        with VideoFileClip(self.test_video) as video:
            # Check if video has audio
            self.assertIsNotNone(video.audio)
            
            # Check audio duration
            self.assertEqual(
                video.audio.duration,
                self.total_duration,
                "Background music duration incorrect"
            )

    def test_segment_transitions(self):
        """Test that segments transition correctly."""
        with VideoFileClip(self.test_video) as video:
            # Check transition points
            for i in range(1, 4):
                transition_time = i * self.segment_duration
                
                # Get frames just before and after transition
                before_frame = video.get_frame(transition_time - 0.1)
                after_frame = video.get_frame(transition_time + 0.1)
                
                # Verify frames are different (transition occurred)
                self.assertFalse(
                    (before_frame == after_frame).all(),
                    f"No transition at {transition_time} seconds"
                )

    def test_audio_sync(self):
        """Test that audio is synchronized with video."""
        with VideoFileClip(self.test_video) as video:
            for i in range(1, 4):
                start_time = (i - 1) * self.segment_duration
                segment = video.subclip(start_time, start_time + 1)
                
                # Check if audio starts with video
                self.assertEqual(
                    segment.audio.start,
                    0,
                    f"Segment {i} audio not synchronized"
                )


if __name__ == "__main__":
    unittest.main() 