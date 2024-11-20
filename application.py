# app.py
from flask import Flask, request, jsonify, send_from_directory, abort, render_template  # Added for rendering templates
import os
import requests
import subprocess
import uuid
import threading
import logging
from werkzeug.utils import secure_filename
import json  # Added for JSON parsing
from threading import Lock  # Added for thread synchronization
import re  # Added for input validation
import dotenv  # Added for loading .env file

application = Flask(__name__)

# Load environment variables from .env file if not already set
dotenv.load_dotenv()

# Configuration
API_KEY = os.getenv('API_KEY', '{INSERT API KEY HERE}}')
SUCCESS_WEBHOOK_URL = 'https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b'
ERROR_WEBHOOK_URL = 'https://hook.us1.make.com/31yc9urbo92ui6og29em8f5be9rfuj5b'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

video_status = {}
status_lock = Lock()  # Lock for thread-safe updates

pre_roll_video_path = 'static/videos/pre_roll.mp4'
post_roll_video_path = 'static/videos/post_roll.mp4'

ALLOWED_FADE_EFFECTS = {
    'fade', 'wipeleft', 'wiperight', 'wipeup', 'wipedown', 'slideleft', 'slideright', 'slideup', 'slidedown',
    'circlecrop', 'rectcrop', 'distance', 'fadeblack', 'fadewhite', 'radial', 'smoothleft', 'smoothright',
    'smoothup', 'smoothdown', 'circleopen', 'circleclose', 'vertopen', 'vertclose', 'horzopen', 'horzclose',
    'dissolve', 'pixelize', 'diagtl', 'diagtr', 'diagbl', 'diagbr', 'hlslice', 'hrslice', 'vuslice', 'vdslice',
    'hblur', 'fadegrays', 'wipetl', 'wipetr', 'wipebl', 'wipebr', 'squeezeh', 'squeezev'
}

TEMPLATES_DIR = 'templates'  # Directory to store video templates
SOCIAL_MEDIA_PRESETS = {
    'instagram': {'resolution': '1080x1080', 'duration_limit': 60},
    'tiktok': {'resolution': '1080x1920', 'duration_limit': 60},
    'youtube': {'resolution': '1920x1080', 'duration_limit': None},
    # ...add more presets as needed...
}

UPLOADS_DIR = 'uploads'

def allowed_api_key(key):
    return key == API_KEY

def is_valid_directory_name(name):
    return re.match(r'^[a-z0-9]+$', name) is not None

def get_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        api_key = request.form.get('api_key')
    return api_key

@application.route('/api/upload_image/<directory>', methods=['POST'])
def upload_image(directory):
    api_key = get_api_key()
    if not allowed_api_key(api_key):
        logger.warning('Unauthorized access attempt')
        return jsonify({'error': 'Unauthorized'}), 401

    if not is_valid_directory_name(directory):
        return jsonify({'error': 'Invalid directory name'}), 400

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    directory_path = os.path.join(UPLOADS_DIR, directory)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, secure_filename(file.filename))
    file.save(file_path)
    return jsonify({'status': 'Image uploaded', 'file_path': file_path}), 200

@application.route('/api/creation', methods=['POST'])
def create_video():
    api_key = get_api_key()
    if not allowed_api_key(api_key):
        logger.warning('Unauthorized access attempt')
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        if data is None:
            raise ValueError("No JSON data received")

        # If your client sends data under the "body" key, extract it
        # data = data.get('body', data)

        segments = data.get('segments', [])
        zoom_pan = data.get('zoom_pan', False)
        fade_effect = data.get('fade_effect', 'fade')
        audiogram = data.get('audiogram', {})
        watermark = data.get('watermark', {})
        background_music = data.get('background_music', None)
        resolution = data.get('resolution', '1920x1080')
        thumbnail = data.get('thumbnail', False)
        audio_enhancement = data.get('audio_enhancement', {})
        dynamic_text = data.get('dynamic_text', {})
        template = data.get('template', None)
        social_preset = data.get('social_preset', None)
        use_local_files = data.get('use_local_files', False)
        logger.debug(f'Received data: {data}')
    except Exception as e:
        logger.error(f'Invalid JSON format: {e}')
        return jsonify({'error': 'Invalid JSON format'}), 400

    if not segments or not (1 <= len(segments) <= 20):
        logger.error('Number of segments must be between 1 and 20')
        return jsonify({'error': 'Number of segments must be between 1 and 20'}), 400

    if fade_effect not in ALLOWED_FADE_EFFECTS:
        logger.error(f'Invalid fade effect: {fade_effect}')
        return jsonify({'error': 'Invalid fade effect'}), 400

    # Apply social media presets if specified
    if social_preset:
        preset = SOCIAL_MEDIA_PRESETS.get(social_preset)
        if preset:
            resolution = preset.get('resolution', resolution)
            # Implement duration limit if needed
        else:
            logger.error(f'Invalid social media preset: {social_preset}')
            return jsonify({'error': 'Invalid social media preset'}), 400

    video_id = str(uuid.uuid4())
    logger.info(f'Starting video processing with ID: {video_id}')
    with status_lock:
        video_status[video_id] = 'Processing'

    thread = threading.Thread(target=process_video, args=(
        video_id, segments, zoom_pan, fade_effect, audiogram,
        watermark, background_music, resolution, thumbnail,
        audio_enhancement, dynamic_text, template, use_local_files
    ))
    thread.start()

    return jsonify({'status': 'Processing started', 'video_id': video_id}), 200


@application.route('/api/status/<video_id>', methods=['GET'])
def get_video_status(video_id):
    status = video_status.get(video_id, 'Unknown video ID')
    return jsonify({'video_id': video_id, 'status': status})


@application.route('/api/videos', methods=['GET'])
def list_videos():
    videos = os.listdir('static/videos')
    return jsonify({'videos': videos})


@application.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    video_path = os.path.join('static/videos', f'{video_id}.mp4')
    if os.path.exists(video_path):
        os.remove(video_path)
        return jsonify({'status': 'Video deleted'}), 200
    else:
        return jsonify({'error': 'Video not found'}), 404


@application.route('/api/pre_roll', methods=['POST'])
def upload_pre_roll():
    api_key = get_api_key()
    if not allowed_api_key(api_key):
        logger.warning('Unauthorized access attempt')
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file.save(pre_roll_video_path)
        return jsonify({'status': 'Pre-roll video uploaded'}), 200


@application.route('/api/post_roll', methods=['POST'])
def upload_post_roll():
    api_key = get_api_key()
    if not allowed_api_key(api_key):
        logger.warning('Unauthorized access attempt')
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        file.save(post_roll_video_path)
        return jsonify({'status': 'Post-roll video uploaded'}), 200


def process_video(video_id, segments, zoom_pan, fade_effect, audiogram, watermark, background_music, resolution, thumbnail, audio_enhancement, dynamic_text, template, use_local_files):
    try:
        video_status[video_id] = 'Processing'
        # Ensure the output directory exists
        output_dir = 'static/videos'
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f'Ensured output directory exists: {output_dir}')
        
        temp_dir = f'temp/{video_id}'
        os.makedirs(temp_dir, exist_ok=True)
        logger.debug(f'Created directory {temp_dir}')
        image_files = []
        audio_files = []
        durations = []

        # Download files and get durations
        for index, segment in enumerate(segments):
            if use_local_files:
                image_path = segment['imageUrl']
                audio_path = segment['audioUrl']
            else:
                image_url = segment['imageUrl']
                audio_url = segment['audioUrl']
                image_path = os.path.join(temp_dir, f'image_{index}.png')
                audio_path = os.path.join(temp_dir, f'audio_{index}.mp3')
                download_file(image_url, image_path)
                download_file(audio_url, audio_path)

            volume = segment.get('volume', 1.0)  # Default volume is 1.0
            text = segment.get('text', '')  # Text overlay
            video_filter = segment.get('filter', '')  # Video filter

            # Adjust audio volume
            adjusted_audio_path = os.path.join(temp_dir, f'adjusted_audio_{index}.mp3')
            adjust_audio_volume(audio_path, adjusted_audio_path, volume)

            duration = get_audio_duration(adjusted_audio_path)
            durations.append(duration)
            image_files.append(image_path)
            audio_files.append(adjusted_audio_path)

            logger.debug(f'Downloaded and processed segment {index}: image={image_path}, audio={adjusted_audio_path}, duration={duration}, volume={volume}, text={text}, filter={video_filter}')

        if template:
            template_path = os.path.join(TEMPLATES_DIR, template)
            if not os.path.exists(template_path):
                raise Exception(f'Template not found: {template}')
            logger.debug(f'Using template: {template_path}')
            # TODO Implement template processing logic here

        # Apply audio enhancements
        for audio_file in audio_files:
            enhance_audio(audio_file, audio_enhancement)

        # Create video
        video_path = f'static/videos/{video_id}.mp4'
        create_video_from_segments(image_files, audio_files, durations, video_path, temp_dir, zoom_pan, fade_effect, audiogram, watermark, background_music, resolution, text, video_filter)
        logger.info(f'Video created successfully: {video_path}')

        # Add dynamic text overlays
        if dynamic_text:
            temp_video_with_text_path = os.path.join(temp_dir, 'temp_video_with_text.mp4')
            apply_dynamic_text_overlay(temp_video_path, dynamic_text, temp_video_with_text_path)
            temp_video_path = temp_video_with_text_path

        # Generate thumbnail if requested
        if thumbnail:
            thumbnail_path = f'static/videos/{video_id}_thumbnail.png'
            generate_thumbnail(video_path, thumbnail_path)
            logger.info(f'Thumbnail created successfully: {thumbnail_path}')

        # Trigger success webhook
        requests.post(SUCCESS_WEBHOOK_URL, json={'video_url': f'/videos/{video_id}.mp4'})
        logger.info(f'Success webhook triggered for video ID: {video_id}')
        with status_lock:
            video_status[video_id] = 'Completed'
    except Exception as e:
        logger.error(f'Error processing video ID {video_id}: {e}')
        # Trigger error webhook
        requests.post(ERROR_WEBHOOK_URL, json={'error': str(e)}, timeout=5)
        with status_lock:
            video_status[video_id] = 'Failed'
    finally:
        # Clean up
        remove_temp_files(temp_dir)
        logger.debug(f'Removed temporary files for video ID: {video_id}')


def adjust_audio_volume(input_path, output_path, volume):
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-filter:a', f'volume={volume}',
            output_path
        ], check=True)
        logger.debug(f'Adjusted audio volume for {input_path} to {volume}')
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg error during audio volume adjustment: {e}')
        raise


def download_file(url, path):
    try:
        response = requests.get(url, timeout=10)  # Added timeout
        response.raise_for_status()
        with open(path, 'wb') as f:
            f.write(response.content)
        logger.debug(f'Downloaded file from {url} to {path}')
    except requests.RequestException as e:
        logger.error(f'Error downloading file from {url}: {e}')
        raise


def get_audio_duration(path):
    result = subprocess.run(['ffprobe', '-i', path, '-show_entries', 'format=duration',
                             '-v', 'quiet', '-of', 'csv=p=0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    duration_str = result.stdout.decode('utf-8').strip()
    duration = float(duration_str)
    logger.debug(f'Got audio duration for {path}: {duration}')
    return duration


def create_video_from_segments(images, audios, durations, output_path, temp_dir, zoom_pan, fade_effect, audiogram, watermark, background_music, resolution, text, video_filter):
    temp_video_path = os.path.join(temp_dir, 'temp_video.mp4')
    inputs = []
    filter_complex_parts = []
    filter_index = 0
    num_inputs = len(images)
    prev_stream = None

    # Define common frame rate
    common_fps = '25'

    # Add inputs and scale them to the same resolution and frame rate
    for i, image in enumerate(images):
        inputs.extend(['-loop', '1', '-t', str(durations[i]), '-i', image])
        input_label = f'[{filter_index}:v]'
        scaled_label = f'[v{filter_index}]'
        # Scale and set fps for the input image
        filter_complex_parts.append(f'{input_label} scale={resolution},fps={common_fps} {scaled_label}')
        filter_index += 1

        if prev_stream is None:
            # First input
            prev_stream = scaled_label
        else:
            # Apply xfade between prev_stream and current scaled_label
            xfade_label = f'[xfade{filter_index}]'
            offset = sum(durations[:i])  # Calculate offset based on durations
            filter_complex_parts.append(
                f'{prev_stream}{scaled_label} xfade=transition={fade_effect}:duration=1:offset={offset} {xfade_label}'
            )
            prev_stream = xfade_label  # Update prev_stream for the next iteration

    # Handle pre-roll video if it exists
    if os.path.exists(pre_roll_video_path):
        inputs.extend(['-i', pre_roll_video_path])
        pre_roll_label = f'[{filter_index}:v]'
        filter_index += 1
        # Scale and set fps for pre-roll
        filter_complex_parts.append(f'{pre_roll_label} scale={resolution},fps={common_fps} [scaled_pre]')
        # Transition from pre-roll to first image
        filter_complex_parts.insert(0,
            f'[scaled_pre]{prev_stream} xfade=transition={fade_effect}:duration=1:offset=0 [xfade_pre]'
        )
        prev_stream = '[xfade_pre]'

    # Apply any final filters (e.g., format conversion)
    final_label = '[v]'
    filter_complex_parts.append(f'{prev_stream} format=yuv420p {final_label}')

    filter_complex = '; '.join(filter_complex_parts)

    # Build FFmpeg command
    ffmpeg_command = ['ffmpeg', '-y']
    ffmpeg_command.extend(inputs)
    ffmpeg_command.extend([
        '-filter_complex', filter_complex,
        '-map', final_label,
        temp_video_path
    ])

    try:
        subprocess.run(ffmpeg_command, check=True)
        logger.debug('Video created successfully with ffmpeg')
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg error during video creation: {e}')
        raise

    # ...existing code to merge audio and finalize video...


def merge_audio_files(audio_files, output_path):
    dir_name = os.path.dirname(output_path)
    audio_list_path = os.path.join(dir_name, 'audio_list.txt')
    with open(audio_list_path, 'w') as f:
        for audio in audio_files:
            abs_audio_path = os.path.abspath(audio)
            f.write(f"file '{abs_audio_path}'\n")
    
    logger.debug(f'Created audio list file for ffmpeg: {audio_list_path}')
    
    try:
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', audio_list_path,
            '-c', 'copy', output_path
        ], check=True)
        logger.debug(f'Merged audio files into {output_path}')
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg error during audio merging: {e}')
        raise


def remove_temp_files(path):
    if os.path.exists(path):
        subprocess.run(['rm', '-rf', path], check=True)
        logger.debug(f'Removed temporary files at {path}')
    else:
        logger.debug(f'No temporary files to remove at {path}')


@application.route('/download/<filename>', methods=['GET'])
def download_filename(filename):
    # Sanitize the filename to prevent directory traversal attacks
    safe_filename = secure_filename(filename)
    file_path = os.path.join('static/videos', safe_filename)
    if (os.path.isfile(file_path)):
        logger.info(f'Serving file: {safe_filename}')
        return send_from_directory('static/videos', safe_filename, as_attachment=True)
    else:
        logger.error(f'File not found: {safe_filename}')
        return jsonify({'error': 'File not found'}), 404


def generate_thumbnail(video_path, thumbnail_path):
    try:
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-ss', '00:00:01.000', '-vframes', '1',
            thumbnail_path
        ], check=True)
        logger.debug(f'Generated thumbnail for {video_path} at {thumbnail_path}')
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg error during thumbnail generation: {e}')
        raise


def enhance_audio(audio_path, enhancement_params):
    try:
        filters = []
        if 'noise_reduction' in enhancement_params:
            nr_level = enhancement_params['noise_reduction']
            filters.append(f'arnndn=m={nr_level}')
        if 'equalization' in enhancement_params:
            eq_settings = enhancement_params['equalization']
            filters.append(f'equalizer={eq_settings}')
        if not filters:
            return  # No enhancements requested

        filter_str = ','.join(filters)
        enhanced_audio_path = audio_path.replace('.mp3', '_enhanced.mp3')

        subprocess.run([
            'ffmpeg', '-y', '-i', audio_path,
            '-af', filter_str,
            enhanced_audio_path
        ], check=True)
        os.replace(enhanced_audio_path, audio_path)
        logger.debug(f'Enhanced audio: {audio_path}')
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg error during audio enhancement: {e}')
        raise


def apply_dynamic_text_overlay(video_path, dynamic_text_params, output_path):
    try:
        text = dynamic_text_params.get('text', '')
        position = dynamic_text_params.get('position', '10:10')
        font_size = dynamic_text_params.get('font_size', 24)
        color = dynamic_text_params.get('color', 'white')
        start_time = dynamic_text_params.get('start_time', 0)
        end_time = dynamic_text_params.get('end_time', None)

        drawtext_filter = f"drawtext=text='{text}':x={position.split(':')[0]}:y={position.split(':')[1]}:fontsize={font_size}:fontcolor={color}"
        if end_time:
            duration = end_time - start_time
            drawtext_filter += f":enable='between(t,{start_time},{end_time})'"
        else:
            drawtext_filter += f":enable='gte(t,{start_time})'"

        subprocess.run([
            'ffmpeg', '-y', '-i', video_path,
            '-vf', drawtext_filter,
            '-codec:a', 'copy',
            output_path
        ], check=True)
        logger.debug(f'Applied dynamic text overlay: {output_path}')
    except subprocess.CalledProcessError as e:
        logger.error(f'ffmpeg error during dynamic text overlay: {e}')
        raise


@application.route('/web')
def web_index():
    logger.debug('Rendering index.html')
    return render_template('index.html')

@application.route('/web/upload_image')
def web_upload_image():
    logger.debug('Rendering upload_image.html')
    return render_template('upload_image.html')

@application.route('/web/creation')
def web_creation():
    logger.debug('Rendering creation.html')
    return render_template('creation.html')

@application.route('/web/status')
def web_status():
    logger.debug('Rendering status.html')
    return render_template('status.html')

@application.route('/web/videos')
def web_videos():
    logger.debug('Rendering videos.html')
    return render_template('videos.html')

@application.route('/web/pre_roll')
def web_pre_roll():
    logger.debug('Rendering pre_roll.html')
    return render_template('pre_roll.html')

@application.route('/web/post_roll')
def web_post_roll():
    logger.debug('Rendering post_roll.html')
    return render_template('post_roll.html')


@application.route('/health', methods=['GET'])
def health_check():
    return "GOOD"

@application.route('/')
def default_route():
    return '<html><body><b>Hi!</b></body></html>'

if __name__ == '__main__':
    if not os.path.exists('static/videos'):
        os.makedirs('static/videos')  
    application.debug = True
    application.run(host='0.0.0.0', port=5000)

