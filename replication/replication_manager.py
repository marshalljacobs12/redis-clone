# replication/replication_manager.py

import asyncio
from protocol.serializer import encode_command

class ReplicationManager:
    def __init__(self):
        self.is_replica = False
        self.master_host = None
        self.master_port = None
        self.replica_writers = []  # asyncio writers for replicas if acting as master

    # ─────────────────────────────────────────────────────────────────────────────
    # MASTER MODE: forward commands to replicas
    # ─────────────────────────────────────────────────────────────────────────────
    def add_replica(self, writer):
        self.replica_writers.append(writer)
        print(f"[Replication] Added replica: {writer.get_extra_info('peername')}")

    async def forward_to_replicas(self, *tokens):
        if not self.replica_writers:
            return
        msg = await encode_command(*tokens)
        for writer in self.replica_writers:
            try:
                writer.write(msg.encode())
                await writer.drain()
            except Exception as e:
                print(f"[Replication] Error sending to replica: {e}")

    # ─────────────────────────────────────────────────────────────────────────────
    # REPLICA MODE: connect to master and listen
    # ─────────────────────────────────────────────────────────────────────────────
    async def become_replica(self, host, port):
        self.is_replica = True
        self.master_host = host
        self.master_port = port
        asyncio.create_task(self._replica_listener())

    async def _replica_listener(self):
        try:
            reader, writer = await asyncio.open_connection(self.master_host, self.master_port)
            print(f"[Replication] Connected to master {self.master_host}:{self.master_port}")

            # Identify self as replica
            writer.write((await encode_command("REPLICAOF")).encode())
            await writer.drain()

            from protocol.parser import RESPParser
            from server.command_router import CommandHandler

            handler = CommandHandler()

            while True:
                first_line = await reader.readline()
                if not first_line:
                    break

                # buffer rest of RESP message
                full_msg = bytearray(first_line)
                if first_line.startswith(b"*"):
                    num_args = int(first_line[1:].strip())
                    for _ in range(num_args):
                        length_line = await reader.readline()
                        full_msg.extend(length_line)
                        length = int(length_line[1:].strip())
                        data = await reader.readexactly(length + 2)
                        full_msg.extend(data)

                parser = RESPParser(bytes(full_msg))
                tokens = parser.parse()

                print(f"[Replica] Applying command: {tokens}")
                await handler.handle(tokens)

        except Exception as e:
            print(f"[Replication] Error in replica: {e}")
