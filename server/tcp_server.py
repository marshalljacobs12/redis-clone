# server/tcp_server.py

import asyncio
from server.command_router import CommandHandler
from persistence.aof_replayer import replay_aof

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, handler: CommandHandler):
    addr = writer.get_extra_info('peername')
    while True:
        try:
            data = await reader.readline()
            if not data:
                break

            # RESP parsing
            command_line = data.decode().strip()
            if command_line.startswith("*"):
                # Multi-bulk RESP array
                count = int(command_line[1:])
                tokens = []
                for _ in range(count):
                    await reader.readline()  # skip $<len>
                    value = (await reader.readline()).decode().strip()
                    tokens.append(value)
            else:
                tokens = command_line.split()

            response = await handler.handle(tokens, writer)
            if response is not None:
                writer.write(response.encode())
                await writer.drain()

        except Exception as e:
            writer.write(f"-ERR {str(e)}\r\n".encode())
            await writer.drain()
            break

    writer.close()
    await writer.wait_closed()


async def start_server():
    handler = CommandHandler()

    # Replay past state
    await replay_aof("aof.log", handler)
    
    # Start GC task
    asyncio.create_task(handler.expiry.run_gc(handler._delete_key_everywhere, interval=1))

    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, handler), host="0.0.0.0", port=6379
    )

    print("🚀 Redis clone running on port 6379")
    async with server:
        await server.serve_forever()
