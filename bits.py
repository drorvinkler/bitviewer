from typing import Iterator


class Bits(Iterator[bool]):
    def __init__(self, data: bytes, start: int) -> None:
        super().__init__()
        self._data = data
        self._start = start
        self._index = 0

    @property
    def _real_index(self):
        return self._index + self._start

    def __next__(self) -> bool:
        if self._real_index >= len(self._data) * 8:
            raise StopIteration

        b = self._data[self._real_index // 8] << (self._real_index % 8)
        self._index += 1
        return bool(b & 128)

    def jump(self, to):
        self._index = to
