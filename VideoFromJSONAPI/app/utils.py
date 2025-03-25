
from flask import request
from app.config import Config

# ...existing code...

def validate_api_key(api_key, request_obj=None):
    req = request_obj or request
    # ...existing validation logic...