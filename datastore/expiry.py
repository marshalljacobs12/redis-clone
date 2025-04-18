import time
import asyncio

class ExpiryManager:
    def __init__(self):
        # key -> expiry timestamp
        self.expiries = {}

    def set_expiry(self, key: str, ttl_seconds: int):
        self.expiries[key] = time.time() + ttl_seconds

    def ttl(self, key: str) -> int:
        if key not in self.expiries:
            return -1  # no expiry set
        remaining = int(self.expiries[key] - time.time())
        return remaining if remaining > 0 else -2  # expired

    def is_expired(self, key: str) -> bool:
        return self.ttl(key) == -2

    def remove(self, key: str):
        self.expiries.pop(key, None)

    def keys_to_delete(self) -> list[str]:
        now = time.time()
        return [k for k, exp in self.expiries.items() if exp <= now]

    async def run_gc(self, store_deleter, interval: int = 1):
        while True:
            expired_keys = self.keys_to_delete()
            for key in expired_keys:
                store_deleter(key)
                self.remove(key)
            await asyncio.sleep(interval)
