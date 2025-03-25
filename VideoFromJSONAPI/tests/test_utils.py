
import os
import time
import json
from unittest import TestCase
from unittest.mock import patch
from application import application
import unittest
import logging
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_pixabay_media(media_type, query):
    cache_dir = 'tests/cache'
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f"{media_type}_{query}.json")
    if os.path.exists(cache_file):
        file_age = time.time() - os.path.getmtime(cache_file)
        if file_age < 7 * 24 * 60 * 60:  # Less than 7 days old
            with open(cache_file, 'r') as f:
                return json.load(f)
    # Fetch from Pixabay and cache the result
    data = pixabay_api_call(media_type, query)
    with open(cache_file, 'w') as f:
        json.dump(data, f)
    return data

class APITestCase(unittest.TestCase):
    def move_file(self, src, dst):
        import shutil
        try:
            shutil.move(src, dst)
            logger.debug(f"Moved file from {src} to {dst}")
            return True
        except Exception as e:
            logger.error(f"Error moving file from {src} to {dst}: {e}")
            return False

    def setUp(self):
        self.app = application.test_client()
        self.app.testing = True
        logger.debug("Test client setup completed")

    def tearDown(self):
        # Cleanup actions if necessary
        logger.debug("Tear down completed")

    @patch("routes.requests.post")
    def test_create_video_with_audio_enhancement(self, mock_post):
        mock_post.return_value.status_code = 200
        response = self.app.post('/api/creation', json={
            "segments": [{"imageUrl": "https://example.com/image.jpg", "audioUrl": "https://example.com/audio.mp3"}],
            "audio_enhancement": {"noise_reduction": True, "equalization": "bass_boost"}
        }, headers={"X-API-Key": "your_api_key_here"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Processing started", response.data)
        logger.debug("test_create_video_with_audio_enhancement passed")

    @patch("routes.requests.post")
    def test_get_video_status(self, mock_post):
        video_id = "test-video-id"
        with patch('routes.video_status', {video_id: "Processing"}):
            response = self.app.get(f'/api/status/{video_id}', headers={"X-API-Key": "your_api_key_here"})
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Processing", response.data)
            logger.debug("test_get_video_status passed")

    def test_list_videos(self):
        response = self.app.get('/api/videos')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json.get("videos", []), list)
        logger.debug("test_list_videos passed")

    def test_delete_video(self):
        video_id = "nonexistent-video-id"
        response = self.app.delete(f'/api/videos/{video_id}')
        self.assertEqual(response.status_code, 404)
        logger.debug("test_delete_video passed")

    def test_upload_pre_roll(self):
        with patch('routes.validate_api_key', return_value=True):
            data = {
                'file': (bytes("fake video content", encoding='utf-8'), 'pre_roll.mp4')
            }
            response = self.app.post('/api/pre_roll', content_type='multipart/form-data', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Pre-roll video uploaded", response.data)
            logger.debug("test_upload_pre_roll passed")

    def test_upload_post_roll(self):
        with patch('routes.validate_api_key', return_value=True):
            data = {
                'file': (bytes("fake video content", encoding='utf-8'), 'post_roll.mp4')
            }
            response = self.app.post('/api/post_roll', content_type='multipart/form-data', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Post-roll video uploaded", response.data)
            logger.debug("test_upload_post_roll passed")

    def test_upload_image(self):
        with patch('routes.validate_api_key', return_value=True):
            data = {
                'file': (bytes("fake image content", encoding='utf-8'), 'image.jpg')
            }
            response = self.app.post('/api/upload_image/test_dir', content_type='multipart/form-data', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Image uploaded", response.data)
            logger.debug("test_upload_image passed")


if __name__ == "__main__":
    unittest.main()