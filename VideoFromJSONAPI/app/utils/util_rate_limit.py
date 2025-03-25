"""Rate limiting and credit management utility."""
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from app.config import Config

logger = logging.getLogger(__name__)

class RateLimiter:
    """Handles rate limiting and credit management for API keys."""
    
    def __init__(self):
        """Initialize the rate limiter with empty request tracking."""
        self._request_times: Dict[str, list] = {}  # API key -> list of request timestamps
        self._credits: Dict[str, Dict] = {}  # API key -> credit info
        self._lock = threading.Lock()  # Global lock for thread safety
    
    def check_rate_limit(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the request should be rate limited.
        
        Args:
            api_key: The API key to check
            
        Returns:
            Tuple of (allowed, error_message)
        """
        with self._lock:
            current_time = time.time()
            
            # Get or initialize request times for this API key
            if api_key not in self._request_times:
                self._request_times[api_key] = []
            
            # Remove old request times (older than 1 minute)
            self._request_times[api_key] = [
                t for t in self._request_times[api_key]
                if current_time - t < 60  # 1 minute
            ]
            
            # Check if rate limit exceeded (more than 60 requests per minute)
            if len(self._request_times[api_key]) >= 60:
                return False, (
                    "Rate limit exceeded. Please wait before making another request."
                )
            
            # Add current request time
            self._request_times[api_key].append(current_time)
            return True, None
    
    def check_credits(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Check if the API key has available credits.
        
        Args:
            api_key: The API key to check
            
        Returns:
            Tuple of (has_credits, error_message)
        """
        with self._lock:
            # Get key info from config
            key_info = Config.API_KEYS.get(api_key)
            if not key_info:
                return False, "Invalid API key"
            
            # Get plan info
            plan = key_info.get("plan", "free")
            credits_limit = {
                "free": 10,
                "starter": 60,
                "creator": 150,
                "pro": 500
            }.get(plan)
            
            if not credits_limit:
                return False, "Invalid plan"
            
            # Initialize credits if not set
            if "credits_used" not in key_info:
                key_info["credits_used"] = 0
            if "credits_reset" not in key_info:
                key_info["credits_reset"] = (
                    datetime.now() + timedelta(days=30)
                ).isoformat()
            
            # Check if credits need to be reset
            credits_reset = datetime.fromisoformat(key_info["credits_reset"])
            if datetime.now() >= credits_reset:
                key_info["credits_used"] = 0
                key_info["credits_reset"] = (
                    datetime.now() + timedelta(days=30)
                ).isoformat()
            
            # Check if credits are available
            if key_info["credits_used"] >= credits_limit:
                return False, "Monthly credit limit reached"
            
            return True, None
    
    def use_credit(self, api_key: str) -> None:
        """
        Use one credit for the given API key.
        
        Args:
            api_key: The API key to use a credit for
        """
        with self._lock:
            key_info = Config.API_KEYS.get(api_key)
            if key_info:
                key_info["credits_used"] = key_info.get("credits_used", 0) + 1
    
    def get_credit_info(self, api_key: str) -> Optional[Dict]:
        """
        Get credit information for an API key.
        
        Args:
            api_key: The API key to check
            
        Returns:
            Dictionary containing credit information or None if key not found
        """
        with self._lock:
            key_info = Config.API_KEYS.get(api_key)
            if not key_info:
                return None
            
            plan = key_info.get("plan", "free")
            credits_limit = {
                "free": 10,
                "starter": 60,
                "creator": 150,
                "pro": 500
            }.get(plan)
            
            if not credits_limit:
                return None
            
            return {
                "plan": plan.capitalize(),
                "credits_total": credits_limit,
                "credits_used": key_info.get("credits_used", 0),
                "credits_remaining": credits_limit - key_info.get("credits_used", 0),
                "credits_reset": key_info.get("credits_reset"),
                "rate_limit": 60,  # 60 requests per minute
                "features": ["basic"] if plan == "free" else ["basic", "priority_support"]
            }


# Create a singleton instance
rate_limiter = RateLimiter()