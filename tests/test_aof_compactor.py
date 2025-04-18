# tests/test_aof_compactor.py

import unittest
import os
from persistence.aof_compactor import rewrite_aof

class MockCommandHandler:
    def __init__(self):
        self.store = MockBaseStore()
        self.lists = MockListStore()
        self.sets = MockSetStore()
        self.hashes = MockHashStore()
        self.zsets = MockZSetStore()

class MockBaseStore:
    def __init__(self):
        self.store = {
            "foo": ("bar", None),
            "hello": ("world", None)
        }

class MockListStore:
    def __init__(self):
        self.lists = {
            "mylist": ["a", "b", "c"]
        }

class MockSetStore:
    def __init__(self):
        self.sets = {
            "myset": {"x", "y"}
        }

class MockHashStore:
    def __init__(self):
        self.hashes = {
            "myhash": {"name": "Alice", "age": "30"}
        }

class MockZSetStore:
    def __init__(self):
        self.scores = {
            "myzset": {"one": 1.0, "two": 2.5}
        }
        self.sorted = {
            "myzset": [(1.0, "one"), (2.5, "two")]
        }

class TestAOFCompactor(unittest.TestCase):
    def setUp(self):
        self.outfile = "test_rewrite.log"
        if os.path.exists(self.outfile):
            os.remove(self.outfile)

    def tearDown(self):
        if os.path.exists(self.outfile):
            os.remove(self.outfile)

    def test_rewrite_aof_creates_expected_commands(self):
        handler = MockCommandHandler()
        rewrite_aof(handler, out_file=self.outfile)

        with open(self.outfile, "rb") as f:
            content = f.read().decode("utf-8")

        # Minimal checks for correct RESP formatting
        self.assertIn("*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n", content)
        self.assertIn("*5\r\n$5\r\nRPUSH\r\n$6\r\nmylist\r\n$1\r\na\r\n$1\r\nb\r\n$1\r\nc\r\n", content)
        self.assertIn("*4\r\n$4\r\nSADD\r\n$5\r\nmyset\r\n$1\r\nx\r\n$1\r\ny\r\n", content)
        self.assertIn("*4\r\n$4\r\nHSET\r\n$6\r\nmyhash\r\n$4\r\nname\r\n$5\r\nAlice\r\n", content)
        self.assertIn("*4\r\n$4\r\nZADD\r\n$6\r\nmyzset\r\n$3\r\n1.0\r\n$3\r\none\r\n", content)

    def test_rewrite_empty_stores(self):
        class EmptyHandler:
            def __init__(self):
                self.store = MockBaseStore()
                self.store.store.clear()
                self.lists = MockListStore()
                self.lists.lists.clear()
                self.sets = MockSetStore()
                self.sets.sets.clear()
                self.hashes = MockHashStore()
                self.hashes.hashes.clear()
                self.zsets = MockZSetStore()
                self.zsets.scores.clear()
                self.zsets.sorted.clear()

        rewrite_aof(EmptyHandler(), out_file=self.outfile)

        with open(self.outfile, "r") as f:
            content = f.read()

        self.assertEqual(content, "")  # Should write nothing

if __name__ == "__main__":
    unittest.main()
