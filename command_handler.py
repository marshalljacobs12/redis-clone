# redis_clone/command_handler.py

from datastore import DataStore

class CommandHandler:
    def __init__(self, store: DataStore):
        self.store = store

    def handle(self, tokens: list[str]):
        if not tokens:
            return self._error("Empty command")

        cmd = tokens[0].upper()

        try:
            if cmd == "PING":
                return "+PONG\r\n"

            elif cmd == "SET":
                if len(tokens) != 3:
                    return self._error("Usage: SET key value")
                self.store.set(tokens[1], tokens[2])
                return "+OK\r\n"

            elif cmd == "GET":
                if len(tokens) != 2:
                    return self._error("Usage: GET key")
                val = self.store.get(tokens[1])
                return self._bulk_string(val)

            elif cmd == "DEL":
                if len(tokens) != 2:
                    return self._error("Usage: DEL key")
                success = self.store.delete(tokens[1])
                return f":{int(success)}\r\n"

            elif cmd == "EXISTS":
                if len(tokens) != 2:
                    return self._error("Usage: EXISTS key")
                exists = self.store.exists(tokens[1])
                return f":{int(exists)}\r\n"

            elif cmd == "EXPIRE":
                if len(tokens) != 3:
                    return self._error("Usage: EXPIRE key seconds")
                success = self.store.expire(tokens[1], int(tokens[2]))
                return f":{int(success)}\r\n"

            elif cmd == "TTL":
                if len(tokens) != 2:
                    return self._error("Usage: TTL key")
                ttl = self.store.ttl(tokens[1])
                return f":{ttl}\r\n"

            else:
                return self._error(f"Unknown command '{cmd}'")

        except Exception as e:
            return self._error(str(e))

    def _error(self, message: str) -> str:
        return f"-ERR {message}\r\n"

    def _bulk_string(self, val: str | None) -> str:
        if val is None:
            return "$-1\r\n"
        return f"${len(val)}\r\n{val}\r\n"
