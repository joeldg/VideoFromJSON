"""Command-line interface for video processing."""
import argparse
import json
import logging
import sys
from pathlib import Path

from app.video_processor import VideoProcessor


def setup_logging():
    """Configure logging for the CLI."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def process_video(args):
    """Process a video for a specific platform."""
    logger = setup_logging()
    
    try:
        # Validate input file
        input_path = Path(args.input)
        if not input_path.exists():
            logger.error(f"Input file not found: {args.input}")
            return 1
            
        # Load subtitles if provided
        subtitles = None
        if args.subtitles:
            try:
                with open(args.subtitles) as f:
                    subtitles = json.load(f)
            except Exception as e:
                logger.error(f"Error loading subtitles: {str(e)}")
                return 1
            
        # Process video
        success, msg, output_path = VideoProcessor.process_video_for_platform(
            str(input_path),
            args.platform,
            watermark=args.watermark,
            subtitles=subtitles,
            volume=args.volume,
            fade_in=args.fade_in,
            fade_out=args.fade_out,
            transition=args.transition
        )
            
        if success:
            logger.info(f"Video processed successfully: {output_path}")
            return 0
        else:
            logger.error(f"Failed to process video: {msg}")
            return 1
            
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        return 1


def get_video_info(args):
    """Get information about a video file."""
    logger = setup_logging()
    
    try:
        info = VideoProcessor.get_video_info(args.input)
        if info:
            logger.info("Video Information:")
            for key, value in info.items():
                logger.info(f"{key}: {value}")
            return 0
        else:
            logger.error("Could not read video information")
            return 1
            
    except Exception as e:
        logger.error(f"Error getting video info: {str(e)}")
        return 1


def validate_video(args):
    """Validate a video for a specific platform."""
    logger = setup_logging()
    
    try:
        valid, msg = VideoProcessor.validate_video_for_platform(
            args.input, args.platform)
            
        if valid:
            logger.info(msg)
            return 0
        else:
            logger.error(msg)
            return 1
            
    except Exception as e:
        logger.error(f"Error validating video: {str(e)}")
        return 1


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Video processing tool for social media platforms")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process video command
    process_parser = subparsers.add_parser(
        "process", help="Process a video for a specific platform")
    process_parser.add_argument(
        "input", help="Input video file path")
    process_parser.add_argument(
        "platform", choices=["tiktok", "instagram", "facebook", "youtube"],
        help="Target platform")
    process_parser.add_argument(
        "--watermark", help="Text to use as watermark")
    process_parser.add_argument(
        "--subtitles", help="JSON file containing subtitles")
    process_parser.add_argument(
        "--volume", type=float, default=1.0,
        help="Audio volume (0.0 to 1.0)")
    process_parser.add_argument(
        "--fade-in", type=float, default=0.0,
        help="Fade in duration in seconds")
    process_parser.add_argument(
        "--fade-out", type=float, default=0.0,
        help="Fade out duration in seconds")
    process_parser.add_argument(
        "--transition", choices=["fade", "fade_black", "fade_white"],
        help="Transition effect to apply")
    
    # Get video info command
    info_parser = subparsers.add_parser(
        "info", help="Get information about a video file")
    info_parser.add_argument(
        "input", help="Input video file path")
    
    # Validate video command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a video for a specific platform")
    validate_parser.add_argument(
        "input", help="Input video file path")
    validate_parser.add_argument(
        "platform", choices=["tiktok", "instagram", "facebook", "youtube"],
        help="Target platform")
    
    args = parser.parse_args()
    
    if args.command == "process":
        return process_video(args)
    elif args.command == "info":
        return get_video_info(args)
    elif args.command == "validate":
        return validate_video(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main()) 