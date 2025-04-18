# tests/test_datastore.py

import time
import unittest
from datastore import DataStore

class TestDataStore(unittest.TestCase):
    def setUp(self):
        self.ds = DataStore()

    def test_set_get(self):
        self.ds.set("foo", "bar")
        self.assertEqual(self.ds.get("foo"), "bar")

    def test_del(self):
        self.ds.set("foo", "bar")
        self.assertTrue(self.ds.delete("foo"))
        self.assertIsNone(self.ds.get("foo"))

    def test_exists(self):
        self.ds.set("foo", "bar")
        self.assertTrue(self.ds.exists("foo"))
        self.ds.delete("foo")
        self.assertFalse(self.ds.exists("foo"))

    def test_expire_and_ttl(self):
        self.ds.set("foo", "bar")
        self.assertTrue(self.ds.expire("foo", 2))
        ttl1 = self.ds.ttl("foo")
        self.assertTrue(0 <= ttl1 <= 1)
        time.sleep(2.1)
        self.assertIsNone(self.ds.get("foo"))
        self.assertEqual(self.ds.ttl("foo"), -2)

    def test_no_expiry(self):
        self.ds.set("foo", "bar")
        self.assertEqual(self.ds.ttl("foo"), -1)

if __name__ == "__main__":
    unittest.main()
