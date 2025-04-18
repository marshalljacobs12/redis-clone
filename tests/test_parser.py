# tests/test_parser.py
import unittest
from protocol.parser import RESPParser

class TestRESPParser(unittest.TestCase):
    def test_simple_set_command(self):
        raw = b'*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n'
        parser = RESPParser(raw)
        result = parser.parse()
        self.assertEqual(result, ['SET', 'foo', 'bar'])

    def test_get_command(self):
        raw = b'*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n'
        parser = RESPParser(raw)
        result = parser.parse()
        self.assertEqual(result, ['GET', 'foo'])

    def test_null_bulk_string(self):
        raw = b'*2\r\n$3\r\nGET\r\n$-1\r\n'
        parser = RESPParser(raw)
        result = parser.parse()
        self.assertEqual(result, ['GET', None])

if __name__ == "__main__":
    unittest.main()
