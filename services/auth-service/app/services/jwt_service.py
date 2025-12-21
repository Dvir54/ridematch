"""
JWT Service - Token creation, validation, and revocation.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import hashlib

from app.config import settings
from app.schemas.token import TokenData
from app.database import redis_client


# Token Creation
def create_access_token(
    user_id: int,
    email: str,
    is_admin: bool = False,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create short-lived JWT access token (default 15 min)."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    
    payload = {
        "sub": str(user_id),
        "email": email,
        "is_admin": is_admin,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create long-lived JWT refresh token (default 7 days)."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.refresh_token_expire_minutes))
    
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# Token Decoding
def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode access token. Returns None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        
        try:
            user_id = int(user_id_str)
        except ValueError:
            return None
        
        if payload.get("type", "access") != "access":
            return None
        
        return TokenData(
            user_id=user_id,
            email=payload.get("email"),
            is_admin=payload.get("is_admin", False),
            token_type="access"
        )
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[int]:
    """Decode refresh token. Returns user_id or None if invalid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        user_id_str = payload.get("sub")
        if user_id_str is None or payload.get("type") != "refresh":
            return None
        
        return int(user_id_str)
    except (JWTError, ValueError):
        return None


# Redis Token Storage
REFRESH_TOKEN_PREFIX = "refresh_token:"


def _get_token_key(token: str) -> str:
    """Generate Redis key from token hash."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return f"{REFRESH_TOKEN_PREFIX}{token_hash}"


def store_refresh_token(token: str, user_id: int) -> bool:
    """Store refresh token in Redis with auto-expiration."""
    try:
        key = _get_token_key(token)
        expiration_seconds = settings.refresh_token_expire_minutes * 60
        redis_client.setex(key, expiration_seconds, str(user_id))
        return True
    except Exception:
        return False


def is_refresh_token_valid(token: str) -> bool:
    """Check if refresh token exists in Redis (not revoked)."""
    try:
        return redis_client.exists(_get_token_key(token)) == 1
    except Exception:
        return False


def revoke_refresh_token(token: str) -> bool:
    """Revoke refresh token by removing from Redis."""
    try:
        redis_client.delete(_get_token_key(token))
        return True
    except Exception:
        return False


def revoke_all_user_tokens(user_id: int) -> int:
    """Revoke all refresh tokens for a user. Returns revoked count."""
    try:
        count = 0
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor=cursor, match=f"{REFRESH_TOKEN_PREFIX}*", count=100)
            for key in keys:
                if redis_client.get(key) == str(user_id):
                    redis_client.delete(key)
                    count += 1
            if cursor == 0:
                break
        return count
    except Exception:
        return 0
