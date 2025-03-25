"""Tests for rate limiting system."""
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from app.config import Config
from app.utils.util_rate_limit import RateLimiter


class TestRateLimiter(unittest.TestCase):
    """Test cases for rate limiting system."""

    def setUp(self):
        """Set up test environment."""
        self.rate_limiter = RateLimiter()
        self.test_api_key = "test_key_123"
        self.test_api_key2 = "test_key_456"
        
        # Reset rate limiter state
        self.rate_limiter._request_times = {}
        self.rate_limiter._credits = {}

    def test_rate_limit_basic(self):
        """Test basic rate limiting functionality."""
        # First 60 requests should be allowed
        for _ in range(60):
            allowed, _ = self.rate_limiter.check_rate_limit(self.test_api_key)
            self.assertTrue(allowed)
        
        # 61st request should be blocked
        allowed, _ = self.rate_limiter.check_rate_limit(self.test_api_key)
        self.assertFalse(allowed)

    def test_rate_limit_expiry(self):
        """Test rate limit expiry after 1 minute."""
        # First request
        allowed, _ = self.rate_limiter.check_rate_limit(self.test_api_key)
        self.assertTrue(allowed)
        
        # Simulate time passing
        with patch('time.time') as mock_time:
            mock_time.return_value = datetime.now().timestamp() + 61  # 61 seconds later
            allowed, _ = self.rate_limiter.check_rate_limit(self.test_api_key)
            self.assertTrue(allowed)

    def test_credits_free_tier(self):
        """Test credit system for free tier."""
        # Set up API key with free tier
        Config.API_KEYS[self.test_api_key] = {
            "name": "Test Key",
            "plan": "free",
            "credits_used": 0,
            "credits_reset": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
        
        # Use all credits
        for _ in range(10):
            has_credits, _ = self.rate_limiter.check_credits(self.test_api_key)
            if has_credits:
                self.rate_limiter.use_credit(self.test_api_key)
        
        # Next request should be blocked
        has_credits, _ = self.rate_limiter.check_credits(self.test_api_key)
        self.assertFalse(has_credits)

    def test_credits_monthly_reset(self):
        """Test credit reset after monthly period."""
        # Set up API key with expired reset date
        Config.API_KEYS[self.test_api_key] = {
            "name": "Test Key",
            "plan": "free",
            "credits_used": 10,
            "credits_reset": (datetime.now() - timedelta(days=1)).isoformat(),
            "is_active": True
        }
        
        # Credits should be reset
        has_credits, _ = self.rate_limiter.check_credits(self.test_api_key)
        self.assertTrue(has_credits)
        
        # Verify credits were reset
        credit_info = self.rate_limiter.get_credit_info(self.test_api_key)
        self.assertEqual(credit_info["credits_used"], 0)
        self.assertEqual(credit_info["credits_remaining"], 10)

    def test_credit_info(self):
        """Test credit information retrieval."""
        # Set up API key
        Config.API_KEYS[self.test_api_key] = {
            "name": "Test Key",
            "plan": "starter",
            "credits_used": 30,
            "credits_reset": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
        
        credit_info = self.rate_limiter.get_credit_info(self.test_api_key)
        self.assertEqual(credit_info["plan"], "Starter")
        self.assertEqual(credit_info["credits_total"], 60)
        self.assertEqual(credit_info["credits_used"], 30)
        self.assertEqual(credit_info["credits_remaining"], 30)

    def test_invalid_api_key(self):
        """Test handling of invalid API key."""
        has_credits, error_msg = self.rate_limiter.check_credits("invalid_key")
        self.assertFalse(has_credits)
        self.assertIn("Invalid API key", error_msg)

    def test_invalid_plan(self):
        """Test handling of invalid plan."""
        Config.API_KEYS[self.test_api_key] = {
            "name": "Test Key",
            "plan": "invalid_plan",
            "credits_used": 0,
            "credits_reset": (datetime.now() + timedelta(days=30)).isoformat(),
            "is_active": True
        }
        
        has_credits, error_msg = self.rate_limiter.check_credits(self.test_api_key)
        self.assertFalse(has_credits)
        self.assertIn("Invalid plan", error_msg)

    def test_concurrent_requests(self):
        """Test handling of concurrent requests."""
        # Simulate concurrent requests
        with patch('threading.Lock') as mock_lock:
            mock_lock.return_value = MagicMock()
            mock_lock.return_value.__enter__.return_value = None
            mock_lock.return_value.__exit__.return_value = None
            
            # First 60 requests should be allowed
            for _ in range(60):
                allowed, _ = self.rate_limiter.check_rate_limit(self.test_api_key)
                self.assertTrue(allowed)
            
            # 61st request should be blocked
            allowed, _ = self.rate_limiter.check_rate_limit(self.test_api_key)
            self.assertFalse(allowed)

    def test_credit_info_all_plans(self):
        """Test credit information for all subscription plans."""
        plans = ["free", "starter", "creator", "pro"]
        expected_credits = {
            "free": 10,
            "starter": 60,
            "creator": 150,
            "pro": 500
        }
        
        for plan in plans:
            Config.API_KEYS[self.test_api_key] = {
                "name": f"Test Key {plan}",
                "plan": plan,
                "credits_used": 0,
                "credits_reset": (datetime.now() + timedelta(days=30)).isoformat(),
                "is_active": True
            }
            
            credit_info = self.rate_limiter.get_credit_info(self.test_api_key)
            self.assertEqual(credit_info["credits_total"], expected_credits[plan])
            self.assertEqual(credit_info["credits_used"], 0)
            self.assertEqual(credit_info["credits_remaining"], expected_credits[plan])


if __name__ == '__main__':
    unittest.main() 