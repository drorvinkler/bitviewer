from math import ceil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QPixmap, QImage, QPalette, QPaintEvent
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollBar,
    QHBoxLayout,
    QGraphicsView,
    QGraphicsScene,
)

from app import App
from bitmap_creator import BitmapCreator

_BITMAP_THRESHOLD = 3


class BitsWidget(QWidget):
    def __init__(self, bit_size, row_width, grid_size) -> None:
        super().__init__()
        self._app = App()
        self._bit_size = bit_size
        self._row_width = row_width
        self._grid_size = grid_size
        self._one_color = Qt.blue
        self._zero_color = Qt.white
        self._painting = False
        self._last_painted_bitmap = None

        self._bits_area = QWidget()
        self._bits_canvas = QGraphicsScene()
        self._bits_canvas_holder = QGraphicsView(self._bits_canvas)
        self._bits_canvas_holder.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._bits_canvas_holder.setBackgroundBrush(
            QBrush(
                self._bits_area.palette().color(QPalette.ColorRole.Background),
                Qt.SolidPattern,
            )
        )
        self._bits_canvas_holder.setStyleSheet("border: 0px")

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
        inner_layout.addWidget(self._bits_canvas_holder, stretch=1)
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
        return (
            self._bits_area.width()
            if self._bit_size > _BITMAP_THRESHOLD
            else self._bits_canvas_holder.width() - 2
        )

    @property
    def _bits_area_height(self):
        return (
            self._bits_area.height()
            if self._bit_size > _BITMAP_THRESHOLD
            else self._bits_canvas_holder.height() - 2
        )

    @property
    def _num_rows(self):
        return ceil(self._app.num_bits / self._row_width)

    def load_file(self, filename):
        self._app.load_file(filename)

    def paintEvent(self, a0: QPaintEvent) -> None:
        super().paintEvent(a0)
        self._painting = True
        self._set_scrollbars()
        if self._bit_size > _BITMAP_THRESHOLD:
            self._paint_large_bits()
        else:
            self._paint_small_bits()

        self._draw_grid()
        self._painting = False

    def _paint_large_bits(self):
        self._bits_canvas_holder.hide()
        self._bits_area.show()

        self._app.draw(
            self._row_width,
            self._h_scrollbar.value(),
            self._v_scrollbar.value(),
            self._bits_area_height // self._bit_size,
            self._bits_area_width // self._bit_size,
            self._draw_bit,
        )

    def _paint_small_bits(self):
        self._bits_area.hide()
        self._bits_canvas_holder.show()

        visible_columns = self._bits_area_width // self._bit_size
        visible_rows = self._bits_area_height // self._bit_size
        bc = BitmapCreator(
            min(self._row_width * self._bit_size, visible_columns * self._bit_size),
            min(
                (self._app.num_bits // self._bit_size) * self._bit_size,
                visible_rows * self._bit_size,
            ),
            self._bit_size,
        )
        self._app.draw(
            self._row_width,
            self._h_scrollbar.value(),
            self._v_scrollbar.value(),
            visible_rows,
            visible_columns,
            bc.add_bit,
        )
        bitmap = bc.finalize()
        if bitmap != self._last_painted_bitmap:
            # Ugly hack to avoid an endless loop of firing the paintEvent of
            # the bits canvas, which then fires this paintEvent and so on
            self._draw_bitmap(bitmap, bc.row_width)
            # TODO: Paint remainder of bits in case all rows are shown and self._num_bits % self._row_width != 0
            self._last_painted_bitmap = bitmap

    def _draw_bit(self, x, y, bit):
        painter = QPainter(self)
        painter.setPen(
            QPen(Qt.black if self._bit_size > 2 else Qt.transparent, 1, Qt.SolidLine)
        )
        painter.setBrush(
            QBrush(self._one_color if bit else self._zero_color, Qt.SolidPattern)
        )
        painter.drawRect(
            x * self._bit_size, y * self._bit_size, self._bit_size, self._bit_size
        )

    def _draw_bitmap(self, data: bytes, row_width: int):
        pixmap = self._create_pixmap(data, row_width)
        self._bits_canvas.clear()
        self._bits_canvas.setSceneRect(0, 0, pixmap.width(), pixmap.height())
        self._bits_canvas.addPixmap(pixmap)

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

    def _create_pixmap(self, data: bytes, row_width: int):
        pixmap = QPixmap.fromImage(
            QImage(
                data,
                row_width * 8,
                len(data) // row_width,
                row_width,
                QImage.Format_Mono,
            )
        )
        mask = pixmap.createMaskFromColor(Qt.white, Qt.MaskOutColor)
        p = QPainter(pixmap)
        p.setPen(self._one_color)
        p.drawPixmap(pixmap.rect(), mask, mask.rect())
        p.end()
        mask = pixmap.createMaskFromColor(Qt.black, Qt.MaskOutColor)
        p = QPainter(pixmap)
        p.setPen(self._zero_color)
        p.drawPixmap(pixmap.rect(), mask, mask.rect())
        p.end()
        return pixmap

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
