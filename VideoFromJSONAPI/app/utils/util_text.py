import subprocess
import logging

logger = logging.getLogger(__name__)


def apply_dynamic_text_overlay(video_path, dynamic_text_params, output_path):
    try:
        text = dynamic_text_params.get("text", "")
        position = dynamic_text_params.get("position", "10:10")
        font_size = dynamic_text_params.get("font_size", 24)
        color = dynamic_text_params.get("color", "white")
        start_time = dynamic_text_params.get("start_time", 0)
        end_time = dynamic_text_params.get("end_time", None)

        drawtext_filter = f"drawtext=text='{text}':x={position.split(':')[0]}:y={position.split(':')[1]}:fontsize={font_size}:fontcolor={color}"
        if end_time:
            duration = end_time - start_time
            drawtext_filter += f":enable='between(t,{start_time},{end_time})'"
        else:
            drawtext_filter += f":enable='gte(t,{start_time})'"

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                video_path,
                "-vf",
                drawtext_filter,
                "-codec:a",
                "copy",
                output_path,
            ],
            check=True,
        )
        logger.debug(f"Applied dynamic text overlay: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"ffmpeg error during dynamic text overlay: {e}")
        raise
