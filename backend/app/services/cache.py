from typing import Optional, Any, Dict
from cachetools import LRUCache
from dataclasses import dataclass

@dataclass
class CacheOptions:
    max_size: int = 500
    ttl: int = 3600

class CacheService:
    def __init__(self, options: Optional[CacheOptions] = None):
        if options is None:
            options = CacheOptions()
        self.cache = LRUCache(maxsize=options.max_size)

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache by key."""
        return self.cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Store a value in cache."""
        self.cache[key] = value

    def has(self, key: str) -> bool:
        """Check if key exists in cache."""
        return key in self.cache

    def delete(self, key: str) -> None:
        """Remove a key from cache."""
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """Return current cache size and max size."""
        return {
            "size": len(self.cache),
            "max_size": self.cache.maxsize
        }
