# datastore/hash_store.py

class HashStore:
    def __init__(self):
        self.hashes = {}

    def hset(self, key: str, field: str, value: str) -> int:
        if key not in self.hashes:
            self.hashes[key] = {}
        is_new = field not in self.hashes[key]
        self.hashes[key][field] = value
        return 1 if is_new else 0

    def hget(self, key: str, field: str) -> str | None:
        return self.hashes.get(key, {}).get(field)

    def hgetall(self, key: str) -> list[str]:
        h = self.hashes.get(key, {})
        result = []
        for field, value in h.items():
            result.extend([field, value])
        return result

    def hdel(self, key: str, *fields: str) -> int:
        if key not in self.hashes:
            return 0
        count = 0
        for field in fields:
            if field in self.hashes[key]:
                del self.hashes[key][field]
                count += 1
        if not self.hashes[key]:
            del self.hashes[key]
        return count
