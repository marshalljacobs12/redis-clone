import time

class EvictionTracker:
    def __init__(self):
        self.access_times = {}   # key -> timestamp
        self.access_counts = {}  # key -> count

    def record_access(self, key):
        self.access_times[key] = time.time()
        self.access_counts[key] = self.access_counts.get(key, 0) + 1
        print(f"[LFU] {key} count = {self.access_counts[key]}")

    def remove(self, key):
        self.access_times.pop(key, None)
        self.access_counts.pop(key, None)

    def lru_key(self):
        return min(self.access_times.items(), key=lambda x: x[1])[0]

    def lfu_key(self):
        return min(self.access_counts.items(), key=lambda x: x[1])[0]
