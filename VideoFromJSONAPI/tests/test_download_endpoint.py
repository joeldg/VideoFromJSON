
import unittest
from application import app_instance

class TestDownloadEndpoint(unittest.TestCase):

    def setUp(self):
        self.client = app_instance.test_client()

    def test_download_success(self):
        # Test successful download of a video
        response = self.client.get('/download/existing_video.mp4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'video/mp4')

    def test_download_file_not_found(self):
        # Test download with a non-existent filename
        response = self.client.get('/download/non_existent_video.mp4')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()