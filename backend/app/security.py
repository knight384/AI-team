from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
import jwt
from jwt.exceptions import PyJWTError
import hashlib
import secrets

# Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add JTI (JWT ID) to make each token unique
    jti = secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "type": "access", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Add JTI (JWT ID) to make each token unique
    jti = secrets.token_urlsafe(32)
    to_encode.update({"exp": expire, "type": "refresh", "jti": jti})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("type")
        if token_type != expected_type:
            return None
        return payload
    except PyJWTError:
        return None


def generate_token_fingerprint(token: str) -> str:
    """Generate a fingerprint for a refresh token to store in Redis."""
    return hashlib.sha256(token.encode()).hexdigest()


def generate_rate_limit_key(identifier: str, endpoint: str) -> str:
    """Generate a Redis key for rate limiting."""
    return f"rate_limit:{endpoint}:{identifier}"


async def check_rate_limit(redis_client, key: str, max_attempts: int = 5, window_seconds: int = 300) -> bool:
    """
    Check if rate limit is exceeded. Stub implementation for brute-force defense.
    Returns True if request should be allowed, False if rate limited.
    """
    if redis_client is None:
        # If Redis is not available, allow the request
        return True
    
    try:
        current = await redis_client.get(key)
        if current is None:
            await redis_client.setex(key, window_seconds, "1")
            return True
        
        count = int(current)
        if count >= max_attempts:
            return False
        
        await redis_client.incr(key)
        return True
    except Exception:
        # On error, fail open
        return True


async def store_refresh_token_fingerprint(
    redis_client,
    user_id: int,
    fingerprint: str,
    expires_in: int
) -> None:
    """Store refresh token fingerprint in Redis with expiration."""
    if redis_client is None:
        return
    
    try:
        key = f"refresh_token:{user_id}:{fingerprint}"
        await redis_client.setex(key, expires_in, "1")
    except Exception:
        pass


async def verify_refresh_token_fingerprint(
    redis_client,
    user_id: int,
    fingerprint: str
) -> bool:
    """Verify that a refresh token fingerprint exists in Redis."""
    if redis_client is None:
        # If Redis is not available, allow the refresh
        return True
    
    try:
        key = f"refresh_token:{user_id}:{fingerprint}"
        exists = await redis_client.exists(key)
        return bool(exists)
    except Exception:
        # On error, fail open
        return True


async def revoke_refresh_token_fingerprint(
    redis_client,
    user_id: int,
    fingerprint: str
) -> None:
    """Revoke a refresh token by deleting its fingerprint from Redis."""
    if redis_client is None:
        return
    
    try:
        key = f"refresh_token:{user_id}:{fingerprint}"
        await redis_client.delete(key)
    except Exception:
        pass


async def blacklist_token(redis_client, token: str, expires_in: int) -> None:
    """
    Blacklist a token on logout. Placeholder for token revocation.
    In production, store token jti in Redis with expiration.
    """
    if redis_client is None:
        return
    
    try:
        jti = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{jti}"
        await redis_client.setex(key, expires_in, "1")
    except Exception:
        pass


async def is_token_blacklisted(redis_client, token: str) -> bool:
    """Check if a token is blacklisted."""
    if redis_client is None:
        return False
    
    try:
        jti = hashlib.sha256(token.encode()).hexdigest()
        key = f"blacklist:{jti}"
        exists = await redis_client.exists(key)
        return bool(exists)
    except Exception:
        return False
