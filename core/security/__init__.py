"""Security module for authentication and authorization"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
import hashlib


class SecurityManager:
    """Manages API keys and access tokens"""
    
    def __init__(self):
        self.valid_keys = {}
        self.tokens = {}
    
    def verify_api_key(self, api_key: str) -> bool:
        """Verify if API key is valid"""
        # In production, check against database
        return api_key in self.valid_keys
    
    def add_api_key(self, key: str, description: str = "") -> None:
        """Add a new API key"""
        self.valid_keys[key] = {
            "created": datetime.now(),
            "description": description
        }
    
    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate access token"""
        token = secrets.token_urlsafe(32)
        self.tokens[token] = {
            "user_id": user_id,
            "created": datetime.now(),
            "expires": datetime.now() + timedelta(seconds=expires_in)
        }
        return token
    
    def verify_token(self, token: str) -> Optional[str]:
        """Verify token and return user_id if valid"""
        if token not in self.tokens:
            return None
        
        token_data = self.tokens[token]
        if datetime.now() > token_data["expires"]:
            del self.tokens[token]
            return None
        
        return token_data["user_id"]
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, password: str, hash_value: str) -> bool:
        """Verify password against hash"""
        return self.hash_password(password) == hash_value
    
    def revoke_token(self, token: str) -> bool:
        """Revoke a token"""
        if token in self.tokens:
            del self.tokens[token]
            return True
        return False
    
    def revoke_api_key(self, key: str) -> bool:
        """Revoke an API key"""
        if key in self.valid_keys:
            del self.valid_keys[key]
            return True
        return False


# Global security manager instance
security_manager = SecurityManager()
