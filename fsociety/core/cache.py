"""
Caching and performance optimization module for fsociety.

This module provides caching mechanisms to improve performance by
avoiding repeated expensive operations.
"""

from __future__ import annotations

import functools
import hashlib
import json
import logging
import pickle
import time
from pathlib import Path
from typing import Any, Callable, ParamSpec, TypeVar

from fsociety.core.config import INSTALL_DIR


logger = logging.getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")


class Cache:
    """Simple disk-based cache with TTL support."""

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        default_ttl: int = 3600,
    ) -> None:
        """
        Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            default_ttl: Default time-to-live in seconds
        """
        if cache_dir is None:
            cache_dir = Path(INSTALL_DIR) / ".cache"
        else:
            cache_dir = Path(cache_dir)

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _get_cache_path(self, key: str) -> Path:
        """Get path for cache key."""
        # Hash the key to create valid filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found or expired

        Returns:
            Cached value or default
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return default

        try:
            with open(cache_path, "rb") as f:
                data = pickle.load(f)

            # Check if expired
            if data["expires_at"] < time.time():
                cache_path.unlink()
                return default

            logger.debug(f"Cache hit: {key}")
            return data["value"]

        except Exception as e:
            logger.warning(f"Cache read failed: {e}")
            return default

    def set(
        self, key: str, value: Any, ttl: int | None = None
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for default)
        """
        cache_path = self._get_cache_path(key)

        if ttl is None:
            ttl = self.default_ttl

        data = {
            "value": value,
            "expires_at": time.time() + ttl,
        }

        try:
            with open(cache_path, "wb") as f:
                pickle.dump(data, f)

            logger.debug(f"Cache set: {key} (TTL={ttl}s)")

        except Exception as e:
            logger.warning(f"Cache write failed: {e}")

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()
            logger.debug(f"Cache deleted: {key}")

    def clear(self) -> None:
        """Clear all cache entries."""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()
        logger.info("Cache cleared")

    def cleanup_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        removed = 0
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                with open(cache_file, "rb") as f:
                    data = pickle.load(f)

                if data["expires_at"] < time.time():
                    cache_file.unlink()
                    removed += 1

            except Exception as e:
                logger.debug(f"Error checking {cache_file}: {e}")
                # Remove corrupted cache files
                cache_file.unlink()
                removed += 1

        if removed:
            logger.info(f"Removed {removed} expired cache entries")

        return removed


# Global cache instance
_cache = Cache()


def cached(
    ttl: int | None = None,
    key_prefix: str = "",
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Decorator to cache function results.

    Args:
        ttl: Time-to-live in seconds (None for default)
        key_prefix: Prefix for cache keys

    Example:
        >>> @cached(ttl=300)
        ... def expensive_operation(x: int) -> int:
        ...     return x * 2
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # Create cache key from function name and arguments
            key_parts = [key_prefix, func.__name__]

            # Add positional args
            if args:
                key_parts.append(str(args))

            # Add keyword args
            if kwargs:
                key_parts.append(json.dumps(kwargs, sort_keys=True))

            cache_key = ":".join(key_parts)

            # Try to get from cache
            result = _cache.get(cache_key)
            if result is not None:
                return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            _cache.set(cache_key, result, ttl=ttl)

            return result

        # Add cache control methods
        wrapper.cache_clear = lambda: _cache.clear()  # type: ignore
        wrapper.cache_info = lambda: {"cache_dir": str(_cache.cache_dir)}  # type: ignore

        return wrapper

    return decorator


def memoize(func: Callable[P, T]) -> Callable[P, T]:
    """
    Simple in-memory memoization decorator.

    Args:
        func: Function to memoize

    Example:
        >>> @memoize
        ... def fibonacci(n: int) -> int:
        ...     if n < 2:
        ...         return n
        ...     return fibonacci(n-1) + fibonacci(n-2)
    """
    cache: dict[str, T] = {}

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        # Create key from arguments
        key = str((args, tuple(sorted(kwargs.items()))))

        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    wrapper.cache_clear = cache.clear  # type: ignore
    wrapper.cache_info = lambda: {"size": len(cache)}  # type: ignore

    return wrapper
