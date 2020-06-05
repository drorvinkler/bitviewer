from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSpinBox,
    QAction,
    QFileDialog,
)

from qt_classes.bits_widget import BitsWidget

_DEFAULT_BIT_SIZE = 10
_DEFAULT_ROW_WIDTH = 80
_DEFAULT_GRID_SIZE = 0


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self._header = QWidget()
        self._row_width_spin_box = QSpinBox()
        self._bit_size_spin_box = QSpinBox()
        self._grid_size_spin_box = QSpinBox()
        self._bits_widget = BitsWidget(
            _DEFAULT_BIT_SIZE, _DEFAULT_ROW_WIDTH, _DEFAULT_GRID_SIZE
        )

        self._init_main_window()
        self._create_menu()
        self.show()

    def _init_main_window(self):
        self.setWindowTitle("Bit Viewer")
        self.setGeometry(100, 100, 500, 500)
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        self._init_header()
        layout.addWidget(self._header)
        layout.addWidget(self._bits_widget, stretch=1)
        root.setLayout(layout)

    def _create_menu(self):
        open_file = QAction(text="&Open", parent=self)
        open_file.triggered.connect(self._on_open_file)
        self.menuBar().addMenu("&File").addAction(open_file)

    def _init_header(self):
        layout = QHBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(QLabel(text="Row Width:"))
        self._row_width_spin_box.setMinimum(1)
        self._row_width_spin_box.setMaximum(102400)
        self._row_width_spin_box.setValue(_DEFAULT_ROW_WIDTH)
        self._row_width_spin_box.valueChanged.connect(self._on_row_width_change)
        layout.addWidget(self._row_width_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Bit Size:"))
        self._bit_size_spin_box.setMinimum(1)
        self._bit_size_spin_box.setMaximum(100)
        self._bit_size_spin_box.setValue(_DEFAULT_BIT_SIZE)
        self._bit_size_spin_box.valueChanged.connect(self._on_bit_size_change)
        layout.addWidget(self._bit_size_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Grid Size:"))
        self._grid_size_spin_box.setMinimum(0)
        self._grid_size_spin_box.setMaximum(10240)
        self._grid_size_spin_box.setValue(_DEFAULT_GRID_SIZE)
        self._grid_size_spin_box.valueChanged.connect(self._on_grid_size_change)
        layout.addWidget(self._grid_size_spin_box)

        layout.addStretch()
        self._header.setLayout(layout)

    def _on_bit_size_change(self):
        self._bits_widget.bit_size = self._bit_size_spin_box.value()
        self._bits_widget.repaint()

    def _on_row_width_change(self):
        self._bits_widget.row_width = self._row_width_spin_box.value()
        self._bits_widget.repaint()

    def _on_grid_size_change(self):
        self._bits_widget.grid_size = self._grid_size_spin_box.value()
        self._bits_widget.repaint()

    def _on_open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File")
        if not filename:
            return

        self._bits_widget.load_file(filename)
        self._bits_widget.repaint()
