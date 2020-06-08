from functools import reduce
from math import ceil, log
from typing import Callable, Optional, List

from bitmap import Bitmap
from bits import Bits

DRAW_BIT_TYPE = Callable[[int, int, bool], None]


class App:
    def __init__(self) -> None:
        super().__init__()
        self._data: Optional[bytes] = None

    @property
    def num_bits(self):
        return len(self._data) * 8 if self._data is not None else 0

    def load_file(self, filename):
        max_bytes = 10 ** 6
        with open(filename, "rb") as f:
            self._data = f.read(max_bytes)

    def draw(
        self,
        offset: int,
        row_width: int,
        start_column: int,
        start_row: int,
        visible_rows: int,
        visible_columns: int,
        draw_bit: DRAW_BIT_TYPE,
    ):
        if self._data is None:
            return

        start = start_row * row_width + start_column
        x = y = 0
        bits = Bits(self._data, offset)
        bits.jump(start)
        for b in bits:
            draw_bit(x, y, b)
            x += 1
            if x + start_column >= row_width or x > visible_columns:
                x = 0
                y += 1
                bits.jump((y + start_row) * row_width + start_column)
            if y > visible_rows:
                break

    def create_bitmap(
        self,
        offset: int,
        row_width: int,
        start_column: int,
        start_row: int,
        visible_rows: int,
        visible_columns: int,
        bit_size: int,
    ) -> Optional[Bitmap]:
        if self._data is None:
            return

        start = start_row * row_width + start_column + offset
        num_rows = min(ceil((self.num_bits - start) / row_width), visible_rows + 1) - 1
        bits_per_row = min(row_width, visible_columns)
        bytes_per_row = ceil(bits_per_row / 8)
        result = []
        for _ in range(num_rows):
            result.extend(self._get_row_bytes(start, bytes_per_row) * bit_size)
            start += row_width
        remainder = []
        last_byte = min(start // 8 + bytes_per_row, len(self._data))
        if last_byte < len(self._data):
            result.extend(self._get_row_bytes(start, bytes_per_row) * bit_size)
        else:
            remainder = self._get_end_bits(start)
        result = bytes(b for ob in result for b in self._replicate_byte(ob, bit_size))
        return Bitmap(
            result, bits_per_row * bit_size, bytes_per_row * bit_size, remainder
        )

    def _get_row_bytes(self, start, num_bytes) -> list:
        i, bi = start // 8, start % 8
        if not bi:
            return self._data[i : i + num_bytes]

        h_mask = 2 ** (8 - bi) - 1
        l_mask = 2 ** 8 - h_mask - 1
        pairs = zip(
            self._data[i : i + num_bytes], self._data[i + 1 : i + num_bytes + 1]
        )
        return [((h & h_mask) << bi) + ((l & l_mask) >> (8 - bi)) for h, l in pairs]

    def _get_end_bits(self, start) -> List[bool]:
        i, bi = start // 8, start % 8
        return [bit for byte in self._data[i:] for bit in self._byte_to_bits(byte)][bi:]

    @classmethod
    def _replicate_byte(cls, b: int, n: int) -> list:
        n -= 1
        if not n:
            return [b]

        masks = [cls._move(0xF, n + 1), cls._move(0x3, n + 1), cls._move(1, n + 1)]
        spaced = b
        spaced = (spaced ^ (spaced << (4 * n))) & masks[0]
        spaced = (spaced ^ (spaced << (2 * n))) & masks[1]
        spaced = (spaced ^ (spaced << n)) & masks[2]
        replicated = reduce(lambda x, i: x | (spaced << i), range(n + 1), 0)
        return [(replicated >> (8 * i)) & 0xFF for i in range(n, -1, -1)]

    @classmethod
    def _move(cls, n, m):
        base = int(log(n + 1, 2))
        result = n
        for i in range(8 // base - 1):
            result = (result << (m * base)) | n
        return result

    @staticmethod
    def _byte_to_bits(b):
        return [bool((b >> i) & 1) for i in range(7, -1, -1)]
