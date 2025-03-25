from flask import Blueprint

allroutes = Blueprint("allroutes", __name__)

from app.endpoints.creation import creation_bp
from app.endpoints.upload import upload_bp
from app.endpoints.status import status_bp
from app.endpoints.management import management_bp
from app.endpoints.download import download_bp
from app.endpoints.health import health_bp
from app.endpoints.temp_videos import temp_videos_bp
from app.endpoints.random_data import random_data_bp

allroutes.register_blueprint(creation_bp)
allroutes.register_blueprint(upload_bp)
allroutes.register_blueprint(status_bp)
allroutes.register_blueprint(management_bp)
allroutes.register_blueprint(download_bp)
allroutes.register_blueprint(health_bp)
allroutes.register_blueprint(temp_videos_bp)
allroutes.register_blueprint(random_data_bp)
