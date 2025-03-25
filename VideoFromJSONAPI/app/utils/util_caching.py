import hashlib
import os
import shutil
import logging

from .util_file import get_cached_file, cache_file, get_file_extension

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
