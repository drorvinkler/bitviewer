from typing import Iterator


class Bits(Iterator[bool]):
    def __init__(self, data: bytes, start: int) -> None:
        super().__init__()
        self._data = data
        self._index = start

    def __next__(self) -> bool:
        if self._index >= len(self._data) * 8:
            raise StopIteration

        b = self._data[self._index // 8] << (self._index % 8)
        self._index += 1
        return bool(b & 128)

    def jump(self, to):
        self._index = to
