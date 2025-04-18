# redis_clone/protocol.py

# RESP parsing and serialization
class RESPParser:
    def __init__(self, stream: bytes):
        self.stream = stream
        self.index = 0

    def parse(self):
        if self.stream[self.index:self.index+1] == b'*':
            return self._parse_array()
        raise ValueError("Unsupported RESP type")

    def _parse_array(self):
        self.index += 1
        line = self._readline()
        num_elements = int(line)
        elements = []
        for _ in range(num_elements):
            prefix = self.stream[self.index:self.index+1]
            if prefix == b'$':      # only support bulk strings for now
                self.index += 1
                elements.append(self._parse_bulk_string())
            else:
                raise ValueError(f"Unsupported array element type: {prefix}")
        return elements

    def _parse_bulk_string(self):
        length = int(self._readline())
        if length == -1:
            return None
        value = self.stream[self.index:self.index+length].decode()
        self.index += length + 2  # skip \r\n
        return value

    def _readline(self):
        end = self.stream.index(b'\r\n', self.index)
        line = self.stream[self.index:end].decode()
        self.index = end + 2
        return line
