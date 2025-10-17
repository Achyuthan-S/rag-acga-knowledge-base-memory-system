# src/knowledge_base/cache.py
import redis
import json
from typing import Any, Optional, List
from config.settings import get_settings
from loguru import logger


class CacheStore:
    """Redis cache operations"""

    def __init__(self):
        self.settings = get_settings()
        self.redis_client = redis.Redis(
            host=self.settings.redis_host,
            port=self.settings.redis_port,
            decode_responses=True,
        )
        logger.info("Cache store initialized")

    def set(self, key: str, value: Any, expire: int = 3600):
        """Set a key-value pair with expiration"""
        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, expire, serialized_value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")

    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    def delete(self, key: str):
        """Delete a key"""
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False

    def set_list(self, key: str, values: List[Any], expire: int = 3600):
        """Set a list with expiration"""
        try:
            pipe = self.redis_client.pipeline()
            pipe.delete(key)
            for value in values:
                pipe.rpush(key, json.dumps(value))
            pipe.expire(key, expire)
            pipe.execute()
        except Exception as e:
            logger.error(f"Cache set_list error: {e}")

    def get_list(self, key: str) -> List[Any]:
        """Get list by key"""
        try:
            values = self.redis_client.lrange(key, 0, -1)
            return [json.loads(value) for value in values]
        except Exception as e:
            logger.error(f"Cache get_list error: {e}")
            return []

    def clear_pattern(self, pattern: str):
        """Clear keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear_pattern error: {e}")

    def ping(self) -> bool:
        """Test connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Cache ping error: {e}")
            return False
