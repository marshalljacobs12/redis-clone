import bisect

class ZSetStore:
    def __init__(self):
        # key -> dict[member -> score]
        self.scores = {}
        # key -> sorted list of (score, member)
        self.sorted = {}

    def zadd(self, key: str, score: float, member: str) -> int:
        if key not in self.scores:
            self.scores[key] = {}
            self.sorted[key] = []

        is_new = member not in self.scores[key]
        if not is_new:
            old_score = self.scores[key][member]
            self.sorted[key].remove((old_score, member))

        self.scores[key][member] = score
        bisect.insort(self.sorted[key], (score, member))
        return int(is_new)

    def zscore(self, key: str, member: str) -> str | None:
        return str(self.scores.get(key, {}).get(member))

    def zrange(self, key: str, start: int, stop: int) -> list[str]:
        items = self.sorted.get(key, [])
        return [member for _, member in items[start:stop + 1]]
