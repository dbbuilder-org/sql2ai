"""Redis caching implementation."""

from typing import Any, Optional, List, TypeVar, Generic
from datetime import timedelta
import json
import hashlib
from pydantic import BaseModel
import structlog

from sql2ai_shared.tenancy.context import get_current_tenant

logger = structlog.get_logger()

T = TypeVar("T")


class RedisConfig(BaseModel):
    """Redis connection configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    max_connections: int = 50
    key_prefix: str = "sql2ai"
    default_ttl_seconds: int = 3600  # 1 hour


class CacheEntry(BaseModel, Generic[T]):
    """Cached entry with metadata."""

    value: Any
    created_at: float
    ttl_seconds: int
    tenant_id: Optional[str] = None
    tags: List[str] = []


class RedisCache:
    """Redis cache with tenant isolation and tagging support.

    Features:
    - Tenant-isolated namespaces
    - Tag-based invalidation
    - Automatic serialization
    - TTL management
    - Batch operations
    """

    def __init__(self, config: RedisConfig):
        self.config = config
        self._client = None
        self._connected = False

    async def connect(self) -> None:
        """Connect to Redis."""
        import redis.asyncio as redis

        self._client = redis.Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
            ssl=self.config.ssl,
            socket_timeout=self.config.socket_timeout,
            socket_connect_timeout=self.config.socket_connect_timeout,
            max_connections=self.config.max_connections,
            decode_responses=True,
        )
        self._connected = True
        logger.info(
            "redis_connected",
            host=self.config.host,
            port=self.config.port,
        )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
            self._connected = False
            logger.info("redis_disconnected")

    def _build_key(
        self, key: str, tenant_id: Optional[str] = None
    ) -> str:
        """Build a namespaced cache key."""
        if tenant_id is None:
            tenant = get_current_tenant()
            tenant_id = tenant.id if tenant else "global"

        return f"{self.config.key_prefix}:{tenant_id}:{key}"

    def _tag_key(self, tag: str, tenant_id: Optional[str] = None) -> str:
        """Build a tag set key."""
        if tenant_id is None:
            tenant = get_current_tenant()
            tenant_id = tenant.id if tenant else "global"

        return f"{self.config.key_prefix}:{tenant_id}:_tag:{tag}"

    async def get(
        self,
        key: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[Any]:
        """Get a value from cache."""
        full_key = self._build_key(key, tenant_id)

        try:
            data = await self._client.get(full_key)
            if data is None:
                return None

            entry = CacheEntry(**json.loads(data))
            return entry.value

        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None,
        tags: Optional[List[str]] = None,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Set a value in cache."""
        import time

        full_key = self._build_key(key, tenant_id)
        ttl_seconds = (
            int(ttl.total_seconds())
            if ttl
            else self.config.default_ttl_seconds
        )

        if tenant_id is None:
            tenant = get_current_tenant()
            tenant_id = tenant.id if tenant else "global"

        entry = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl_seconds=ttl_seconds,
            tenant_id=tenant_id,
            tags=tags or [],
        )

        try:
            # Set the value
            await self._client.setex(
                full_key,
                ttl_seconds,
                json.dumps(entry.model_dump()),
            )

            # Add to tag sets for invalidation
            if tags:
                for tag in tags:
                    tag_key = self._tag_key(tag, tenant_id)
                    await self._client.sadd(tag_key, full_key)
                    await self._client.expire(tag_key, ttl_seconds)

            return True

        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))
            return False

    async def delete(
        self,
        key: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Delete a value from cache."""
        full_key = self._build_key(key, tenant_id)

        try:
            result = await self._client.delete(full_key)
            return result > 0
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))
            return False

    async def invalidate_by_tag(
        self,
        tag: str,
        tenant_id: Optional[str] = None,
    ) -> int:
        """Invalidate all cache entries with a specific tag."""
        tag_key = self._tag_key(tag, tenant_id)

        try:
            # Get all keys with this tag
            keys = await self._client.smembers(tag_key)
            if not keys:
                return 0

            # Delete all keys
            deleted = await self._client.delete(*keys)

            # Remove the tag set
            await self._client.delete(tag_key)

            logger.info(
                "cache_invalidated_by_tag",
                tag=tag,
                count=deleted,
            )

            return deleted

        except Exception as e:
            logger.warning("cache_invalidate_error", tag=tag, error=str(e))
            return 0

    async def invalidate_pattern(
        self,
        pattern: str,
        tenant_id: Optional[str] = None,
    ) -> int:
        """Invalidate cache entries matching a pattern."""
        full_pattern = self._build_key(pattern, tenant_id)

        try:
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor,
                    match=full_pattern,
                    count=100,
                )

                if keys:
                    deleted += await self._client.delete(*keys)

                if cursor == 0:
                    break

            logger.info(
                "cache_invalidated_by_pattern",
                pattern=pattern,
                count=deleted,
            )

            return deleted

        except Exception as e:
            logger.warning(
                "cache_invalidate_pattern_error",
                pattern=pattern,
                error=str(e),
            )
            return 0

    async def get_many(
        self,
        keys: List[str],
        tenant_id: Optional[str] = None,
    ) -> dict:
        """Get multiple values from cache."""
        full_keys = [self._build_key(k, tenant_id) for k in keys]

        try:
            values = await self._client.mget(full_keys)
            result = {}

            for key, data in zip(keys, values):
                if data is not None:
                    entry = CacheEntry(**json.loads(data))
                    result[key] = entry.value

            return result

        except Exception as e:
            logger.warning("cache_get_many_error", error=str(e))
            return {}

    async def exists(
        self,
        key: str,
        tenant_id: Optional[str] = None,
    ) -> bool:
        """Check if a key exists in cache."""
        full_key = self._build_key(key, tenant_id)
        try:
            return await self._client.exists(full_key) > 0
        except Exception as e:
            logger.warning("cache_exists_error", key=key, error=str(e))
            return False

    async def ttl(
        self,
        key: str,
        tenant_id: Optional[str] = None,
    ) -> int:
        """Get remaining TTL for a key in seconds."""
        full_key = self._build_key(key, tenant_id)
        try:
            return await self._client.ttl(full_key)
        except Exception as e:
            logger.warning("cache_ttl_error", key=key, error=str(e))
            return -1

    async def clear_tenant(self, tenant_id: str) -> int:
        """Clear all cache entries for a tenant."""
        pattern = f"{self.config.key_prefix}:{tenant_id}:*"

        try:
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100,
                )

                if keys:
                    deleted += await self._client.delete(*keys)

                if cursor == 0:
                    break

            logger.info(
                "cache_tenant_cleared",
                tenant_id=tenant_id,
                count=deleted,
            )

            return deleted

        except Exception as e:
            logger.warning(
                "cache_clear_tenant_error",
                tenant_id=tenant_id,
                error=str(e),
            )
            return 0


# Global cache instance
_cache: Optional[RedisCache] = None


def get_cache() -> RedisCache:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        raise RuntimeError("Cache not initialized")
    return _cache


async def create_cache(config: RedisConfig) -> RedisCache:
    """Create and initialize the global cache."""
    global _cache

    _cache = RedisCache(config)
    await _cache.connect()
    return _cache
