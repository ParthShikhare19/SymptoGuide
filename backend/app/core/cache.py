"""Caching layer with fallback to in-memory cache"""

from typing import Optional, Any
import json
import hashlib
from functools import lru_cache
from datetime import datetime, timedelta


class InMemoryCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self._cache:
            data, expiry = self._cache[key]
            if datetime.now() < expiry:
                return data
            else:
                del self._cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL in seconds"""
        expiry = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = (value, expiry)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if key in self._cache:
            del self._cache[key]
    
    async def clear(self):
        """Clear all cache"""
        self._cache.clear()


class CacheManager:
    """Cache manager with Redis fallback to in-memory"""
    
    def __init__(self, redis_url: Optional[str] = None, enable_cache: bool = True):
        self.enable_cache = enable_cache
        self.cache = InMemoryCache()
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = json.dumps(kwargs, sort_keys=True)
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enable_cache:
            return None
        return await self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache"""
        if self.enable_cache:
            await self.cache.set(key, value, ttl)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        await self.cache.delete(key)
    
    async def clear(self):
        """Clear all cache"""
        await self.cache.clear()


@lru_cache()
def get_cache_manager() -> CacheManager:
    """Get cached CacheManager instance"""
    from app.core.config import settings
    return CacheManager(
        redis_url=settings.REDIS_URL,
        enable_cache=settings.ENABLE_CACHE
    )
