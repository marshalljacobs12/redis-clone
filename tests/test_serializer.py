# tests/test_serializer.py

import unittest
from protocol import serializer as s

class TestSerializer(unittest.TestCase):
    def test_simple_string(self):
        self.assertEqual(s.simple_string("PONG"), "+PONG\r\n")

    def test_error(self):
        self.assertEqual(s.error("Invalid command"), "-ERR Invalid command\r\n")

    def test_integer(self):
        self.assertEqual(s.integer(5), ":5\r\n")

    def test_bulk_string(self):
        self.assertEqual(s.bulk_string("hello"), "$5\r\nhello\r\n")
        self.assertEqual(s.bulk_string(None), "$-1\r\n")

    def test_array(self):
        arr = s.array(["foo", "bar"])
        self.assertEqual(arr, "*2\r\n$3\r\nfoo\r\n$3\r\nbar\r\n")

if __name__ == "__main__":
    unittest.main()
