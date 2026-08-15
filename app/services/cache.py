import hashlib
import time
from typing import Any

class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._data: dict[str, tuple[float, Any]] = {}

    def _key(self, value: str) -> str:
        return hashlib.sha256(value.strip().lower().encode()).hexdigest()

    def get(self, value: str):
        key = self._key(value)
        item = self._data.get(key)
        if not item:
            return None
        expires, result = item
        if expires < time.time():
            self._data.pop(key, None)
            return None
        return result

    def set(self, value: str, result: Any):
        self._data[self._key(value)] = (time.time() + self.ttl, result)
