import os
import shutil
import hashlib
import subprocess
import logging
import requests
from .helpers import get_file_extension, get_cached_file, cache_file

logger = logging.getLogger(__name__)


def download_file(url, file_type):
    """
    Downloads a file from a URL with caching.

    Args:
        url (str): URL of the file to download.
        file_type (str): Type of the file ('video', 'image', 'audio').

    Returns:
        str: Path to the downloaded file.
    """
    file_id = hashlib.md5(url.encode()).hexdigest()
    cached_data = get_cached_file(file_id, file_type)
    if cached_data:
        file_path = os.path.join(
            "downloads", file_type, f"{file_id}.{get_file_extension(file_type)}"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(cached_data)
        return file_path

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        file_extension = get_file_extension(file_type)
        file_path = os.path.join("downloads", file_type, f"{file_id}.{file_extension}")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        cache_file(file_id, response.content, file_type)
        return file_path
    else:
        logger.error(f"Failed to download {file_type} from {url}")
        return None


def is_valid_directory_name(directory_name):
    """
    Check if the directory name is valid and if the directory exists.

    Args:
        directory_name (str): The name of the directory to check.

    Returns:
        bool: True if the directory name is valid and the directory exists, False otherwise.
    """
    if not directory_name.isalnum():
        return False

    directory_path = os.path.join("uploads", directory_name)

    try:
        if not os.path.exists(directory_path):
            return False
    except Exception as e:
        # Log the error if needed
        print(f"Error checking directory existence: {e}")
        return False

    return True


def remove_temp_files(path):
    if os.path.exists(path):
        subprocess.run(["rm", "-f", path], check=True)
        logger.debug(f"Removed temporary files at {path}")
    else:
        logger.debug(f"No temporary files to remove at {path}")
