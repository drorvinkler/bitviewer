from math import ceil
from typing import Optional, List

from bitmap import Bitmap


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

    def create_bitmap(
        self,
        offset: int,
        row_width: int,
        start_column: int,
        start_row: int,
        visible_rows: int,
        visible_columns: int,
    ) -> Optional[Bitmap]:
        if self._data is None:
            return

        start = start_row * row_width + start_column + offset
        num_rows = min(ceil((self.num_bits - start) / row_width), visible_rows + 1) - 1
        bits_per_row = min(row_width, visible_columns)
        bytes_per_row = ceil(bits_per_row / 8)
        result = []
        for _ in range(num_rows):
            result.extend(self._get_row_bytes(start, bytes_per_row))
            start += row_width
        remainder = []
        last_byte = start // 8 + bytes_per_row
        if last_byte < len(self._data):
            result.extend(self._get_row_bytes(start, bytes_per_row))
        else:
            remainder = self._get_end_bits(start)
        return Bitmap(bytes(result), bits_per_row, bytes_per_row, remainder)

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

    @staticmethod
    def _byte_to_bits(b):
        return [bool((b >> i) & 1) for i in range(7, -1, -1)]
