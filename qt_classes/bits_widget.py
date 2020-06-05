from math import ceil

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollBar, QHBoxLayout

from app import App


class BitsWidget(QWidget):
    def __init__(self, bit_size, row_width, grid_size) -> None:
        super().__init__()
        self._app = App()
        self._bit_size = bit_size
        self._row_width = row_width
        self._grid_size = grid_size
        self._painting = False

        self._bits_area = QWidget()

        self._h_scrollbar = QScrollBar(orientation=Qt.Horizontal)
        self._h_scrollbar.setMinimum(0)
        self._h_scrollbar.valueChanged.connect(self._on_scrollbar_change)
        self._h_scrollbar.hide()
        self._v_scrollbar = QScrollBar(orientation=Qt.Vertical)
        self._v_scrollbar.setMinimum(0)
        self._v_scrollbar.valueChanged.connect(self._on_scrollbar_change)
        self._v_scrollbar.hide()

        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)
        inner_layout.addWidget(self._bits_area, stretch=1)
        inner_layout.addWidget(self._h_scrollbar)
        inner_widget = QWidget()
        inner_widget.setLayout(inner_layout)

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(inner_widget, stretch=1)
        outer_layout.addWidget(self._v_scrollbar)
        self.setLayout(outer_layout)

    @property
    def bit_size(self) -> int:
        return self._bit_size

    @bit_size.setter
    def bit_size(self, size: int):
        self._bit_size = size

    @property
    def row_width(self) -> int:
        return self._row_width

    @row_width.setter
    def row_width(self, width: int):
        self._row_width = width

    @property
    def grid_size(self) -> int:
        return self._grid_size

    @grid_size.setter
    def grid_size(self, size: int):
        self._grid_size = size

    @property
    def _bits_area_width(self):
        return self._bits_area.size().width()

    @property
    def _bits_area_height(self):
        return self._bits_area.size().height()

    @property
    def _num_rows(self):
        return ceil(self._app.num_bits / self._row_width)

    def load_file(self, filename):
        self._app.load_file(filename)

    def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
        super().paintEvent(a0)
        self._painting = True
        self._set_scrollbars()
        self._app.draw(
            self._row_width,
            self._h_scrollbar.value(),
            self._v_scrollbar.value(),
            self._bits_area_height // self._bit_size,
            self._bits_area_width // self._bit_size,
            self._draw_bit,
        )
        self._draw_grid()
        self._painting = False

    def _draw_bit(self, x, y, bit):
        painter = QPainter(self)
        painter.setPen(
            QPen(Qt.black if self._bit_size > 2 else Qt.transparent, 1, Qt.SolidLine)
        )
        painter.setBrush(QBrush(Qt.blue if bit else Qt.white, Qt.SolidPattern))
        painter.drawRect(
            x * self._bit_size, y * self._bit_size, self._bit_size, self._bit_size
        )

    def _draw_grid(self):
        if self._grid_size == 0:
            return

        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))

        right = min(
            (self._row_width - self._h_scrollbar.value()) * self._bit_size,
            self._bits_area_width,
        )
        bottom = min(
            (self._num_rows - self._v_scrollbar.value()) * self._bit_size,
            self._bits_area_height,
        )
        self._draw_h_grid(painter, right, bottom)
        self._draw_v_grid(painter, right, bottom)

    def _draw_h_grid(self, painter, right, bottom):
        start_offset = -self._h_scrollbar.value() % self._grid_size
        start = start_offset * self._bit_size
        for x in range(start, right + 1, self._grid_size * self._bit_size):
            painter.drawLine(x, 0, x, bottom)

    def _draw_v_grid(self, painter, right, bottom):
        start_offset = -self._v_scrollbar.value() % self._grid_size
        start = start_offset * self._bit_size
        for y in range(start, bottom + 1, self._grid_size * self._bit_size):
            painter.drawLine(0, y, right, y)

    def _set_scrollbars(self):
        self._set_h_scrollbar()
        v_visibility_changed = self._set_v_scrollbar()
        if v_visibility_changed:
            h_visibility_changed = self._set_h_scrollbar()
            if h_visibility_changed:
                self._set_v_scrollbar()

    def _set_h_scrollbar(self):
        h_scroll_max = self._calc_h_scrollbar_max()
        was_visible = self._h_scrollbar.isVisible()
        if h_scroll_max > 0:
            self._h_scrollbar.setMaximum(h_scroll_max)
            self._h_scrollbar.show()
            return not was_visible
        else:
            self._h_scrollbar.setValue(0)
            self._h_scrollbar.hide()
            return was_visible

    def _set_v_scrollbar(self):
        v_scroll_max = self._calc_v_scrollbar_max()
        was_visible = self._v_scrollbar.isVisible()
        if v_scroll_max > 0:
            self._v_scrollbar.setMaximum(v_scroll_max)
            self._v_scrollbar.show()
            return not was_visible
        else:
            self._v_scrollbar.setValue(0)
            self._v_scrollbar.hide()
            return was_visible

    def _calc_h_scrollbar_max(self):
        return self._row_width - (self._bits_area_width // self.bit_size)

    def _calc_v_scrollbar_max(self):
        visible_rows = self._bits_area_height // self.bit_size
        return self._num_rows - visible_rows

    def _on_scrollbar_change(self):
        if not self._painting:
            self.repaint()
