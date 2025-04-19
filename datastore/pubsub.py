# datastore/pubsub.py
import asyncio
from collections import defaultdict

class PubSubManager:
    def __init__(self):
        # channel -> set of writer objects (asyncio.StreamWriter)
        self.channels = defaultdict(set)
        self.lock = asyncio.Lock()

    async def subscribe(self, writer, *channel_names):
        async with self.lock:
            for channel in channel_names:
                self.channels[channel].add(writer)
        return f"Subscribed to: {', '.join(channel_names)}"

    async def unsubscribe(self, writer, *channel_names):
        async with self.lock:
            for channel in channel_names:
                if writer in self.channels[channel]:
                    self.channels[channel].remove(writer)
                    if not self.channels[channel]:
                        del self.channels[channel]
        return f"Unsubscribed from: {', '.join(channel_names)}"

    async def publish(self, channel, message):
        async with self.lock:
            if channel not in self.channels:
                return 0  # No subscribers
            subscribers = list(self.channels[channel])
        
        # Send messages outside the lock to avoid blocking
        for writer in subscribers:
            try:
                writer.write(self.format_pubsub_message(channel, message).encode())
                await writer.drain()
            except Exception as e:
                # Optionally handle broken connections
                pass

        return len(subscribers)

    def format_pubsub_message(self, channel, message):
        return f"*3\r\n$7\r\nmessage\r\n${len(channel)}\r\n{channel}\r\n${len(message)}\r\n{message}\r\n"
