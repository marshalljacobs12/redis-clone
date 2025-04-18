# datastore/set_store.py

class SetStore:
    def __init__(self):
        self.sets = {}  # key: set

    def sadd(self, key, *values):
        if key not in self.sets:
            self.sets[key] = set()
        added = 0
        for val in values:
            if val not in self.sets[key]:
                self.sets[key].add(val)
                added += 1
        return added

    def srem(self, key, *values):
        if key not in self.sets:
            return 0
        removed = 0
        for val in values:
            if val in self.sets[key]:
                self.sets[key].remove(val)
                removed += 1
        return removed

    def sismember(self, key, value):
        return value in self.sets.get(key, set())

    def smembers(self, key):
        return list(self.sets.get(key, []))
