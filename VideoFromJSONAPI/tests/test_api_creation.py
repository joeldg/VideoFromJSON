import unittest
from unittest.mock import patch
from VideoFromJSONAPI import application
# Import functions from utils.py
from app.utils.utils import validate_api_key

class TestAPICreation(unittest.TestCase):
    def setUp(self):
        self.app = application.test_client()
        self.app.testing = True

    @patch('app.routes.validate_api_key', return_value=True)
    def test_creation_endpoint(self, mock_validate_api_key):
        # Test missing segments field
        response = self.app.post('/api/creation', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Missing 'segments' field", response.data)

    @patch('app.routes.validate_api_key', return_value=True)
    def test_valid_creation_request(self, mock_validate_api_key):
        response = self.app.post('/api/creation', json={'segments': []})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Processing started", response.data)

if __name__ == '__main__':
    unittest.main()
