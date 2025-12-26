"""Caching decorators for easy cache integration."""

from typing import Any, Callable, List, Optional, TypeVar, Union
from datetime import timedelta
from functools import wraps
import hashlib
import json
import inspect
import structlog

logger = structlog.get_logger()

F = TypeVar("F", bound=Callable[..., Any])


def _generate_cache_key(
    prefix: str,
    func: Callable,
    args: tuple,
    kwargs: dict,
    key_builder: Optional[Callable] = None,
) -> str:
    """Generate a cache key from function arguments."""
    if key_builder:
        return f"{prefix}:{key_builder(*args, **kwargs)}"

    # Get function signature
    sig = inspect.signature(func)
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()

    # Build key from parameters
    key_parts = [prefix, func.__module__, func.__name__]

    for param_name, param_value in bound.arguments.items():
        # Skip 'self' and 'cls' parameters
        if param_name in ("self", "cls"):
            continue

        # Convert value to string representation
        if hasattr(param_value, "model_dump"):
            # Pydantic model
            value_str = json.dumps(param_value.model_dump(), sort_keys=True)
        elif isinstance(param_value, (dict, list)):
            value_str = json.dumps(param_value, sort_keys=True)
        else:
            value_str = str(param_value)

        key_parts.append(f"{param_name}:{value_str}")

    # Hash for shorter keys
    key_string = ":".join(key_parts)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]

    return f"{prefix}:{func.__name__}:{key_hash}"


def cached(
    prefix: str = "cache",
    ttl: Optional[Union[int, timedelta]] = None,
    tags: Optional[List[str]] = None,
    key_builder: Optional[Callable[..., str]] = None,
    unless: Optional[Callable[..., bool]] = None,
) -> Callable[[F], F]:
    """Cache decorator for functions.

    Args:
        prefix: Cache key prefix
        ttl: Time to live (seconds or timedelta)
        tags: Tags for group invalidation
        key_builder: Custom function to build cache key
        unless: Function that returns True to skip caching

    Usage:
        @cached(prefix="users", ttl=300, tags=["user"])
        async def get_user(user_id: str) -> User:
            return await db.get_user(user_id)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from sql2ai_shared.caching.redis import get_cache

            # Check if we should skip caching
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)

            cache = get_cache()
            cache_key = _generate_cache_key(prefix, func, args, kwargs, key_builder)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug("cache_hit", key=cache_key)
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Convert ttl to timedelta
            cache_ttl = None
            if ttl is not None:
                cache_ttl = ttl if isinstance(ttl, timedelta) else timedelta(seconds=ttl)

            # Store in cache
            await cache.set(
                cache_key,
                result,
                ttl=cache_ttl,
                tags=tags,
            )
            logger.debug("cache_set", key=cache_key)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import asyncio

            return asyncio.get_event_loop().run_until_complete(
                async_wrapper(*args, **kwargs)
            )

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def cache_aside(
    prefix: str = "cache",
    ttl: Optional[Union[int, timedelta]] = None,
    tags: Optional[List[str]] = None,
    loader: Optional[Callable] = None,
) -> Callable[[F], F]:
    """Cache-aside pattern decorator.

    Unlike @cached, this explicitly separates cache lookup from data loading.

    Args:
        prefix: Cache key prefix
        ttl: Time to live
        tags: Tags for invalidation
        loader: Optional data loader function

    Usage:
        @cache_aside(prefix="orders", ttl=600)
        async def get_order(order_id: str) -> Order:
            # This only runs on cache miss
            return await db.get_order(order_id)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from sql2ai_shared.caching.redis import get_cache

            cache = get_cache()
            cache_key = _generate_cache_key(prefix, func, args, kwargs)

            # Try cache first
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.debug("cache_aside_hit", key=cache_key)
                return cached_value

            # Use loader or decorated function
            load_func = loader or func
            result = await load_func(*args, **kwargs)

            # Write through to cache
            cache_ttl = None
            if ttl is not None:
                cache_ttl = ttl if isinstance(ttl, timedelta) else timedelta(seconds=ttl)

            await cache.set(
                cache_key,
                result,
                ttl=cache_ttl,
                tags=tags,
            )
            logger.debug("cache_aside_set", key=cache_key)

            return result

        return wrapper

    return decorator


def invalidate(
    prefix: str = "cache",
    tags: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    key_builder: Optional[Callable[..., str]] = None,
) -> Callable[[F], F]:
    """Decorator to invalidate cache after function execution.

    Args:
        prefix: Cache key prefix
        tags: Tags to invalidate
        pattern: Pattern to invalidate
        key_builder: Custom function to build cache key

    Usage:
        @invalidate(tags=["user", "orders"])
        async def update_user(user_id: str, data: dict):
            return await db.update_user(user_id, data)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from sql2ai_shared.caching.redis import get_cache

            # Execute the function first
            result = await func(*args, **kwargs)

            cache = get_cache()

            # Invalidate by tags
            if tags:
                for tag in tags:
                    await cache.invalidate_by_tag(tag)
                    logger.debug("cache_invalidated_tag", tag=tag)

            # Invalidate by pattern
            if pattern:
                await cache.invalidate_pattern(pattern)
                logger.debug("cache_invalidated_pattern", pattern=pattern)

            # Invalidate specific key
            if key_builder:
                cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
                await cache.delete(cache_key)
                logger.debug("cache_invalidated_key", key=cache_key)

            return result

        return wrapper

    return decorator


class CacheManager:
    """Helper class for managing cache operations."""

    def __init__(self, prefix: str = "cache"):
        self.prefix = prefix

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Any],
        ttl: Optional[Union[int, timedelta]] = None,
        tags: Optional[List[str]] = None,
    ) -> Any:
        """Get from cache or set using factory function."""
        from sql2ai_shared.caching.redis import get_cache

        cache = get_cache()
        full_key = f"{self.prefix}:{key}"

        # Try cache
        value = await cache.get(full_key)
        if value is not None:
            return value

        # Generate value
        if inspect.iscoroutinefunction(factory):
            value = await factory()
        else:
            value = factory()

        # Store in cache
        cache_ttl = None
        if ttl is not None:
            cache_ttl = ttl if isinstance(ttl, timedelta) else timedelta(seconds=ttl)

        await cache.set(full_key, value, ttl=cache_ttl, tags=tags)

        return value

    async def invalidate(
        self,
        key: Optional[str] = None,
        tag: Optional[str] = None,
        pattern: Optional[str] = None,
    ) -> int:
        """Invalidate cache entries."""
        from sql2ai_shared.caching.redis import get_cache

        cache = get_cache()
        count = 0

        if key:
            full_key = f"{self.prefix}:{key}"
            if await cache.delete(full_key):
                count += 1

        if tag:
            count += await cache.invalidate_by_tag(tag)

        if pattern:
            full_pattern = f"{self.prefix}:{pattern}"
            count += await cache.invalidate_pattern(full_pattern)

        return count
