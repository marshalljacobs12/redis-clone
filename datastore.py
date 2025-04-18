# redis_clone/datastore.py

import time
from typing import Any, Optional

class DataStore:
    def __init__(self):
        self.store: dict[str, tuple[Any, Optional[float]]] = {}

    def _is_expired(self, key: str) -> bool:
        if key not in self.store:
            return True
        _, expiry = self.store[key]
        return expiry is not None and time.time() > expiry

    def set(self, key: str, value: Any):
        self.store[key] = (value, None)

    def get(self, key: str) -> Optional[Any]:
        if self._is_expired(key):
            self.store.pop(key, None)
            return None
        return self.store[key][0]

    def delete(self, key: str) -> bool:
        return self.store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        if self._is_expired(key):
            self.store.pop(key, None)
            return False
        return key in self.store

    def expire(self, key: str, ttl_seconds: int) -> bool:
        if key not in self.store:
            return False
        value, _ = self.store[key]
        self.store[key] = (value, time.time() + ttl_seconds)
        return True

    def ttl(self, key: str) -> int:
        if key not in self.store:
            return -2  # Redis returns -2 if key doesn't exist
        _, expiry = self.store[key]
        if expiry is None:
            return -1  # Redis returns -1 if no TTL
        remaining = int(expiry - time.time())
        return remaining if remaining > 0 else -2
