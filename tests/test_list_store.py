# tests/test_list_store.py

import unittest
from datastore.list_store import ListStore

class TestListStore(unittest.TestCase):
    def setUp(self):
        self.ls = ListStore()

    def test_lpush_rpush_and_lrange(self):
        self.ls.lpush("mylist", "c", "b", "a")
        self.ls.rpush("mylist", "d", "e")
        self.assertEqual(self.ls.lrange("mylist", 0, 10), ["a", "b", "c", "d", "e"])

    def test_lpop_and_rpop(self):
        self.ls.rpush("mylist", "one", "two", "three")
        self.assertEqual(self.ls.lpop("mylist"), "one")
        self.assertEqual(self.ls.rpop("mylist"), "three")

    def test_llen(self):
        self.ls.lpush("mylist", "a", "b", "c")
        self.assertEqual(self.ls.llen("mylist"), 3)
