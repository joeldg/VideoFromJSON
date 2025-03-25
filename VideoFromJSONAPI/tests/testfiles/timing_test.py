"""Test video timing with specific audio and image durations."""
import json
import os

import numpy as np
import scipy.io.wavfile as wavfile
from moviepy.editor import (AudioFileClip, ColorClip, CompositeVideoClip,
                            ImageClip, TextClip)
from PIL import Image


def create_beep_sound(
    duration=5, frequency=440, sample_rate=44100, volume=0.5
):
    """Create a beep sound with specified parameters."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    beep = volume * np.sin(2 * np.pi * frequency * t)
    return beep


def create_numbered_images():
    """Create numbered test images."""
    for i in range(1, 4):
        # Create a colored background
        background = ColorClip(
            size=(1920, 1080),
            color=(i * 50, i * 50, i * 50)
        ).set_duration(5)  # Each image will be shown for 5 seconds
        
        # Add number text
        text = TextClip(
            f"Segment {i}",
            fontsize=100,
            color='white',
            size=(1920, 1080),
            method='caption'
        ).set_duration(5)
        
        # Combine clips
        image = CompositeVideoClip([background, text])
        
        # Save frame as numpy array
        frame = image.get_frame(0)
        
        # Convert to PIL Image and save as JPEG
        pil_image = Image.fromarray(frame)
        pil_image = pil_image.convert('RGB')  # Convert to RGB mode
        pil_image.save(f"tests/testfiles/images/{i}.jpg", "JPEG")
        
        # Clean up
        image.close()


def create_test_audio():
    """Create test audio files with specific durations."""
    # Create a 5-second beep sound
    beep_sound = create_beep_sound(duration=5)
    
    # Save the beep sound as a temporary WAV file
    wavfile.write(
        "tests/testfiles/audio/temp_beep.wav",
        44100,
        beep_sound.astype(np.float32)
    )
    
    # Create three segments with different durations
    for i in range(1, 4):
        # Load the beep sound and set duration
        segment = AudioFileClip(
            "tests/testfiles/audio/temp_beep.wav"
        ).set_duration(5)  # Each segment is 5 seconds
        
        # Save the audio segment
        segment.write_audiofile(f"tests/testfiles/audio/segment_{i}.mp3")
        segment.close()
    
    # Create background music (a lower frequency beep)
    background = create_beep_sound(duration=15, frequency=220, volume=0.3)
    wavfile.write(
        "tests/testfiles/audio/temp_background.wav",
        44100,
        background.astype(np.float32)
    )
    
    # Load and save background music
    background_clip = AudioFileClip("tests/testfiles/audio/temp_background.wav")
    background_clip.write_audiofile("tests/testfiles/audio/background.mp3")
    background_clip.close()
    
    # Clean up temporary files
    os.remove("tests/testfiles/audio/temp_beep.wav")
    os.remove("tests/testfiles/audio/temp_background.wav")


def create_timing_test_video():
    """Create a test video with specific timings."""
    # Create segments
    segments = []
    current_time = 0
    
    for i in range(1, 4):
        # Load image and audio
        image = ImageClip(f"tests/testfiles/images/{i}.jpg").set_duration(5)
        audio = AudioFileClip(f"tests/testfiles/audio/segment_{i}.mp3")
        
        # Combine image and audio
        segment = image.set_audio(audio)
        
        # Set start time
        segment = segment.set_start(current_time)
        current_time += 5
        
        segments.append(segment)
    
    # Add background music
    background_music = AudioFileClip("tests/testfiles/audio/background.mp3")
    background_music = background_music.set_duration(15)  # Total duration
    background_music = background_music.volumex(0.3)  # Lower volume
    
    # Combine all segments
    video = CompositeVideoClip(segments)
    video = video.set_audio(background_music)
    
    # Save video
    video.write_videofile(
        "tests/testfiles/timing_test.mp4",
        fps=30,
        codec='libx264',
        audio_codec='aac'
    )
    
    # Clean up
    video.close()


def create_timing_test_json():
    """Create a JSON configuration for timing test."""
    config = {
        "body": {
            "segments": [
                {
                    "imageUrl": "tests/testfiles/images/1.jpg",
                    "audioUrl": "tests/testfiles/audio/segment_1.mp3",
                    "volume": 1.0,
                    "duration": 5
                },
                {
                    "imageUrl": "tests/testfiles/images/2.jpg",
                    "audioUrl": "tests/testfiles/audio/segment_2.mp3",
                    "volume": 1.0,
                    "duration": 5
                },
                {
                    "imageUrl": "tests/testfiles/images/3.jpg",
                    "audioUrl": "tests/testfiles/audio/segment_3.mp3",
                    "volume": 1.0,
                    "duration": 5
                }
            ],
            "background_music": "tests/testfiles/audio/background.mp3",
            "background_volume": 0.3,
            "fade_effect": "fade",
            "fade_duration": 1.0,
            "resolution": "1920x1080"
        }
    }
    
    with open("tests/testfiles/timing_test.json", "w") as f:
        json.dump(config, f, indent=2)


def main():
    """Run the timing test."""
    # Create necessary directories
    os.makedirs("tests/testfiles/images", exist_ok=True)
    os.makedirs("tests/testfiles/audio", exist_ok=True)
    
    # Create test files
    create_numbered_images()
    create_test_audio()
    create_timing_test_video()
    create_timing_test_json()


if __name__ == "__main__":
    main() 