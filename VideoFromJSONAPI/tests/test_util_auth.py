# test_util_auth.py

import unittest
from unittest.mock import MagicMock
from app.utils.util_auth import validate_api_key
from app.config import Config


class TestValidateApiKey(unittest.TestCase):
    def test_validate_api_key_header(self):
        mock_request = MagicMock()
        mock_request.headers.get.return_value = Config.API_KEY
        self.assertTrue(validate_api_key(mock_request))

    def test_validate_api_key_json(self):
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.is_json = True
        mock_request.get_json.return_value = {"api_key": Config.API_KEY}
        self.assertTrue(validate_api_key(mock_request))

    def test_validate_api_key_form(self):
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.is_json = False
        mock_request.form.get.return_value = Config.API_KEY
        self.assertTrue(validate_api_key(mock_request))

    def test_validate_api_key_args(self):
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.is_json = False
        mock_request.form.get.return_value = None
        mock_request.args.get.return_value = Config.API_KEY
        self.assertTrue(validate_api_key(mock_request))

    def test_invalid_api_key(self):
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "invalid_key"
        self.assertFalse(validate_api_key(mock_request))


if __name__ == "__main__":
    unittest.main()
