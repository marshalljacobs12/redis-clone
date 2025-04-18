# datastore/list_store.py

from collections import deque

class ListStore:
    def __init__(self):
        self.lists = {}  # key: deque

    def lpush(self, key, *values):
        if key not in self.lists:
            self.lists[key] = deque()
        for val in values:
            self.lists[key].appendleft(val)
        return len(self.lists[key])

    def rpush(self, key, *values):
        if key not in self.lists:
            self.lists[key] = deque()
        for val in values:
            self.lists[key].append(val)
        return len(self.lists[key])

    def lpop(self, key):
        if key in self.lists and self.lists[key]:
            return self.lists[key].popleft()
        return None

    def rpop(self, key):
        if key in self.lists and self.lists[key]:
            return self.lists[key].pop()
        return None

    def lrange(self, key, start, end):
        if key not in self.lists:
            return []
        lst = self.lists[key]
        return list(lst)[start:end+1]

    def llen(self, key):
        return len(self.lists.get(key, []))
