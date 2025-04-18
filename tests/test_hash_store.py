import unittest
from datastore.hash_store import HashStore

class TestHashStore(unittest.TestCase):
    def setUp(self):
        self.h = HashStore()

    def test_hset_and_hget(self):
        self.assertEqual(self.h.hset("hash1", "field1", "val1"), 1)
        self.assertEqual(self.h.hget("hash1", "field1"), "val1")
        self.assertEqual(self.h.hset("hash1", "field1", "newval"), 0)
        self.assertEqual(self.h.hget("hash1", "field1"), "newval")

    def test_hgetall(self):
        self.h.hset("hash1", "a", "1")
        self.h.hset("hash1", "b", "2")
        result = self.h.hgetall("hash1")
        self.assertEqual(set(result), {"a", "1", "b", "2"})

    def test_hdel(self):
        self.h.hset("hash1", "a", "1")
        self.h.hset("hash1", "b", "2")
        count = self.h.hdel("hash1", "a", "x")
        self.assertEqual(count, 1)
        self.assertIsNone(self.h.hget("hash1", "a"))

if __name__ == "__main__":
    unittest.main()
