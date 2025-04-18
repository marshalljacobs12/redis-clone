# tests/test_set_store.py

import unittest
from datastore.set_store import SetStore

class TestSetStore(unittest.TestCase):
    def setUp(self):
        self.ss = SetStore()

    def test_sadd_and_smembers(self):
        self.ss.sadd("myset", "a", "b", "c")
        members = set(self.ss.smembers("myset"))
        self.assertEqual(members, {"a", "b", "c"})

    def test_srem(self):
        self.ss.sadd("myset", "x", "y", "z")
        removed = self.ss.srem("myset", "x", "y")
        self.assertEqual(removed, 2)
        self.assertNotIn("x", self.ss.smembers("myset"))

    def test_sismember(self):
        self.ss.sadd("myset", "a")
        self.assertTrue(self.ss.sismember("myset", "a"))
        self.assertFalse(self.ss.sismember("myset", "b"))
