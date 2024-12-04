import re
from typing import Iterator

class ChunkCutter:
    def __init__(self):
        self.lines = []

    def load(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.lines = file.readlines()

    def get_chunk(self) -> Iterator[str]:
        raise NotImplementedError("This method should be overridden by subclasses")




class TimestampChunkCutter(ChunkCutter):
    def __init__(self, chunk_size):
        super().__init__()
        self.chunk_size = chunk_size

    def get_chunk(self) -> Iterator[str]:
        current_chunk = []
        timestamp_count = 0

        for line in self.lines:
            timestamp_match = re.search(r'\*?\*?\d{2}:\d{2}:\d{2}\*?\*?', line)
            if timestamp_match:
                timestamp_count += 1
                if timestamp_count > self.chunk_size:
                    yield ''.join(current_chunk)
                    current_chunk = [ line ]
                    timestamp_count = 1
                else:
                    current_chunk.append(line)
            else:
                current_chunk.append(line)

        if current_chunk:
            yield ''.join(current_chunk)
