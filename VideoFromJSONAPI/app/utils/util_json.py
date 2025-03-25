import json
import logging

logger = logging.getLogger(__name__)


def validate_json(json_data):
    try:
        parsed = json.loads(json_data)
        return parsed
    except json.JSONDecodeError as e:
        logger.error(f"JSON validation error: {e}")
        return None
