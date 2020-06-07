from typing import Callable

from bits import Bits

DRAW_BIT_TYPE = Callable[[int, int, bool], None]


class App:
    def __init__(self) -> None:
        super().__init__()
        self._data = None

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
