# test_app.py
import unittest
import json
import logging
import os
import io
from unittest.mock import patch
from application import application

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class APITestCase(unittest.TestCase):
    def move_file(self, src, dst):
        if os.path.exists(src):
            os.rename(src, dst)

    def setUp(self):
        self.application = application.test_client()
        self.api_key = '25c05693-b83c-4f0b-b0fb-c0d1a17dd5c2'
        logger.info('Setting up test client and API key')
        self.pre_roll_backup = 'static/videos/pre_roll_backup.mp4'
        self.post_roll_backup = 'static/videos/post_roll_backup.mp4'
        self.move_file('static/videos/pre_roll.mp4', self.pre_roll_backup)
        self.move_file('static/videos/post_roll.mp4', self.post_roll_backup)

    def tearDown(self):
        self.move_file(self.pre_roll_backup, 'static/videos/pre_roll.mp4')
        self.move_file(self.post_roll_backup, 'static/videos/post_roll.mp4')

    @patch('requests.post')
    def test_create_video(self, mock_post):
        logger.info('Starting test_create_video')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        data = {
            "segments": segments
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video passed')

    @patch('requests.post')
    def test_create_video_with_zoom_pan(self, mock_post):
        logger.info('Starting test_create_video_with_zoom_pan')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        data = {
            "segments": segments,
            "zoom_pan": True
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_zoom_pan passed')

    @patch('requests.post')
    def test_create_video_with_fade_effect(self, mock_post):
        logger.info('Starting test_create_video_with_fade_effect')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        data = {
            "segments": segments,
            "fade_effect": "wipeleft"
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_fade_effect passed')

    @patch('requests.post')
    def test_create_video_with_audiogram(self, mock_post):
        logger.info('Starting test_create_video_with_audiogram')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        audiogram = {
            "size": "640x480",
            "gamma": 1.5,
            "color": "red",
            "position": "10:10"
        }
        data = {
            "segments": segments,
            "audiogram": audiogram
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_audiogram passed')

    @patch('requests.post')
    def test_create_video_with_watermark(self, mock_post):
        logger.info('Starting test_create_video_with_watermark')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        watermark = {
            "text": "Sample Watermark",
            "position": "10:10",
            "opacity": 0.5
        }
        data = {
            "segments": segments,
            "watermark": watermark
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_watermark passed')

    @patch('requests.post')
    def test_create_video_with_background_music(self, mock_post):
        logger.info('Starting test_create_video_with_background_music')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        background_music = "https://example.com/background_music.mp3"
        data = {
            "segments": segments,
            "background_music": background_music
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_background_music passed')

    @patch('requests.post')
    def test_create_video_with_audio_volume(self, mock_post):
        logger.info('Starting test_create_video_with_audio_volume')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3",
                "volume": 0.8 + i * 0.1  # Varying volume levels
            })
        data = {
            "segments": segments
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_audio_volume passed')

    @patch('requests.post')
    def test_exceed_segment_limit(self, mock_post):
        logger.info('Starting test_exceed_segment_limit')
        segments = []
        for i in range(21):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        data = {
            "segments": segments
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Number of segments must be between 1 and 20', str(response.data))
        logger.info('test_exceed_segment_limit passed')

    @patch('requests.post')
    def test_invalid_api_key(self, mock_post):
        logger.info('Starting test_invalid_api_key')
        segments = [{
            "imageUrl": "https://picsum.photos/800/600?random=1",
            "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
        }]
        data = {
            "segments": segments
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': 'invalid_api_key'})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', str(response.data))
        logger.info('test_invalid_api_key passed')

    @patch('requests.post')
    def test_invalid_json_format(self, mock_post):
        logger.info('Starting test_invalid_json_format')
        data = {
            "body": "invalid_json"
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid JSON format', str(response.data))
        logger.info('test_invalid_json_format passed')

    @patch('requests.post')
    def test_create_video_with_custom_resolution(self, mock_post):
        logger.info('Starting test_create_video_with_custom_resolution')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        data = {
            "segments": segments,
            "resolution": "1280x720"
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_custom_resolution passed')

    @patch('requests.post')
    def test_create_video_with_thumbnail(self, mock_post):
        logger.info('Starting test_create_video_with_thumbnail')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            })
        data = {
            "segments": segments,
            "thumbnail": True
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_thumbnail passed')

    @patch('requests.post')
    def test_create_video_with_text_overlay(self, mock_post):
        logger.info('Starting test_create_video_with_text_overlay')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3",
                "text": f"Sample Text {i}"  # Adding text overlay
            })
        data = {
            "segments": segments
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_text_overlay passed')

    @patch('requests.post')
    def test_create_video_with_video_filter(self, mock_post):
        logger.info('Starting test_create_video_with_video_filter')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://picsum.photos/800/600?random={i}",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3",
                "filter": "grayscale"  # Adding video filter
            })
        data = {
            "segments": segments
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_video_filter passed')

    def test_create_video_with_audio_enhancement(self):
        logger.info('Starting test_create_video_with_audio_enhancement')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"https://example.com/image{i+1}.png",
                "audioUrl": f"https://example.com/audio{i+1}.mp3",
                "volume": 1.0
            })
        audio_enhancement = {
            "noise_reduction": 0.5,
            "equalization": "f=1000:t=q:w=1.0:g=5"
        }
        data = {
            "segments": segments,
            "audio_enhancement": audio_enhancement
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_audio_enhancement passed')

    @patch('requests.post')
    def test_create_video_with_dynamic_text(self, mock_post):
        logger.info('Starting test_create_video_with_dynamic_text')
        segments = [
            {
                "imageUrl": "https://picsum.photos/800/600?random=13",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            }
        ]
        dynamic_text = {
            "text": "Limited Time Offer!",
            "position": "w/2:(h/2)-50",
            "font_size": 48,
            "color": "red",
            "start_time": 0,
            "end_time": 5
        }
        data = {
            "segments": segments,
            "dynamic_text": dynamic_text
        }
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_dynamic_text passed')

    @patch('requests.post')
    def test_create_video_with_social_preset(self, mock_post):
        logger.info('Starting test_create_video_with_social_preset')
        segments = [
            {
                "imageUrl": "https://picsum.photos/800/600?random=14",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            }
        ]
        data = {
            "segments": segments,
            "social_preset": "tiktok"
        }
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_social_preset passed')

    @patch('requests.post')
    def test_create_video_with_template(self, mock_post):
        logger.info('Starting test_create_video_with_template')
        segments = [
            {
                "imageUrl": "https://picsum.photos/800/600?random=15",
                "audioUrl": "https://downloads.tuxfamily.org/pdsounds/sounds/076No%20Title-.mp3"
            }
        ]
        data = {
            "segments": segments,
            "template": "promo_template.mp4"
        }
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_template passed')

    def test_get_video_status(self):
        logger.info('********* Starting test_get_video_status')
        video_id = 'test_video_id'
        response = self.application.get(f'/api/status/{video_id}')
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Unknown video ID', str(response.data))
        logger.info('test_get_video_status passed')

    def test_list_videos(self):
        logger.info('********* Starting test_list_videos')
        response = self.application.get('/api/videos')
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('videos', str(response.data))
        logger.info('test_list_videos passed')

    def test_delete_video(self):
        logger.info('********* Starting test_delete_video')
        video_id = 'test_video_id'
        video_path = os.path.join('static/videos', f'{video_id}.mp4')
        os.makedirs('static/videos', exist_ok=True)
        with open(video_path, 'w') as f:
            f.write('mock video content')
        
        response = self.application.delete(f'/api/videos/{video_id}')
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Video deleted', str(response.data))
        logger.info('test_delete_video passed')

    def test_upload_pre_roll(self):
        logger.info('Starting test_upload_pre_roll')
        data = {
            'file': (io.BytesIO(b'my file contents'), 'pre_roll.mp4')
        }
        response = self.application.post('/api/pre_roll', content_type='multipart/form-data', data=data)
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Pre-roll video uploaded', str(response.data))
        logger.info('test_upload_pre_roll passed')

    def test_upload_post_roll(self):
        logger.info('Starting test_upload_post_roll')
        data = {
            'file': (io.BytesIO(b'my file contents'), 'post_roll.mp4')
        }
        response = self.application.post('/api/post_roll', content_type='multipart/form-data', data=data)
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Post-roll video uploaded', str(response.data))
        logger.info('test_upload_post_roll passed')

    def test_upload_image(self):
        logger.info('Starting test_upload_image')
        directory = 'testdir123'
        data = {
            'file': (io.BytesIO(b'my image contents'), 'test_image.png')
        }
        response = self.application.post(f'/api/upload_image/{directory}', content_type='multipart/form-data', data=data)
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Image uploaded', str(response.data))
        logger.info('test_upload_image passed')

    def test_upload_image_invalid_directory(self):
        logger.info('Starting test_upload_image_invalid_directory')
        directory = 'invalid_dir!'
        data = {
            'file': (io.BytesIO(b'my image contents'), 'test_image.png')
        }
        response = self.application.post(f'/api/upload_image/{directory}', content_type='multipart/form-data', data=data)
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid directory name', str(response.data))
        logger.info('test_upload_image_invalid_directory passed')

    @patch('requests.post')
    def test_create_video_with_local_files(self, mock_post):
        logger.info('Starting test_create_video_with_local_files')
        segments = []
        for i in range(3):
            segments.append({
                "imageUrl": f"uploads/testdir123/test_image_{i}.png",
                "audioUrl": f"uploads/testdir123/test_audio_{i}.mp3"
            })
        data = {
            "segments": segments,
            "use_local_files": True
        }
        logger.debug(f'Sending request with data: {data}')
        response = self.application.post('/api/creation', json=data, headers={'X-API-Key': self.api_key})
        logger.debug(f'Received response: {response.data}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Processing started', str(response.data))
        logger.info('test_create_video_with_local_files passed')


if __name__ == '__main__':
    logger.info('Starting tests')
    unittest.main()
    logger.info('Tests completed')