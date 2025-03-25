
import os
import hashlib
import shutil
import logging

logger = logging.getLogger(__name__)

def get_file_extension(file_type):
    if file_type == "video":
        return "mp4"
    elif file_type == "image":
        return "jpg"
    elif file_type == "audio":
        return "mp3"
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def get_cached_file(file_id, file_type):
    cache_dir = os.path.join("cache", file_type)
    cache_file_path = os.path.join(cache_dir, file_id)
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "rb") as f:
            return f.read()
    return None

def cache_file(file_id, content, file_type):
    cache_dir = os.path.join("cache", file_type)
    os.makedirs(cache_dir, exist_ok=True)
    cache_file_path = os.path.join(cache_dir, file_id)
    with open(cache_file_path, "wb") as f:
        f.write(content)