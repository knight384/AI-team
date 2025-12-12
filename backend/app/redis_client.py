from typing import Optional
import os

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None


class RedisClient:
    """Redis client wrapper with graceful fallback."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.enabled = False
        
    async def connect(self):
        """Connect to Redis if available."""
        if not REDIS_AVAILABLE:
            return
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            await self.client.ping()
            self.enabled = True
        except Exception:
            self.client = None
            self.enabled = False
    
    async def close(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.enabled or not self.client:
            return None
        try:
            return await self.client.get(key)
        except Exception:
            return None
    
    async def setex(self, key: str, seconds: int, value: str) -> None:
        """Set value in Redis with expiration."""
        if not self.enabled or not self.client:
            return
        try:
            await self.client.setex(key, seconds, value)
        except Exception:
            pass
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        if not self.enabled or not self.client:
            return False
        try:
            result = await self.client.exists(key)
            return bool(result)
        except Exception:
            return False
    
    async def delete(self, key: str) -> None:
        """Delete key from Redis."""
        if not self.enabled or not self.client:
            return
        try:
            await self.client.delete(key)
        except Exception:
            pass
    
    async def incr(self, key: str) -> None:
        """Increment value in Redis."""
        if not self.enabled or not self.client:
            return
        try:
            await self.client.incr(key)
        except Exception:
            pass


# Global Redis client instance
redis_client = RedisClient()
