# datastore/base_store.py

import time
import sys
from typing import Any, Optional
from datastore.eviction import EvictionTracker
import config

class BaseStore:
    def __init__(self):
        self.store: dict[str, tuple[Any, Optional[float]]] = {}
        self.eviction = EvictionTracker()

    def _is_expired(self, key: str) -> bool:
        if key not in self.store:
            return True
        _, expiry = self.store[key]
        return expiry is not None and time.time() > expiry

    def set(self, key: str, value: Any):
        self._maybe_evict()
        self.store[key] = (value, None)
        self.eviction.record_access(key)

    def get(self, key: str) -> Optional[Any]:
        if self._is_expired(key):
            self.store.pop(key, None)
            self.eviction.remove(key)
            return None
        self.eviction.record_access(key)
        return self.store[key][0]

    def delete(self, key: str) -> bool:
        self.eviction.remove(key)
        return self.store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        if self._is_expired(key):
            self.store.pop(key, None)
            self.eviction.remove(key)
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
            return -2
        _, expiry = self.store[key]
        if expiry is None:
            return -1
        remaining = int(expiry - time.time())
        return remaining if remaining > 0 else -2

    def _maybe_evict(self):
        if self._memory_usage() < config.MAX_MEMORY_BYTES:
            return

        if config.EVICTION_POLICY == "noeviction":
            raise MemoryError("OOM command not allowed when used memory > 'maxmemory'")

        if config.EVICTION_POLICY == "allkeys-lru":
            key_to_evict = self.eviction.lru_key()
        elif config.EVICTION_POLICY == "allkeys-lfu":
            key_to_evict = self.eviction.lfu_key()
        else:
            raise ValueError(f"Unknown eviction policy: {config.EVICTION_POLICY}")

        if key_to_evict:
            print(f"[Eviction] Evicting '{key_to_evict}' due to policy {config.EVICTION_POLICY}")
            self.delete(key_to_evict)

    def _memory_usage(self) -> int:
        total = 0
        for key, (val, _) in self.store.items():
            total += sys.getsizeof(key) + sys.getsizeof(val)
        return total
