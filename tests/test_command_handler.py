# tests/test_command_handler.py

import time
import unittest
from datastore import DataStore
from command_handler import CommandHandler

class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        self.store = DataStore()
        self.handler = CommandHandler(self.store)

    def test_ping(self):
        res = self.handler.handle(["PING"])
        self.assertEqual(res, "+PONG\r\n")

    def test_set_and_get(self):
        self.assertEqual(self.handler.handle(["SET", "foo", "bar"]), "+OK\r\n")
        self.assertEqual(self.handler.handle(["GET", "foo"]), "$3\r\nbar\r\n")

    def test_get_missing_key(self):
        self.assertEqual(self.handler.handle(["GET", "missing"]), "$-1\r\n")

    def test_set_invalid_args(self):
        self.assertIn("-ERR", self.handler.handle(["SET", "foo"]))

    def test_get_invalid_args(self):
        self.assertIn("-ERR", self.handler.handle(["GET"]))

    def test_del(self):
        self.handler.handle(["SET", "foo", "bar"])
        self.assertEqual(self.handler.handle(["DEL", "foo"]), ":1\r\n")
        self.assertEqual(self.handler.handle(["DEL", "foo"]), ":0\r\n")

    def test_exists(self):
        self.assertEqual(self.handler.handle(["EXISTS", "foo"]), ":0\r\n")
        self.handler.handle(["SET", "foo", "bar"])
        self.assertEqual(self.handler.handle(["EXISTS", "foo"]), ":1\r\n")

    def test_expire_and_ttl(self):
        self.handler.handle(["SET", "foo", "bar"])
        self.assertEqual(self.handler.handle(["EXPIRE", "foo", "2"]), ":1\r\n")
        ttl = int(self.handler.handle(["TTL", "foo"]).strip()[1:])
        self.assertTrue(0 <= ttl <= 1)
        time.sleep(2.1)
        self.assertEqual(self.handler.handle(["TTL", "foo"]), ":-2\r\n")

    def test_expire_invalid_key(self):
        self.assertEqual(self.handler.handle(["EXPIRE", "missing", "10"]), ":0\r\n")

    def test_ttl_no_expiry(self):
        self.handler.handle(["SET", "foo", "bar"])
        self.assertEqual(self.handler.handle(["TTL", "foo"]), ":-1\r\n")

    def test_unknown_command(self):
        self.assertIn("-ERR", self.handler.handle(["FOOBAR"]))

    def test_empty_command(self):
        self.assertIn("-ERR", self.handler.handle([]))

if __name__ == "__main__":
    unittest.main()
