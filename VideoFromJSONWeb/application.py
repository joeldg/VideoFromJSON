from flask import Flask
from app import create_app
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

application = create_app()

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5001)
