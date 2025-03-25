import os
import requests
from config import PIXABAY_API_KEY
import logging

logger = logging.getLogger(__name__)

def test_pixabay_images():
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": "nature",
        "image_type": "photo",
        "per_page": 5,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print("Image Results:")
        for hit in data.get("hits", []):
            print(f"ID: {hit['id']}, Tags: {hit['tags']}, URL: {hit['webformatURL']}")
        logger.debug("Pixabay image test completed successfully")
    except requests.RequestException as e:
        print(f"Failed to fetch images: {e}")
        logger.error(f"Failed to fetch images: {e}")

def test_pixabay_video():
    url = "https://pixabay.com/api/videos/"
    params = {"key": PIXABAY_API_KEY, "q": "sunset", "per_page": 5}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        print("\nVideo Results:")
        for hit in data.get("hits", []):
            print(
                f"ID: {hit['id']}, Tags: {hit['tags']}, URL: {hit['videos']['medium']['url']}"
            )
        logger.debug("Pixabay video test completed successfully")
    except requests.RequestException as e:
        print(f"Failed to fetch videos: {e}")
        logger.error(f"Failed to fetch videos: {e}")

def main():
    test_pixabay_images()
    test_pixabay_video()

if __name__ == "__main__":
    main()
