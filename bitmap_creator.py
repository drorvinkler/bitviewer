from math import ceil


class BitmapCreator:
    def __init__(self, row_width, height, bit_size) -> None:
        super().__init__()
        self._bit_size = bit_size
        self._row_width = ceil(row_width / 8)
        self._height = height
        self._data = []
        self._curr = 0
        self._index = 0
        self._y = None
        self._remainder = []

    @property
    def remainder(self):
        return self._remainder, self._index

    def add_bit(self, _, y, bit):
        if self._y is not None and y != self._y:
            self._pad()
            self._duplicate_line_to_bit_size()

        if len(self._data) // self._row_width == self._height:
            return

        if self._index // (self._row_width * 8) > y:
            return

        for _ in range(self._bit_size):
            self._add_bit(bit)
            if not self._index % (self._row_width * 8):
                break
        self._y = y

    def finalize(self):
        self._pad()
        if len(self._data) % self._row_width:
            return self._seperate_remainder()

        self._duplicate_line_to_bit_size()
        return bytes(self._data)

    def _pad(self):
        padding = -self._index % 8
        if not padding:
            return

        self._curr <<= padding
        self._index += padding
        self._data.append(self._curr)
        self._curr = 0

    def _add_bit(self, bit):
        self._curr <<= 1
        self._curr |= bit
        self._index += 1
        if not self._index % 8:
            self._data.append(self._curr)
            self._curr = 0

    def _duplicate_line_to_bit_size(self):
        curr_height = len(self._data) // self._row_width
        num_duplicates = min((self._bit_size - 1), self._height - curr_height)
        self._data.extend(self._data[-self._row_width :] * num_duplicates)

    def _seperate_remainder(self):
        end = (len(self._data) // self._row_width) * self._row_width
        self._remainder = self._data[end:]
        return bytes(self._data[:end])
