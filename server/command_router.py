# server/command_router.py

from datastore import BaseStore, ListStore, SetStore, HashStore, ZSetStore, ExpiryManager
from protocol import serializer as s
from persistence.aof_writer import AOFWriter
from persistence.aof_compactor import rewrite_aof
import os

class CommandHandler:
    def __init__(self):
        self.store = BaseStore()
        self.lists = ListStore()
        self.sets = SetStore()
        self.hashes = HashStore()
        self.zsets = ZSetStore()
        self.expiry = ExpiryManager()
        self.aof = AOFWriter()

    def handle(self, tokens: list[str]):
        if not tokens:
            return s.error("Empty command")

        cmd = tokens[0].upper()

        try:
            # --- Base Commands ---
            if cmd == "PING":
                return s.simple_string("PONG")

            elif cmd == "BGREWRITEAOF":
                self.rewrite_aof_log()
                return s.simple_string("Background AOF rewrite started")
            
            elif cmd == "SET":
                if len(tokens) != 3:
                    return self._error("Usage: SET key value")
                self.store.set(tokens[1], tokens[2])
                self.aof.append(tokens)
                return s.simple_string("OK")

            elif cmd == "GET":
                if len(tokens) != 2:
                    return self._error("Usage: GET key")
                self._delete_if_expired(tokens[1])
                val = self.store.get(tokens[1])
                return s.bulk_string(val)

            elif cmd == "DEL":
                if len(tokens) != 2:
                    return self._error("Usage: DEL key")
                success = self.store.delete(tokens[1])
                self.aof.append(tokens)
                return s.integer(int(success))

            elif cmd == "EXISTS":
                if len(tokens) != 2:
                    return self._error("Usage: EXISTS key")
                self._delete_if_expired(tokens[1])
                exists = self.store.exists(tokens[1])
                return s.integer(int(exists))

            elif cmd == "EXPIRE":
                if len(tokens) != 3:
                    return s.error("Usage: EXPIRE key seconds")
                key = tokens[1]
                ttl = int(tokens[2])
                # Check if key exists in any store
                exists = (
                    self.store.exists(key) or
                    key in self.hashes.hashes or
                    key in self.lists.lists or
                    key in self.sets.sets or
                    key in self.zsets.scores  # or self.zsets.sorted, depending on your implementation
                )
                if not exists:
                    return s.integer(0)
                self.expiry.set_expiry(key, ttl)
                return s.integer(1)

            elif cmd == "TTL":
                if len(tokens) != 2:
                    return s.error("Usage: TTL key")
                return s.integer(self.expiry.ttl(tokens[1]))

            # --- LIST Commands ---
            elif cmd == "LPUSH":
                if len(tokens) < 3:
                    return self._error("Usage: LPUSH key value [value ...]")
                count = self.lists.lpush(tokens[1], *tokens[2:])
                self.aof.append(tokens)
                return s.integer(count)

            elif cmd == "RPUSH":
                if len(tokens) < 3:
                    return self._error("Usage: RPUSH key value [value ...]")
                count = self.lists.rpush(tokens[1], *tokens[2:])
                self.aof.append(tokens)
                return s.integer(count)

            elif cmd == "LPOP":
                if len(tokens) != 2:
                    return self._error("Usage: LPOP key")
                self._delete_if_expired(tokens[1])
                val = self.lists.lpop(tokens[1])
                self.aof.append(tokens)
                return s.bulk_string(val)

            elif cmd == "RPOP":
                if len(tokens) != 2:
                    return self._error("Usage: RPOP key")
                self._delete_if_expired(tokens[1])
                val = self.lists.rpop(tokens[1])
                self.aof.append(tokens)
                return s.bulk_string(val)

            elif cmd == "LRANGE":
                if len(tokens) != 4:
                    return self._error("Usage: LRANGE key start end")
                self._delete_if_expired(tokens[1])
                result = self.lists.lrange(tokens[1], int(tokens[2]), int(tokens[3]))
                return s.array(result)

            elif cmd == "LLEN":
                if len(tokens) != 2:
                    return self._error("Usage: LLEN key")
                self._delete_if_expired(tokens[1])
                return s.integer(self.lists.llen(tokens[1]))

            # --- SET Commands ---
            elif cmd == "SADD":
                if len(tokens) < 3:
                    return self._error("Usage: SADD key member [member ...]")
                count = self.sets.sadd(tokens[1], *tokens[2:])
                self.aof.append(tokens)
                return s.integer(count)

            elif cmd == "SREM":
                if len(tokens) < 3:
                    return self._error("Usage: SREM key member [member ...]")
                count = self.sets.srem(tokens[1], *tokens[2:])
                self.aof.append(tokens)
                return s.integer(count)

            elif cmd == "SISMEMBER":
                if len(tokens) != 3:
                    return self._error("Usage: SISMEMBER key member")
                self._delete_if_expired(tokens[1])
                is_member = self.sets.sismember(tokens[1], tokens[2])
                return s.integer(int(is_member))

            elif cmd == "SMEMBERS":
                if len(tokens) != 2:
                    return self._error("Usage: SMEMBERS key")
                self._delete_if_expired(tokens[1])
                members = self.sets.smembers(tokens[1])
                return s.array(members)

            # --- HASH Commands ---
            elif cmd == "HSET":
                if len(tokens) != 4:
                    return s.error("Usage: HSET key field value")
                result = self.hashes.hset(tokens[1], tokens[2], tokens[3])
                self.aof.append(tokens)
                return s.integer(result)

            elif cmd == "HGET":
                if len(tokens) != 3:
                    return s.error("Usage: HGET key field")
                self._delete_if_expired(tokens[1])
                val = self.hashes.hget(tokens[1], tokens[2])
                return s.bulk_string(val)

            elif cmd == "HGETALL":
                if len(tokens) != 2:
                    return s.error("Usage: HGETALL key")
                self._delete_if_expired(tokens[1])
                return s.array(self.hashes.hgetall(tokens[1]))

            elif cmd == "HDEL":
                if len(tokens) < 3:
                    return s.error("Usage: HDEL key field [field ...]")
                count = self.hashes.hdel(tokens[1], *tokens[2:])
                self.aof.append(tokens)
                return s.integer(count)
            
            # --- ZSET Commands ---
            elif cmd == "ZADD":
                if len(tokens) != 4:
                    return s.error("Usage: ZADD key score member")
                result = self.zsets.zadd(tokens[1], float(tokens[2]), tokens[3])
                self.aof.append(tokens)
                return s.integer(result)

            elif cmd == "ZSCORE":
                if len(tokens) != 3:
                    return s.error("Usage: ZSCORE key member")
                self._delete_if_expired(tokens[1])
                score = self.zsets.zscore(tokens[1], tokens[2])
                return s.bulk_string(score)

            elif cmd == "ZRANGE":
                if len(tokens) != 4:
                    return s.error("Usage: ZRANGE key start stop")
                self._delete_if_expired(tokens[1])
                members = self.zsets.zrange(tokens[1], int(tokens[2]), int(tokens[3]))
                return s.array(members)

            else:
                return s.error(f"Unknown command '{cmd}'")

        except Exception as e:
            return s.error(str(e))
        
    def _delete_if_expired(self, key: str):
        if self.expiry.is_expired(key):
            self._delete_key_everywhere(key)

    def _delete_key_everywhere(self, key: str):
        self.store.delete(key)
        self.lists.lists.pop(key, None)
        self.sets.sets.pop(key, None)
        self.hashes.hashes.pop(key, None)
        self.zsets.scores.pop(key, None)
        self.zsets.sorted.pop(key, None)
        self.expiry.remove(key)
        
    def rewrite_aof_log(self):
        rewrite_aof(self)
        os.replace("aof.log.rewrite", "aof.log")