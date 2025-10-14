"""Advanced caching system with multiple backends."""

from __future__ import annotations

import asyncio
import hashlib
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Generic, TypeVar

import aiofiles
import orjson
from cachetools import LRUCache, TTLCache

from fsociety.core.config import get_config

T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    """Cache entry with metadata."""
    
    key: str
    value: T
    created_at: datetime
    expires_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime | None = None
    
    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def access(self) -> None:
        """Record access."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class CacheBackend(ABC, Generic[T]):
    """Abstract cache backend."""
    
    @abstractmethod
    async def get(self, key: str) -> T | None:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass
    
    @abstractmethod
    async def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        pass


class MemoryCache(CacheBackend[T]):
    """In-memory cache backend using cachetools."""
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600) -> None:
        self.cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)
        self.entries: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> T | None:
        """Get value from cache."""
        async with self._lock:
            if key in self.cache:
                entry = self.entries.get(key)
                if entry and not entry.is_expired():
                    entry.access()
                    self.hits += 1
                    return self.cache[key]
            
            self.misses += 1
            return None
    
    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        """Set value in cache."""
        async with self._lock:
            self.cache[key] = value
            
            expires_at = None
            if ttl:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            
            self.entries[key] = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
            )
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.entries:
                    del self.entries[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            self.entries.clear()
            self.hits = 0
            self.misses = 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        async with self._lock:
            return key in self.cache
    
    async def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "backend": "memory",
            "size": len(self.cache),
            "maxsize": self.cache.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


class FileCache(CacheBackend[T]):
    """File-based cache backend."""
    
    def __init__(self, cache_dir: Path | None = None, ttl: int = 3600) -> None:
        config = get_config()
        self.cache_dir = cache_dir or config.install_dir / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = ttl
        self._lock = asyncio.Lock()
        self.hits = 0
        self.misses = 0
    
    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for key."""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    async def get(self, key: str) -> T | None:
        """Get value from cache."""
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            self.misses += 1
            return None
        
        try:
            async with aiofiles.open(cache_path, "rb") as f:
                data = await f.read()
            
            entry: CacheEntry[T] = pickle.loads(data)
            
            if entry.is_expired():
                await self.delete(key)
                self.misses += 1
                return None
            
            entry.access()
            
            # Update entry
            async with aiofiles.open(cache_path, "wb") as f:
                await f.write(pickle.dumps(entry))
            
            self.hits += 1
            return entry.value
            
        except Exception:
            self.misses += 1
            return None
    
    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        """Set value in cache."""
        cache_path = self._get_cache_path(key)
        
        expires_at = None
        if ttl or self.ttl:
            expires_at = datetime.now() + timedelta(seconds=ttl or self.ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.now(),
            expires_at=expires_at,
        )
        
        async with aiofiles.open(cache_path, "wb") as f:
            await f.write(pickle.dumps(entry))
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_path = self._get_cache_path(key)
        
        if cache_path.exists():
            cache_path.unlink()
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        
        self.hits = 0
        self.misses = 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return self._get_cache_path(key).exists()
    
    async def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.cache"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "backend": "file",
            "cache_dir": str(self.cache_dir),
            "size": len(cache_files),
            "total_size_mb": total_size / 1e6,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


class HybridCache(CacheBackend[T]):
    """Hybrid cache with L1 (memory) and L2 (file) storage."""
    
    def __init__(
        self,
        l1_maxsize: int = 100,
        l1_ttl: int = 300,
        l2_ttl: int = 3600,
        cache_dir: Path | None = None,
    ) -> None:
        self.l1 = MemoryCache[T](maxsize=l1_maxsize, ttl=l1_ttl)
        self.l2 = FileCache[T](cache_dir=cache_dir, ttl=l2_ttl)
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
    
    async def get(self, key: str) -> T | None:
        """Get value from cache (L1 first, then L2)."""
        # Try L1 first
        value = await self.l1.get(key)
        if value is not None:
            self.l1_hits += 1
            return value
        
        # Try L2
        value = await self.l2.get(key)
        if value is not None:
            self.l2_hits += 1
            # Promote to L1
            await self.l1.set(key, value)
            return value
        
        self.misses += 1
        return None
    
    async def set(self, key: str, value: T, ttl: int | None = None) -> None:
        """Set value in both cache levels."""
        await self.l1.set(key, value, ttl)
        await self.l2.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete from both cache levels."""
        l1_deleted = await self.l1.delete(key)
        l2_deleted = await self.l2.delete(key)
        return l1_deleted or l2_deleted
    
    async def clear(self) -> None:
        """Clear both cache levels."""
        await self.l1.clear()
        await self.l2.clear()
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in either cache level."""
        return await self.l1.exists(key) or await self.l2.exists(key)
    
    async def stats(self) -> dict[str, Any]:
        """Get cache statistics for both levels."""
        l1_stats = await self.l1.stats()
        l2_stats = await self.l2.stats()
        
        total_hits = self.l1_hits + self.l2_hits
        total_requests = total_hits + self.misses
        hit_rate = total_hits / total_requests if total_requests > 0 else 0.0
        
        return {
            "backend": "hybrid",
            "l1": l1_stats,
            "l2": l2_stats,
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "misses": self.misses,
            "total_hits": total_hits,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


class CacheManager:
    """Manage multiple cache instances."""
    
    def __init__(self, backend: str = "hybrid") -> None:
        self.config = get_config()
        self.backend_type = backend
        self.cache = self._create_backend()
    
    def _create_backend(self) -> CacheBackend:
        """Create cache backend based on configuration."""
        match self.backend_type:
            case "memory":
                return MemoryCache(
                    maxsize=1000,
                    ttl=self.config.performance.cache_ttl,
                )
            case "file":
                return FileCache(
                    cache_dir=self.config.install_dir / "cache",
                    ttl=self.config.performance.cache_ttl,
                )
            case "hybrid":
                return HybridCache(
                    l1_maxsize=100,
                    l1_ttl=300,
                    l2_ttl=self.config.performance.cache_ttl,
                    cache_dir=self.config.install_dir / "cache",
                )
            case _:
                return MemoryCache()
    
    async def get(self, key: str) -> Any:
        """Get value from cache."""
        if not self.config.performance.enable_caching:
            return None
        return await self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache."""
        if not self.config.performance.enable_caching:
            return
        await self.cache.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        return await self.cache.delete(key)
    
    async def clear(self) -> None:
        """Clear all cache entries."""
        await self.cache.clear()
    
    async def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        return await self.cache.stats()
    
    async def cleanup_expired(self) -> int:
        """Cleanup expired entries (for file cache)."""
        if isinstance(self.cache, FileCache):
            count = 0
            for cache_file in self.cache.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, "rb") as f:
                        entry = pickle.load(f)
                    
                    if entry.is_expired():
                        cache_file.unlink()
                        count += 1
                except Exception:
                    pass
            
            return count
        return 0


# Global cache manager
_cache_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


# Convenience decorators
def cached(ttl: int | None = None, key_prefix: str = ""):
    """Decorator for caching function results."""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Build cache key
            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator