# tests/test_expiry.py

import unittest
import time
import asyncio

from datastore.expiry import ExpiryManager

class TestExpiryManager(unittest.TestCase):
    def setUp(self):
        self.expiry = ExpiryManager()

    def test_set_and_ttl(self):
        self.expiry.set_expiry("foo", 2)
        ttl = self.expiry.ttl("foo")
        self.assertTrue(0 <= ttl <= 2)

    def test_ttl_no_expiry(self):
        self.assertEqual(self.expiry.ttl("bar"), -1)

    def test_ttl_expired(self):
        self.expiry.set_expiry("foo", 1)
        time.sleep(1.1)
        self.assertEqual(self.expiry.ttl("foo"), -2)

    def test_is_expired(self):
        self.expiry.set_expiry("foo", 1)
        time.sleep(1.1)
        self.assertTrue(self.expiry.is_expired("foo"))

    def test_remove_expiry(self):
        self.expiry.set_expiry("foo", 5)
        self.expiry.remove("foo")
        self.assertEqual(self.expiry.ttl("foo"), -1)

    def test_keys_to_delete(self):
        self.expiry.set_expiry("a", 1)
        self.expiry.set_expiry("b", 2)
        time.sleep(1.1)
        expired = self.expiry.keys_to_delete()
        self.assertIn("a", expired)
        self.assertNotIn("b", expired)

    def test_run_gc_removes_expired_keys(self):
        deleted_keys = []

        def deleter(key):
            deleted_keys.append(key)

        self.expiry.set_expiry("foo", 1)

        async def run_gc_once():
            await self.expiry.run_gc(deleter, interval=0.1)

        async def test():
            task = asyncio.create_task(run_gc_once())
            await asyncio.sleep(1.2)
            task.cancel()
            self.assertIn("foo", deleted_keys)

        asyncio.run(test())


if __name__ == "__main__":
    unittest.main()
