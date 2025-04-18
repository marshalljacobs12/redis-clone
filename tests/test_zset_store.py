import unittest
from datastore.zset_store import ZSetStore

class TestZSetStore(unittest.TestCase):
    def setUp(self):
        self.z = ZSetStore()

    def test_zadd_and_zscore(self):
        self.assertEqual(self.z.zadd("myz", 1.5, "a"), 1)
        self.assertEqual(self.z.zadd("myz", 2.0, "b"), 1)
        self.assertEqual(self.z.zscore("myz", "a"), "1.5")
        self.assertEqual(self.z.zadd("myz", 3.0, "a"), 0)
        self.assertEqual(self.z.zscore("myz", "a"), "3.0")

    def test_zrange(self):
        self.z.zadd("myz", 2, "b")
        self.z.zadd("myz", 1, "a")
        self.z.zadd("myz", 3, "c")
        self.assertEqual(self.z.zrange("myz", 0, 1), ["a", "b"])
        self.assertEqual(self.z.zrange("myz", 0, 10), ["a", "b", "c"])
