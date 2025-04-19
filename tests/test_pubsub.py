# tests/test_pubsub.py

import asyncio
import pytest
from datastore import PubSubManager

class FakeWriter:
    def __init__(self):
        self.buffer = []

    def write(self, data):
        self.buffer.append(data)

    async def drain(self):
        pass  # No-op for fake writer

    def get_messages(self):
        return b"".join(self.buffer).decode()

@pytest.mark.asyncio
async def test_subscribe_and_publish():
    pubsub = PubSubManager()
    writer = FakeWriter()

    await pubsub.subscribe(writer, "news")
    await pubsub.publish("news", "hello world")

    assert "message" in writer.get_messages()
    assert "news" in writer.get_messages()
    assert "hello world" in writer.get_messages()

@pytest.mark.asyncio
async def test_multiple_subscribers():
    pubsub = PubSubManager()
    writer1 = FakeWriter()
    writer2 = FakeWriter()

    await pubsub.subscribe(writer1, "chat")
    await pubsub.subscribe(writer2, "chat")
    count = await pubsub.publish("chat", "yo")

    assert count == 2
    assert "yo" in writer1.get_messages()
    assert "yo" in writer2.get_messages()

@pytest.mark.asyncio
async def test_unsubscribe():
    pubsub = PubSubManager()
    writer = FakeWriter()

    await pubsub.subscribe(writer, "log")
    await pubsub.unsubscribe(writer, "log")
    count = await pubsub.publish("log", "log message")

    assert count == 0
    assert "log message" not in writer.get_messages()

@pytest.mark.asyncio
async def test_subscribe_multiple_channels():
    pubsub = PubSubManager()
    writer = FakeWriter()

    await pubsub.subscribe(writer, "a", "b", "c")
    await pubsub.publish("a", "msg1")
    await pubsub.publish("c", "msg2")

    messages = writer.get_messages()
    assert "msg1" in messages
    assert "msg2" in messages
