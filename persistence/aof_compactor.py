# persistence/aof_compactor.py

def rewrite_aof(handler, out_file="aof.log.rewrite"):
    with open(out_file, "wb") as f:
        def write_line(line):
            f.write(line.encode("utf-8"))

        # BaseStore (strings)
        for key, (value, _) in handler.store.store.items():
            print(f"key: {key}, value: {value}")
            write_line(_to_resp(["SET", key, value]))

        # ListStore
        for key, dq in handler.lists.lists.items():
            if dq:
                write_line(_to_resp(["RPUSH", key] + list(dq)))

        # SetStore
        for key, s in handler.sets.sets.items():
            if s:
                write_line(_to_resp(["SADD", key] + sorted(s)))

        # HashStore
        for key, fields in handler.hashes.hashes.items():
            for field, val in fields.items():
                write_line(_to_resp(["HSET", key, field, val]))

        # ZSetStore
        for key, members in handler.zsets.scores.items():
            for member, score in members.items():
                write_line(_to_resp(["ZADD", key, str(score), member]))

def _to_resp(tokens):
    out = f"*{len(tokens)}\r\n"
    for token in tokens:
        out += f"${len(token)}\r\n{token}\r\n"
    return out
