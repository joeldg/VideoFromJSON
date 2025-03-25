"""API key management utility."""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.config import Config
from supabase import Client, create_client

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages API keys with support for local config and Supabase."""
    
    def __init__(self):
        """Initialize the API key manager."""
        self.local_keys = Config.API_KEYS
        self.supabase: Optional[Client] = None
        self._init_supabase()
    
    def _init_supabase(self) -> None:
        """Initialize Supabase client if credentials are configured."""
        if Config.SUPABASE_URL and Config.SUPABASE_KEY:
            try:
                self.supabase = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self.supabase = None
    
    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key by checking local config and Supabase.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            bool: True if the key is valid, False otherwise
        """
        # First check local config
        if api_key in self.local_keys:
            logger.debug(f"API key validated from local config: {api_key[:8]}...")
            return True
        
        # If Supabase is configured, check there
        if self.supabase:
            try:
                response = self.supabase.table('api_keys').select('*').eq('key', api_key).execute()
                if response.data:
                    key_data = response.data[0]
                    # Check if key is active and not expired
                    if (key_data.get('is_active', False) and 
                        (not key_data.get('expires_at') or 
                         datetime.fromisoformat(key_data['expires_at']) > datetime.now())):
                        logger.debug(f"API key validated from Supabase: {api_key[:8]}...")
                        return True
            except Exception as e:
                logger.error(f"Error checking API key in Supabase: {e}")
        
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        return False
    
    def get_key_info(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Get information about an API key.
        
        Args:
            api_key: The API key to look up
            
        Returns:
            Optional[Dict[str, Any]]: Key information if found, None otherwise
        """
        # Check local config first
        if api_key in self.local_keys:
            return {
                'name': self.local_keys[api_key].get('name', 'Local Key'),
                'created_at': self.local_keys[api_key].get('created_at', datetime.now().isoformat()),
                'expires_at': self.local_keys[api_key].get('expires_at'),
                'is_active': True,
                'source': 'local'
            }
        
        # Check Supabase if configured
        if self.supabase:
            try:
                response = self.supabase.table('api_keys').select('*').eq('key', api_key).execute()
                if response.data:
                    key_data = response.data[0]
                    return {
                        'name': key_data.get('name', 'Supabase Key'),
                        'created_at': key_data.get('created_at'),
                        'expires_at': key_data.get('expires_at'),
                        'is_active': key_data.get('is_active', False),
                        'source': 'supabase'
                    }
            except Exception as e:
                logger.error(f"Error getting key info from Supabase: {e}")
        
        return None
    
    def create_key(self, name: str, expires_in_days: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new API key.
        
        Args:
            name: Name/description for the key
            expires_in_days: Number of days until the key expires (optional)
            
        Returns:
            Optional[Dict[str, Any]]: Created key information if successful, None otherwise
        """
        import secrets

        # Generate a secure random key
        api_key = secrets.token_urlsafe(32)
        
        # Calculate expiration date if specified
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.now() + timedelta(days=expires_in_days)).isoformat()
        
        # If Supabase is configured, store there
        if self.supabase:
            try:
                response = self.supabase.table('api_keys').insert({
                    'key': api_key,
                    'name': name,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': expires_at,
                    'is_active': True
                }).execute()
                
                if response.data:
                    return {
                        'key': api_key,
                        'name': name,
                        'created_at': response.data[0]['created_at'],
                        'expires_at': response.data[0]['expires_at'],
                        'is_active': True
                    }
            except Exception as e:
                logger.error(f"Error creating API key in Supabase: {e}")
        
        # Fallback to local config if Supabase fails or is not configured
        self.local_keys[api_key] = {
            'name': name,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at,
            'is_active': True
        }
        
        return {
            'key': api_key,
            'name': name,
            'created_at': self.local_keys[api_key]['created_at'],
            'expires_at': self.local_keys[api_key]['expires_at'],
            'is_active': True
        }
    
    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: The API key to revoke
            
        Returns:
            bool: True if the key was revoked, False otherwise
        """
        # Check local config first
        if api_key in self.local_keys:
            del self.local_keys[api_key]
            logger.info(f"API key revoked from local config: {api_key[:8]}...")
            return True
        
        # Check Supabase if configured
        if self.supabase:
            try:
                response = self.supabase.table('api_keys').update({
                    'is_active': False,
                    'revoked_at': datetime.now().isoformat()
                }).eq('key', api_key).execute()
                
                if response.data:
                    logger.info(f"API key revoked in Supabase: {api_key[:8]}...")
                    return True
            except Exception as e:
                logger.error(f"Error revoking API key in Supabase: {e}")
        
        return False

# Create a singleton instance
api_key_manager = APIKeyManager() 