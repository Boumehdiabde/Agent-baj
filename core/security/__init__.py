"""Security helpers for API keys and short-lived access tokens."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional


class SecurityManager:
    """In-process security manager; persistent deployments should use a datastore."""

    def __init__(self):
        self.valid_keys = {}
        self.tokens = {}

    def verify_api_key(self, api_key: str) -> bool:
        """Compare against registered keys without timing-sensitive equality."""
        if not isinstance(api_key, str):
            return False
        return any(hmac.compare_digest(api_key, key) for key in self.valid_keys)

    def add_api_key(self, key: str, description: str = "") -> None:
        if not key:
            raise ValueError("API key must not be empty")
        self.valid_keys[key] = {"created": datetime.now(timezone.utc), "description": description}

    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        if expires_in <= 0:
            raise ValueError("expires_in must be positive")
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        self.tokens[token] = {"user_id": user_id, "created": now, "expires": now + timedelta(seconds=expires_in)}
        return token

    def verify_token(self, token: str) -> Optional[str]:
        token_data = self.tokens.get(token)
        if token_data is None:
            return None
        if datetime.now(timezone.utc) >= token_data["expires"]:
            del self.tokens[token]
            return None
        return token_data["user_id"]

    def hash_password(self, password: str) -> str:
        """Hash with PBKDF2 and a random salt (format: algorithm$salt$digest)."""
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310_000).hex()
        return f"pbkdf2_sha256${salt}${digest}"

    def verify_password(self, password: str, hash_value: str) -> bool:
        try:
            algorithm, salt, expected = hash_value.split("$", 2)
            if algorithm != "pbkdf2_sha256":
                return False
            actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 310_000).hex()
            return hmac.compare_digest(actual, expected)
        except (AttributeError, ValueError):
            return False

    def revoke_token(self, token: str) -> bool:
        return self.tokens.pop(token, None) is not None

    def revoke_api_key(self, key: str) -> bool:
        return self.valid_keys.pop(key, None) is not None


security_manager = SecurityManager()
