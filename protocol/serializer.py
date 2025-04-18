# protocol/serializer.py

def simple_string(msg: str) -> str:
    return f"+{msg}\r\n"

def error(msg: str) -> str:
    return f"-ERR {msg}\r\n"

def integer(val: int) -> str:
    return f":{val}\r\n"

def bulk_string(val: str | None) -> str:
    if val is None:
        return "$-1\r\n"
    return f"${len(val)}\r\n{val}\r\n"

def array(items: list[str]) -> str:
    out = f"*{len(items)}\r\n"
    for item in items:
        out += bulk_string(item)
    return out
