import os
import shutil
import hashlib
import time
import logging
import requests

from config import CACHE_DIR, CACHE_DURATION

logger = logging.getLogger(__name__)


def download_file(url, path):
    """
    Downloads a file from a URL to the given path, with caching for 72 hours.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    # Use a hash of the URL as the cache filename to handle files with the same name from different URLs
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    filename = os.path.basename(url)
    cache_filename = f"{url_hash}_{filename}"
    cache_path = os.path.join(CACHE_DIR, cache_filename)

    # Check if the file exists in the cache and is fresh
    if os.path.exists(cache_path):
        file_age = time.time() - os.path.getmtime(cache_path)
        if file_age < CACHE_DURATION:
            # Copy the cached file to the desired path
            shutil.copy(cache_path, path)
            return
        else:
            # Remove stale cache file
            os.remove(cache_path)

    # Download the file since it's not cached or is stale
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(cache_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        # Copy the file to the desired path
        shutil.copy(cache_path, path)
    else:
        raise Exception(f"Failed to download file: {url}")


def clean_cache():
    """
    Removes files from the cache directory that are older than the cache duration.
    """
    if not os.path.exists(CACHE_DIR):
        return
    for filename in os.listdir(CACHE_DIR):
        file_path = os.path.join(CACHE_DIR, filename)
        if os.path.isfile(file_path):
            file_age = time.time() - os.path.getmtime(file_path)
            if file_age > CACHE_DURATION:
                os.remove(file_path)
