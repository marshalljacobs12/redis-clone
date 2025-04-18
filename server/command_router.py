# server/command_router.py

from datastore import BaseStore, ListStore, SetStore


class CommandHandler:
    def __init__(self):
        self.store = BaseStore()
        self.lists = ListStore()
        self.sets = SetStore()

    def handle(self, tokens: list[str]):
        if not tokens:
            return self._error("Empty command")

        cmd = tokens[0].upper()

        try:
            # --- Base Commands ---
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

            # --- LIST Commands ---
            elif cmd == "LPUSH":
                if len(tokens) < 3:
                    return self._error("Usage: LPUSH key value [value ...]")
                count = self.lists.lpush(tokens[1], *tokens[2:])
                return f":{count}\r\n"

            elif cmd == "RPUSH":
                if len(tokens) < 3:
                    return self._error("Usage: RPUSH key value [value ...]")
                count = self.lists.rpush(tokens[1], *tokens[2:])
                return f":{count}\r\n"

            elif cmd == "LPOP":
                if len(tokens) != 2:
                    return self._error("Usage: LPOP key")
                val = self.lists.lpop(tokens[1])
                return self._bulk_string(val)

            elif cmd == "RPOP":
                if len(tokens) != 2:
                    return self._error("Usage: RPOP key")
                val = self.lists.rpop(tokens[1])
                return self._bulk_string(val)

            elif cmd == "LRANGE":
                if len(tokens) != 4:
                    return self._error("Usage: LRANGE key start end")
                result = self.lists.lrange(tokens[1], int(tokens[2]), int(tokens[3]))
                return self._array(result)

            elif cmd == "LLEN":
                if len(tokens) != 2:
                    return self._error("Usage: LLEN key")
                return f":{self.lists.llen(tokens[1])}\r\n"

            # --- SET Commands ---
            elif cmd == "SADD":
                if len(tokens) < 3:
                    return self._error("Usage: SADD key member [member ...]")
                count = self.sets.sadd(tokens[1], *tokens[2:])
                return f":{count}\r\n"

            elif cmd == "SREM":
                if len(tokens) < 3:
                    return self._error("Usage: SREM key member [member ...]")
                count = self.sets.srem(tokens[1], *tokens[2:])
                return f":{count}\r\n"

            elif cmd == "SISMEMBER":
                if len(tokens) != 3:
                    return self._error("Usage: SISMEMBER key member")
                is_member = self.sets.sismember(tokens[1], tokens[2])
                return f":{int(is_member)}\r\n"

            elif cmd == "SMEMBERS":
                if len(tokens) != 2:
                    return self._error("Usage: SMEMBERS key")
                members = self.sets.smembers(tokens[1])
                return self._array(members)

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

    def _array(self, items: list[str]) -> str:
        out = f"*{len(items)}\r\n"
        for item in items:
            out += self._bulk_string(item)
        return out
