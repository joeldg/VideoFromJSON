"""Tests for video creation endpoint."""
import sys
from unittest.mock import MagicMock

# Mock moviepy modules before any imports
mock_moviepy = MagicMock()
mock_moviepy.video = MagicMock()
mock_moviepy.video.fx = MagicMock()
mock_moviepy.video.fx.all = MagicMock()
mock_moviepy.editor = MagicMock()
mock_moviepy.editor.VideoFileClip = MagicMock()
mock_moviepy.editor.AudioFileClip = MagicMock()
mock_moviepy.editor.ImageClip = MagicMock()
mock_moviepy.editor.concatenate_videoclips = MagicMock()
mock_moviepy.editor.CompositeVideoClip = MagicMock()
mock_moviepy.editor.TextClip = MagicMock()
mock_moviepy.editor.ColorClip = MagicMock()

sys.modules['moviepy'] = mock_moviepy
sys.modules['moviepy.video'] = mock_moviepy.video
sys.modules['moviepy.video.fx'] = mock_moviepy.video.fx
sys.modules['moviepy.video.fx.all'] = mock_moviepy.video.fx.all
sys.modules['moviepy.editor'] = mock_moviepy.editor

import json
import os
import time
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, mock_open, patch

import dotenv
from app.config import Config
from app.endpoints.creation import creation_bp
from app.utils.util_rate_limit import RateLimiter, rate_limiter
from flask import Flask


class TestCreationEndpoint(unittest.TestCase):
    """Test cases for video creation endpoint."""

    def setUp(self):
        """Set up test environment."""
        self.app = Flask(__name__)
        self.app.register_blueprint(creation_bp)
        self.client = self.app.test_client()
        
        # Mock time and datetime
        self.current_time = 1234567890.0
        self.current_datetime = datetime.fromtimestamp(self.current_time)
        
        # Mock environment variables
        self.env_vars = {
            "API_KEY": "test_api_key",
            "PIXABAY_API_KEY": "test_pixabay_key",
            "FLASK_DEBUG": "False",
            "SUPABASE_URL": "test_url",
            "SUPABASE_KEY": "test_key"
        }
        
        # Mock file system
        self.makedirs_calls = []
        
        # Set up patches
        self.patches = [
            patch('time.time', return_value=self.current_time),
            patch(
                'datetime.datetime',
                Mock(now=Mock(return_value=self.current_datetime))
            ),
            patch('os.makedirs', side_effect=self.mock_makedirs),
            patch('os.getenv', side_effect=self.mock_getenv),
            patch('dotenv.load_dotenv'),
            patch('os.path.exists', return_value=True),
            patch('os.path.join', side_effect=os.path.join),
            patch('shutil.rmtree'),
            patch('app.utils.util_video.process_video')
        ]
        
        # Start all patches
        for p in self.patches:
            p.start()
            
        # Initialize test data after patches
        self.valid_api_key = "test-api-key-123"
        self.rate_limiter = RateLimiter()
        
        # Set up API key in Config
        Config.API_KEYS[self.valid_api_key] = {
            "name": "Test Key",
            "plan": "starter",
            "credits_used": 0,
            "credits_reset": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
        
        # Mock request data
        self.valid_request_data = {
            "segments": [
                {
                    "text": "Test segment 1",
                    "duration": 5
                }
            ],
            "video_id": "test-video-123"
        }
        
        # Set up test API key
        self.test_api_key = "test_key_123"
        Config.API_KEYS[self.test_api_key] = {
            "name": "Test Key",
            "plan": "starter",
            "credits_used": 0,
            "credits_reset": "2024-04-24T00:00:00",
            "is_active": True
        }
        
        # Set up test data
        self.test_data = {
            "body": {
                "segments": [
                    {
                        "imageUrl": "https://example.com/image1.png",
                        "audioUrl": "https://example.com/audio1.mp3",
                        "volume": 0.8
                    }
                ],
                "zoom_pan": True,
                "fade_effect": "wipeleft",
                "resolution": "1080x1080"
            }
        }
        
        # Reset rate limiter state
        rate_limiter._request_times = {}
        rate_limiter._credits = {}
        
        # Set up mock classes for moviepy
        self.mock_audio_clip = MagicMock()
        self.mock_audio_clip.duration = 10.0
        
        self.mock_image_clip = MagicMock()
        self.mock_image_clip.set_duration.return_value = self.mock_image_clip
        self.mock_image_clip.set_audio.return_value = self.mock_image_clip
        self.mock_image_clip.fx.return_value = self.mock_image_clip
        self.mock_image_clip.crossfadein.return_value = self.mock_image_clip
        self.mock_image_clip.crossfadeout.return_value = self.mock_image_clip
        
        # Set up mock video clip
        self.mock_video_clip = MagicMock()
        self.mock_video_clip.duration = 10.0
        self.mock_video_clip.write_videofile.return_value = None
        
        # Set up mock thread
        self.mock_thread = MagicMock()
        self.mock_thread.daemon = True
        self.mock_thread.start.return_value = None
        
        # Set up mock time
        self.mock_time = MagicMock()
        self.mock_time.return_value = self.current_time
        
        # Set up mock datetime
        self.mock_datetime = MagicMock()
        self.mock_datetime.now.return_value = self.current_datetime
        self.mock_datetime.fromisoformat = datetime.fromisoformat

    def tearDown(self):
        """Clean up after each test."""
        # Reset rate limiter state
        rate_limiter._request_times = {}
        rate_limiter._credits = {}
        
        # Remove test API key
        if self.test_api_key in Config.API_KEYS:
            del Config.API_KEYS[self.test_api_key]
        
        # Stop all patches
        for p in self.patches:
            p.stop()

    def mock_makedirs(self, path, exist_ok=False):
        self.makedirs_calls.append((path, exist_ok))
        
    def mock_getenv(self, key, default=None):
        return self.env_vars.get(key, default)

    @patch('app.utils.util_video.fetch_resource')
    @patch('app.utils.util_video.AudioFileClip')
    @patch('app.utils.util_video.ImageClip')
    @patch('app.utils.util_video.concatenate_videoclips')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('threading.Thread')
    @patch('threading.Lock')
    @patch('time.time')
    @patch('datetime.datetime')
    def test_create_video_success(
        self,
        mock_datetime,
        mock_time,
        mock_lock,
        mock_thread,
        mock_open,
        mock_makedirs,
        mock_concatenate,
        mock_image_clip,
        mock_audio_clip,
        mock_fetch_resource
    ):
        """Test successful video creation."""
        # Set up mock time
        mock_time.return_value = self.current_time
        mock_datetime.now.return_value = self.current_datetime
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Mock fetch_resource to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_fetch_resource.return_value = mock_response
        
        # Set up mock clips
        mock_audio_clip.return_value = self.mock_audio_clip
        mock_image_clip.return_value = self.mock_image_clip
        mock_concatenate.return_value = self.mock_video_clip
        
        # Set up mock thread
        mock_thread.return_value = self.mock_thread
        
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json=self.test_data
        )
        
        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        self.assertIn('video_id', data)
        self.assertIn('credits', data)
        self.assertEqual(data['status'], 'Processing')
        
        # Check credit information
        credit_info = data['credits']
        self.assertEqual(credit_info['plan'], 'Starter')
        self.assertEqual(credit_info['credits_used'], 1)
        self.assertEqual(credit_info['credits_remaining'], 59)

    def test_missing_api_key(self):
        """Test request without API key."""
        response = self.client.post(
            '/creation',
            json=self.test_data
        )
        
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unauthorized')
        self.assertEqual(data['message'], 'API key required')

    @patch('app.utils.util_video.fetch_resource')
    @patch('app.utils.util_video.AudioFileClip')
    @patch('app.utils.util_video.ImageClip')
    @patch('app.utils.util_video.concatenate_videoclips')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('threading.Thread')
    @patch('threading.Lock')
    @patch('time.time')
    @patch('datetime.datetime')
    def test_rate_limit(
        self,
        mock_datetime,
        mock_time,
        mock_lock,
        mock_thread,
        mock_open,
        mock_makedirs,
        mock_concatenate,
        mock_image_clip,
        mock_audio_clip,
        mock_fetch_resource
    ):
        """Test rate limiting."""
        # Set up mock time
        mock_time.return_value = self.current_time
        mock_datetime.now.return_value = self.current_datetime
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Mock fetch_resource to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_fetch_resource.return_value = mock_response
        
        # Set up mock clips
        mock_audio_clip.return_value = self.mock_audio_clip
        mock_image_clip.return_value = self.mock_image_clip
        mock_concatenate.return_value = self.mock_video_clip
        
        # Set up mock thread
        mock_thread.return_value = self.mock_thread
        
        # First 60 requests should be allowed
        for _ in range(60):
            response = self.client.post(
                '/creation',
                headers={'X-API-Key': self.test_api_key},
                json=self.test_data
            )
            self.assertEqual(response.status_code, 202)
        
        # 61st request should be blocked
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json=self.test_data
        )
        
        self.assertEqual(response.status_code, 429)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Rate limit exceeded')
        self.assertIn('Rate limit exceeded', data['message'])

    def test_credit_limit(self):
        """Test credit limit enforcement."""
        # Set up API key with no remaining credits
        Config.API_KEYS[self.test_api_key]["credits_used"] = 60
        
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json=self.test_data
        )
        
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Credit limit reached')
        self.assertEqual(data['message'], 'Monthly credit limit reached')

    def test_invalid_json(self):
        """Test invalid JSON request."""
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            data='invalid json'
        )
        
        self.assertEqual(response.status_code, 415)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Unsupported Media Type')
        self.assertEqual(data['message'], 'Content-Type must be application/json')

    def test_missing_body(self):
        """Test request without body field."""
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json={"invalid": "data"}
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Invalid JSON format')
        self.assertEqual(data['message'], 'Missing required field: body')

    def test_invalid_segments(self):
        """Test request with invalid segments."""
        invalid_data = {
            "body": {
                "segments": []  # Empty segments list
            }
        }
        
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json=invalid_data
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], 'Invalid JSON format')
        self.assertIn('segments', data['message'])

    @patch('app.utils.util_video.process_video')
    @patch('app.utils.util_video.fetch_resource')
    @patch('app.utils.util_video.AudioFileClip')
    @patch('app.utils.util_video.ImageClip')
    @patch('app.utils.util_video.concatenate_videoclips')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('threading.Thread')
    @patch('threading.Lock')
    @patch('time.time')
    @patch('datetime.datetime')
    def test_video_processing(
        self,
        mock_datetime,
        mock_time,
        mock_lock,
        mock_thread,
        mock_open,
        mock_makedirs,
        mock_concatenate,
        mock_image_clip,
        mock_audio_clip,
        mock_fetch_resource,
        mock_process_video
    ):
        """Test video processing thread creation."""
        # Set up mock time
        mock_time.return_value = self.current_time
        mock_datetime.now.return_value = self.current_datetime
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Mock fetch_resource to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_fetch_resource.return_value = mock_response
        
        # Set up mock clips
        mock_audio_clip.return_value = self.mock_audio_clip
        mock_image_clip.return_value = self.mock_image_clip
        mock_concatenate.return_value = self.mock_video_clip
        
        # Set up mock thread
        mock_thread.return_value = self.mock_thread
        
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json=self.test_data
        )
        
        self.assertEqual(response.status_code, 202)
        
        # Verify process_video was called with correct arguments
        mock_process_video.assert_called_once()
        call_args = mock_process_video.call_args[1]
        self.assertIn('video_id', call_args)
        self.assertIn('segments', call_args)
        self.assertEqual(call_args['zoom_pan'], True)
        self.assertEqual(call_args['fade_effect'], 'wipeleft')
        self.assertEqual(call_args['resolution'], '1080x1080')
        self.assertIn('video_status', call_args)
        self.assertIn('status_lock', call_args)
        self.assertIn('audiogram', call_args)
        self.assertIn('watermark', call_args)
        self.assertIn('background_music', call_args)
        self.assertIn('thumbnail', call_args)
        self.assertIn('audio_enhancement', call_args)
        self.assertIn('dynamic_text', call_args)
        self.assertIn('template', call_args)
        self.assertIn('use_local_files', call_args)
        self.assertIn('intro_music', call_args)
        self.assertIn('outro_music', call_args)
        self.assertIn('audio_filters', call_args)
        self.assertIn('segment_audio_effects', call_args)

    def test_get_endpoint_info(self):
        """Test GET request for endpoint information."""
        response = self.client.get('/creation')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('endpoint', data)
        self.assertIn('method', data)
        self.assertIn('parameters', data)
        self.assertIn('example', data)

    @patch('app.utils.util_video.fetch_resource')
    @patch('app.utils.util_video.AudioFileClip')
    @patch('app.utils.util_video.ImageClip')
    @patch('app.utils.util_video.concatenate_videoclips')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch('threading.Thread')
    @patch('threading.Lock')
    @patch('time.time')
    @patch('datetime.datetime')
    def test_credit_reset(
        self,
        mock_datetime,
        mock_time,
        mock_lock,
        mock_thread,
        mock_open,
        mock_makedirs,
        mock_concatenate,
        mock_image_clip,
        mock_audio_clip,
        mock_fetch_resource
    ):
        """Test credit reset after monthly period."""
        # Set up mock time
        mock_time.return_value = self.current_time
        mock_datetime.now.return_value = self.current_datetime
        mock_datetime.fromisoformat = datetime.fromisoformat
        
        # Mock fetch_resource to return a successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'fake_image_data'
        mock_fetch_resource.return_value = mock_response
        
        # Set up mock clips
        mock_audio_clip.return_value = self.mock_audio_clip
        mock_image_clip.return_value = self.mock_image_clip
        mock_concatenate.return_value = self.mock_video_clip
        
        # Set up mock thread
        mock_thread.return_value = self.mock_thread
        
        # Set up API key with expired reset date
        Config.API_KEYS[self.test_api_key]["credits_reset"] = "2024-03-24T00:00:00"
        Config.API_KEYS[self.test_api_key]["credits_used"] = 60
        
        response = self.client.post(
            '/creation',
            headers={'X-API-Key': self.test_api_key},
            json=self.test_data
        )
        
        self.assertEqual(response.status_code, 202)
        data = json.loads(response.data)
        self.assertEqual(data['credits']['credits_used'], 1)
        self.assertEqual(data['credits']['credits_remaining'], 59)


if __name__ == '__main__':
    unittest.main() 