# redis_clone/server.py

import asyncio
from datastore import DataStore
from command_handler import CommandHandler
from protocol import RESPParser

class RedisServer:
    def __init__(self, host='127.0.0.1', port=6379):
        self.host = host
        self.port = port
        self.store = DataStore()
        self.handler = CommandHandler(self.store)

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info('peername')
        print(f"[+] Connection from {addr}")

        try:
            while not reader.at_eof():
                data = await reader.readuntil(b'\r\n')  # read first line
                if not data:
                    break

                # Peek at the array length to know how much more to read
                remaining = await self._read_full_request(reader, data)
                full_data = data + remaining

                # Parse the command
                try:
                    parser = RESPParser(full_data)
                    tokens = parser.parse()
                    response = self.handler.handle(tokens)
                except Exception as e:
                    response = f"-ERR {str(e)}\r\n"

                writer.write(response.encode())
                await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionResetError):
            print(f"[-] Connection closed: {addr}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def _read_full_request(self, reader, first_line):
        # Only needed for array requests
        if not first_line.startswith(b'*'):
            return b''
        num_elements = int(first_line[1:-2])
        chunks = []
        for _ in range(num_elements * 2):  # $len + data per element
            chunks.append(await reader.readuntil(b'\r\n'))
        return b''.join(chunks)

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"🚀 Redis clone server running on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    try:
        asyncio.run(RedisServer().start())
    except KeyboardInterrupt:
        print("\n🛑 Server shut down.")
