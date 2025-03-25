import unittest
from unittest.mock import patch
from application import application
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TestCreationEndpoint(unittest.TestCase):
    def setUp(self):
        self.app = application.test_client()
        self.app.testing = True
        logger.debug("Test client setup completed")

    @patch("routes.requests.post")
    def test_create_video_with_audio_enhancement_success(self, mock_post):
        mock_post.return_value.status_code = 200
        response = self.app.post('/api/creation', json={
            "segments": [{"imageUrl": "https://example.com/image.jpg", "audioUrl": "https://example.com/audio.mp3"}],
            "audio_enhancement": {"noise_reduction": True, "equalization": "bass_boost"}
        }, headers={"X-API-Key": "your_api_key_here"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Processing started", response.data)
        logger.debug("test_create_video_with_audio_enhancement_success passed")

    @patch("routes.requests.post")
    def test_create_video_invalid_data(self, mock_post):
        mock_post.return_value.status_code = 400
        response = self.app.post('/api/creation', json={}, headers={"X-API-Key": "your_api_key_here"})
        self.assertEqual(response.status_code, 400)
        logger.debug("test_create_video_invalid_data passed")

if __name__ == "__main__":
    unittest.main()