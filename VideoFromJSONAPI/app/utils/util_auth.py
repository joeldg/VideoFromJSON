"""Authentication utility functions."""
import logging
import re

from app.config import Config
from app.utils.util_api_keys import api_key_manager
from flask import request
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


def validate_api_key(req=None) -> bool:
    """
    Validate the API key from the request headers.
    
    Args:
        req: Flask request object (optional)
        
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    if req is None:
        req = request
    
    api_key = req.headers.get(Config.API_KEY_HEADER)
    
    if not api_key:
        logger.warning("No API key provided in request headers")
        return False
    
    # Use the API key manager to validate the key
    is_valid = api_key_manager.validate_key(api_key)
    
    if is_valid:
        # Get key info for logging
        key_info = api_key_manager.get_key_info(api_key)
        if key_info:
            logger.info(
                f"Request authenticated with API key: {api_key[:8]}... "
                f"(Name: {key_info['name']}, Source: {key_info['source']})"
            )
    
    return is_valid


def is_valid_directory_name(name):
    return re.match(r"^[a-z0-9]+$", name) is not None
