"""Run all test cases for the VideoFromJSON API."""
import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_test_video_creation():
    """Create test videos in different formats."""
    logger.info("Creating test videos...")
    
    # Create landscape video for YouTube
    from testfiles.create_test_video import create_landscape_video
    create_landscape_video()
    
    # Create vertical video for TikTok
    from testfiles.create_tiktok_video import create_vertical_video
    create_vertical_video()
    
    # Create square video for Instagram
    from testfiles.create_test_video import create_square_video
    create_square_video()
    
    logger.info("Test videos created successfully")

def run_subtitle_tests():
    """Test video processing with different subtitle formats."""
    logger.info("Running subtitle tests...")
    
    # Test with karaoke subtitles
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --subtitles tests/testfiles/subtitles/karaoke.json")
    
    # Test with TikTok subtitles
    os.system("python -m app.cli process tests/testfiles/test_video_vertical.mp4 tiktok --subtitles tests/testfiles/subtitles/tiktok.json")
    
    # Test with overlapping subtitles
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --subtitles tests/testfiles/subtitles/overlapping.json")
    
    # Test with quick subtitles
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --subtitles tests/testfiles/subtitles/quick.json")
    
    # Test with long text subtitles
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --subtitles tests/testfiles/subtitles/long_text.json")
    
    logger.info("Subtitle tests completed")

def run_platform_tests():
    """Test video processing for different platforms."""
    logger.info("Running platform-specific tests...")
    
    # Test YouTube processing
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube")
    
    # Test TikTok processing
    os.system("python -m app.cli process tests/testfiles/test_video_vertical.mp4 tiktok")
    
    # Test Instagram processing (using square video)
    os.system("python -m app.cli process tests/testfiles/test_video_square.mp4 instagram")
    
    # Test Facebook processing
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 facebook")
    
    logger.info("Platform tests completed")

def run_enhancement_tests():
    """Test video enhancements like watermarks and transitions."""
    logger.info("Running enhancement tests...")
    
    # Test with watermark
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --watermark 'Test Watermark'")
    
    # Test with fade transition
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --transition fade")
    
    # Test with volume adjustment
    os.system("python -m app.cli process tests/testfiles/test_video.mp4 youtube --volume 1.5")
    
    logger.info("Enhancement tests completed")

def main():
    """Run all tests in sequence."""
    try:
        # Create test videos
        run_test_video_creation()
        
        # Run platform-specific tests
        run_platform_tests()
        
        # Run subtitle tests
        run_subtitle_tests()
        
        # Run enhancement tests
        run_enhancement_tests()
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 