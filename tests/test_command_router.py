# tests/test_command_router.py

import time
import unittest
from server.command_router import CommandHandler

class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        self.handler = CommandHandler()

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

    # --- LIST COMMANDS ---
    def test_lpush_rpush_lrange(self):
        self.assertEqual(self.handler.handle(["LPUSH", "mylist", "c", "b", "a"]), ":3\r\n")
        self.assertEqual(self.handler.handle(["RPUSH", "mylist", "d", "e"]), ":5\r\n")
        result = self.handler.handle(["LRANGE", "mylist", "0", "4"])
        self.assertEqual(result, "*5\r\n$1\r\na\r\n$1\r\nb\r\n$1\r\nc\r\n$1\r\nd\r\n$1\r\ne\r\n")
    
    def test_lpop_rpop(self):
        self.handler.handle(["RPUSH", "mylist", "one", "two", "three"])
        self.assertEqual(self.handler.handle(["LPOP", "mylist"]), "$3\r\none\r\n")
        self.assertEqual(self.handler.handle(["RPOP", "mylist"]), "$5\r\nthree\r\n")

    def test_llen(self):
        self.handler.handle(["RPUSH", "mylist", "x", "y"])
        self.assertEqual(self.handler.handle(["LLEN", "mylist"]), ":2\r\n")

    def test_lrange_invalid_args(self):
        self.assertIn("-ERR", self.handler.handle(["LRANGE", "mylist", "1"]))

    # --- SET COMMANDS ---
    def test_sadd_smembers(self):
        self.assertEqual(self.handler.handle(["SADD", "myset", "a", "b", "c"]), ":3\r\n")
        members = self.handler.handle(["SMEMBERS", "myset"])
        self.assertTrue(all(m in members for m in ["$1\r\na\r\n", "$1\r\nb\r\n", "$1\r\nc\r\n"]))

    def test_srem(self):
        self.handler.handle(["SADD", "myset", "x", "y", "z"])
        self.assertEqual(self.handler.handle(["SREM", "myset", "x", "y"]), ":2\r\n")
        remaining = self.handler.handle(["SMEMBERS", "myset"])
        self.assertNotIn("$1\nx\r\n", remaining)

    def test_sismember(self):
        self.handler.handle(["SADD", "myset", "hello"])
        self.assertEqual(self.handler.handle(["SISMEMBER", "myset", "hello"]), ":1\r\n")
        self.assertEqual(self.handler.handle(["SISMEMBER", "myset", "world"]), ":0\r\n")

    # --- HASH COMMANDS ---
    def test_hset_hget(self):
        self.assertEqual(self.handler.handle(["HSET", "h", "f1", "v1"]), ":1\r\n")
        self.assertEqual(self.handler.handle(["HGET", "h", "f1"]), "$2\r\nv1\r\n")

    def test_hgetall(self):
        self.handler.handle(["HSET", "h", "a", "1"])
        self.handler.handle(["HSET", "h", "b", "2"])
        res = self.handler.handle(["HGETALL", "h"])
        self.assertIn("$1\r\na\r\n", res)
        self.assertIn("$1\r\n1\r\n", res)
        self.assertIn("$1\r\nb\r\n", res)
        self.assertIn("$1\r\n2\r\n", res)  

    def test_hdel(self):
        self.handler.handle(["HSET", "h", "f", "v"])
        self.assertEqual(self.handler.handle(["HDEL", "h", "f", "nonexistent"]), ":1\r\n")

    # --- ZSET COMMANDS ---
    def test_zadd_zscore_zrange(self):
        self.assertEqual(self.handler.handle(["ZADD", "myz", "2", "b"]), ":1\r\n")
        self.assertEqual(self.handler.handle(["ZADD", "myz", "1", "a"]), ":1\r\n")
        self.assertEqual(self.handler.handle(["ZSCORE", "myz", "a"]), "$3\r\n1.0\r\n")        
        res = self.handler.handle(["ZRANGE", "myz", "0", "1"])
        self.assertIn("$1\r\na\r\n", res)
        self.assertIn("$1\r\nb\r\n", res)

if __name__ == "__main__":
    unittest.main()
