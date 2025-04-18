# persistence/aof_writer.py

class AOFWriter:
    def __init__(self, filepath="aof.log"):
        self.filepath = filepath
        self.file = open(self.filepath, "ab", buffering=0)  # binary append
    
    def append(self, tokens: list[str]):
        self.file.write(self._encode_as_resp(tokens))

    def _encode_as_resp(self, tokens: list[str]) -> bytes:
        out = f"*{len(tokens)}\r\n"
        for token in tokens:
            out += f"${len(token)}\r\n{token}\r\n"
        return out.encode("utf-8")

    def close(self):
        self.file.close()
