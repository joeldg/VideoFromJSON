# app.py
from flask import Flask
import logging
import os
from config import LOG_LEVEL
from routes import routes

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

application = Flask(__name__)
application.register_blueprint(routes)

if __name__ == "__main__":
    if not os.path.exists("static/videos"):
        os.makedirs("static/videos")
    application.debug = True
    application.run(host="0.0.0.0", port=5000)
