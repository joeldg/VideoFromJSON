import unittest
import sys
import os
from unittest.mock import patch  # Ensure patch is imported

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from application import application  # Import the Flask app instance
from app.utils import *
from app.utils.util_auth import validate_api_key  # Import validate_api_key directly
import logging
import io

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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

    @patch("app.utils.util_auth.validate_api_key")
    @patch("requests.post")  # Correctly patch the requests module
    def test_create_video_with_audio_enhancement(
        self, mock_post, mock_validate_api_key
    ):
        mock_validate_api_key.return_value = True
        mock_post.return_value.status_code = 200
        response = self.app.post(
            "/api/creation",
            json={
                "segments": [
                    {
                        "imageUrl": "https://example.com/image.jpg",
                        "audioUrl": "https://example.com/audio.mp3",
                    }
                ],
                "audio_enhancement": {
                    "noise_reduction": True,
                    "equalization": "bass_boost",
                },
            },
            headers={"X-API-Key": "your_api_key_here"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Processing started", response.data)
        logger.debug("test_create_video_with_audio_enhancement passed")

    @patch("app.utils.util_auth.validate_api_key")
    @patch("requests.post")  # Correctly patch the requests module
    def test_get_video_status(self, mock_post, mock_validate_api_key):
        mock_validate_api_key.return_value = True
        video_id = "test-video-id"
        with patch("app.routes.creation.video_status", {"test-video-id": "Processing"}):
            response = self.app.get(
                f"/api/status/{video_id}", headers={"X-API-Key": "your_api_key_here"}
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Processing", response.data)
            logger.debug("test_get_video_status passed")

    @patch("app.utils.util_auth.validate_api_key")
    def test_list_videos(self, mock_validate_api_key):
        mock_validate_api_key.return_value = True
        response = self.app.get("/api/videos")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json.get("videos", []), list)
        logger.debug("test_list_videos passed")

    @patch("app.utils.util_auth.validate_api_key")
    def test_delete_video(self, mock_validate_api_key):
        mock_validate_api_key.return_value = True
        video_id = "nonexistent-video-id"
        response = self.app.delete(f"/api/videos/{video_id}")
        self.assertEqual(response.status_code, 404)
        logger.debug("test_delete_video passed")

    # @patch("app.utils.util_auth.validate_api_key")
    # def test_upload_pre_roll(self, mock_validate_api_key):
    #     mock_validate_api_key.return_value = True
    #     with patch("app.routes.creation.pre_roll_video_path", "/path/to/pre_roll.mp4"):
    #         data = {
    #             "file": (bytes("fake video content", encoding="utf-8"), "pre_roll.mp4")
    #         }
    #         response = self.app.post(
    #             "/api/pre_roll", content_type="multipart/form-data", data=data
    #         )
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b"Pre-roll video uploaded", response.data)
    #         logger.debug("test_upload_pre_roll passed")

    # @patch("app.utils.util_auth.validate_api_key")
    # def test_upload_post_roll(self, mock_validate_api_key):
    #     mock_validate_api_key.return_value = True
    #     with patch("app.routes.creation.post_roll_video_path", "/path/to/post_roll.mp4"):
    #         data = {
    #             "file": (bytes("fake video content", encoding="utf-8"), "post_roll.mp4")
    #         }
    #         response = self.app.post(
    #             "/api/post_roll", content_type="multipart/form-data", data=data
    #         )
    #         self.assertEqual(response.status_code, 200)
    #         self.assertIn(b"Post-roll video uploaded", response.data)
    #         logger.debug("test_upload_post_roll passed")

    @patch("app.utils.util_auth.validate_api_key")
    def test_upload_image(self, mock_validate_api_key):
        mock_validate_api_key.return_value = True
        data = {"file": (bytes("fake image content", encoding="utf-8"), "image.jpg")}
        response = self.app.post(
            "/api/upload_image/test_dir",
            content_type="multipart/form-data",
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Image uploaded", response.data)
        logger.debug("test_upload_image passed")

    @patch("requests.get")  # Correctly patch the requests module
    def test_generate_random_data_route(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "segments": [],
            "zoom_pan": False,
            "fade_effect": "fade",
            "audiogram": {},
            "watermark": {},
            "background_music": None,
            "resolution": "1920x1080",
            "thumbnail": False,
            "audio_enhancement": {},
            "dynamic_text": {},
            "template": None,
            "social_preset": None,
            "use_local_files": False,
            "audio_filters": {},
            "segment_audio_effects": [],
            "intro_music": None,
            "outro_music": None,
        }
        response = self.app.get(
            "/api/generate_random_data", headers={"X-API-Key": "your_api_key_here"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("segments", response.json)
        logger.debug("test_generate_random_data_route passed")

    @patch("flask.send_from_directory")
    def test_download_filename(self, mock_send):
        mock_send.return_value = "file content"
        filename = "test_video.mp4"
        response = self.app.get(
            f"/download/{filename}", headers={"X-API-Key": "your_api_key_here"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b"file content")
        logger.debug("test_download_filename passed")


if __name__ == "__main__":
    unittest.main()
