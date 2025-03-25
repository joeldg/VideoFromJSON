import subprocess
import logging
from moviepy.editor import AudioFileClip

logger = logging.getLogger(__name__)


def adjust_audio_volume(input_path, output_path, volume):
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-filter:a",
                f"volume={volume}",
                output_path,
            ],
            check=True,
        )
        logger.debug(f"Adjusted audio volume for {input_path} to {volume}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during audio volume adjustment: {e}")
        raise


def enhance_audio(audio_path, enhancement_params):
    try:
        filters = []
        if "noise_reduction" in enhancement_params:
            nr_level = enhancement_params["noise_reduction"]
            filters.append(f"arnndn=m={nr_level}")
        if "equalization" in enhancement_params:
            eq_settings = enhancement_params["equalization"]
            filters.append(f"equalizer={eq_settings}")
        if not filters:
            return  # No enhancements requested

        filter_str = ",".join(filters)
        enhanced_audio_path = audio_path.replace(".mp3", "_enhanced.mp3")

        subprocess.run(
            ["ffmpeg", "-y", "-i", audio_path, "-af", filter_str, enhanced_audio_path],
            check=True,
        )
        os.replace(enhanced_audio_path, audio_path)
        logger.debug(f"Enhanced audio: {audio_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during audio enhancement: {e}")
        raise


def apply_audio_effects(audio_path, effects):
    """Applies effects to a single audio file."""
    # Use ffmpeg or moviepy to apply effects like volume, fade in/out
    # ...code to apply effects...


def generate_static_audiogram_clip(audio_clip, audiogram_settings):
    # Generate waveform image from audio clip

    # Load audio data from the audio clip's filename
    audio_path = audio_clip.filename  # Get the path to the audio file
    y, sr = librosa.load(
        audio_path, sr=None
    )  # Load audio data with original sampling rate

    # Create waveform plot using matplotlib
    fig, ax = plt.subplots(
        figsize=(
            int(audiogram_settings.get("width", 640)) / 100,
            int(audiogram_settings.get("height", 100)) / 100,
        ),
        dpi=100,
    )
    ax.plot(y, color=audiogram_settings.get("color", "yellow"))
    ax.set_xlim([0, len(y)])
    ax.set_ylim([-1, 1])
    ax.axis("off")  # Hide axes
    plt.tight_layout()

    # Save plot to a buffer
    from io import BytesIO

    buffer = BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buffer)
    plt.close(fig)  # Close the figure to free memory

    # Create an ImageClip from the buffer
    buffer.seek(0)
    from PIL import Image as PILImage

    waveform_image = PILImage.open(buffer)
    waveform_array = np.array(waveform_image)

    audiogram_clip = ImageClip(waveform_array)
    audiogram_clip = audiogram_clip.set_duration(audio_clip.duration)
    audiogram_clip = audiogram_clip.set_position(
        audiogram_settings.get("position", ("center", "bottom"))
    )
    audiogram_clip = audiogram_clip.set_opacity(audiogram_settings.get("opacity", 0.7))

    return audiogram_clip
