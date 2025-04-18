# tests/test_aof.py

import unittest
import os
from persistence.aof_writer import AOFWriter
from persistence.aof_replayer import replay_aof

class MockCommandHandler:
    def __init__(self):
        self.calls = []

    def handle(self, tokens):
        self.calls.append(tokens)


class TestAOF(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_aof.log"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_append_single_command(self):
        writer = AOFWriter(filepath=self.test_file)
        writer.append(["SET", "foo", "bar"])
        writer.close()

        with open(self.test_file, "rb") as f:  # <-- Binary mode
            content = f.read()

        expected = b"*3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n"
        self.assertEqual(content, expected)

    def test_replay_appended_command(self):
        handler = MockCommandHandler()
        writer = AOFWriter(filepath=self.test_file)
        writer.append(["HSET", "user", "name", "Alice"])
        writer.append(["ZADD", "myz", "1", "x"])
        writer.close()

        replay_aof(self.test_file, handler)

        self.assertEqual(handler.calls, [
            ["HSET", "user", "name", "Alice"],
            ["ZADD", "myz", "1", "x"]
        ])

    def test_replay_ignores_non_resp_lines(self):
        with open(self.test_file, "w") as f:
            f.write("NOTRESP\n")
            f.write("*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n")

        handler = MockCommandHandler()
        replay_aof(self.test_file, handler)

        self.assertEqual(handler.calls, [["GET", "foo"]])

    def test_empty_file_does_not_crash(self):
        open(self.test_file, "w").close()  # create empty file
        handler = MockCommandHandler()
        replay_aof(self.test_file, handler)
        self.assertEqual(handler.calls, [])

    def test_missing_file_does_not_crash(self):
        handler = MockCommandHandler()
        replay_aof("nonexistent_file.log", handler)
        self.assertEqual(handler.calls, [])


if __name__ == "__main__":
    unittest.main()
