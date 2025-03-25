import os
import shutil
import hashlib
import time
import logging
from .utils import clean_cache

logger = logging.getLogger(__name__)

CACHE_DIR = "cache"  # Directory to store cached files
CACHE_DURATION = 72 * 3600  # Cache duration in seconds (72 hours)


def cache_file(file_id, file_data, file_type):
    """
    Caches a file with a specific ID and type.

    Args:
        file_id (str): Unique identifier for the file.
        file_data (bytes): Binary data of the file.
        file_type (str): Type of the file ('video', 'image', 'audio').
    """
    try:
        file_extension = get_file_extension(file_type)
        filename = f"{hashlib.md5(file_id.encode()).hexdigest()}.{file_extension}"
        file_path = os.path.join(CACHE_DIR, file_type, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file_data)
        logger.debug(f"Cached {file_type} file with ID {file_id} at {file_path}")
        clean_cache()
    except Exception as e:
        logger.error(f"Error caching {file_type} file {file_id}: {e}")


def get_cached_file(file_id, file_type):
    """
    Retrieves a cached file by its ID and type.

    Args:
        file_id (str): Unique identifier for the file.
        file_type (str): Type of the file ('video', 'image', 'audio').

    Returns:
        bytes or None: Binary data of the file if cached, else None.
    """
    try:
        file_extension = get_file_extension(file_type)
        filename = f"{hashlib.md5(file_id.encode()).hexdigest()}.{file_extension}"
        file_path = os.path.join(CACHE_DIR, file_type, filename)
        if os.path.exists(file_path):
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age < CACHE_DURATION:
                with open(file_path, "rb") as f:
                    logger.debug(
                        f"Retrieved cached {file_type} file with ID {file_id} from {file_path}"
                    )
                    return f.read()
            else:
                os.remove(file_path)
                logger.debug(f"Removed stale cached {file_type} file with ID {file_id}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving cached {file_type} file {file_id}: {e}")
        return None


def get_file_extension(file_type):
    """
    Returns the file extension based on the file type.

    Args:
        file_type (str): Type of the file.

    Returns:
        str: File extension.
    """
    extensions = {"video": "mp4", "image": "jpg", "audio": "mp3"}
    return extensions.get(file_type, "dat")
