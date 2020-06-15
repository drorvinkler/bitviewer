import json
from dataclasses import asdict
from os.path import exists

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
from qt_classes.settings_dialog import SettingsDialog
from settings import Settings

_SETTINGS_FILE = "settings.json"
_MAX_BIT_SIZE = 100


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        settings = self._load_settings()
        self._settings_dialog = SettingsDialog(self, _MAX_BIT_SIZE)
        self._init_settings(settings)

        self._header = QWidget()
        self._offset_spin_box = QSpinBox()
        self._row_width_spin_box = QSpinBox()
        self._bit_size_spin_box = QSpinBox()
        self._grid_width_spin_box = QSpinBox()
        self._grid_h_offset_spin_box = QSpinBox()
        self._grid_height_spin_box = QSpinBox()
        self._grid_v_offset_spin_box = QSpinBox()
        self._bits_widget = BitsWidget(
            0,
            settings.bit_size,
            settings.row_width,
            0,
            0,
            self._settings_dialog.min_bit_size_borders - 1,
        )

        self._init_main_window(settings.row_width, settings.bit_size, 0, 0)
        self._create_menu()

        self.show()

    def _init_main_window(self, row_width, bit_size, grid_width, grid_height):
        self.setWindowTitle("Bit Viewer")
        self.setGeometry(100, 100, 500, 500)
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        self._init_header(row_width, bit_size, grid_width, grid_height)
        layout.addWidget(self._header)
        layout.addWidget(self._bits_widget, stretch=1)
        root.setLayout(layout)

    def _create_menu(self):
        open_file = QAction(text="&Open", parent=self)
        open_file.setShortcut("Ctrl+O")
        open_file.triggered.connect(self._on_open_file)

        settings = QAction(text="&Setting", parent=self)
        settings.triggered.connect(self._open_settings)

        file_menu = self.menuBar().addMenu("&File")
        file_menu.addAction(open_file)
        file_menu.addAction(settings)

    def _init_settings(self, settings):
        self._settings_dialog.max_bytes = settings.max_bytes
        self._settings_dialog.min_bit_size_borders = settings.bit_borders_start

    def _init_header(self, row_width, bit_size, grid_width, grid_height):
        layout = QHBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(QLabel(text="Offset:"))
        self._offset_spin_box.setMinimum(0)
        self._offset_spin_box.setMaximum(102400)
        self._offset_spin_box.setValue(0)
        self._offset_spin_box.valueChanged.connect(self._on_offset_change)
        layout.addWidget(self._offset_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Row Width:"))
        self._row_width_spin_box.setMinimum(1)
        self._row_width_spin_box.setMaximum(102400)
        self._row_width_spin_box.setValue(row_width)
        self._row_width_spin_box.valueChanged.connect(self._on_row_width_change)
        layout.addWidget(self._row_width_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Bit Size:"))
        self._bit_size_spin_box.setMinimum(1)
        self._bit_size_spin_box.setMaximum(_MAX_BIT_SIZE)
        self._bit_size_spin_box.setValue(bit_size)
        self._bit_size_spin_box.valueChanged.connect(self._on_bit_size_change)
        layout.addWidget(self._bit_size_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Grid Width:"))
        self._grid_width_spin_box.setMinimum(0)
        self._grid_width_spin_box.setMaximum(10240)
        self._grid_width_spin_box.setValue(grid_width)
        self._grid_width_spin_box.valueChanged.connect(self._on_grid_width_change)
        layout.addWidget(self._grid_width_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Offset:"))
        self._grid_h_offset_spin_box.setMinimum(0)
        self._grid_h_offset_spin_box.setMaximum(
            max(self._grid_width_spin_box.value() - 1, 0)
        )
        self._grid_h_offset_spin_box.setValue(0)
        self._grid_h_offset_spin_box.valueChanged.connect(self._on_grid_h_offset_change)
        layout.addWidget(self._grid_h_offset_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Grid Height:"))
        self._grid_height_spin_box.setMinimum(0)
        self._grid_height_spin_box.setMaximum(10240)
        self._grid_height_spin_box.setValue(grid_height)
        self._grid_height_spin_box.valueChanged.connect(self._on_grid_height_change)
        layout.addWidget(self._grid_height_spin_box)

        layout.addSpacing(10)

        layout.addWidget(QLabel(text="Offset:"))
        self._grid_v_offset_spin_box.setMinimum(0)
        self._grid_v_offset_spin_box.setMaximum(
            max(self._grid_height_spin_box.value() - 1, 0)
        )
        self._grid_v_offset_spin_box.setValue(0)
        self._grid_v_offset_spin_box.valueChanged.connect(self._on_grid_v_offset_change)
        layout.addWidget(self._grid_v_offset_spin_box)

        layout.addStretch()
        self._header.setLayout(layout)

    def _on_offset_change(self):
        self._bits_widget.offset = self._offset_spin_box.value()
        self._bits_widget.repaint()

    def _on_row_width_change(self):
        self._bits_widget.row_width = self._row_width_spin_box.value()
        self._bits_widget.repaint()

    def _on_bit_size_change(self):
        self._bits_widget.bit_size = self._bit_size_spin_box.value()
        self._bits_widget.repaint()

    def _on_grid_width_change(self):
        self._bits_widget.grid_width = self._grid_width_spin_box.value()
        self._grid_h_offset_spin_box.setMaximum(
            max(self._grid_width_spin_box.value() - 1, 0)
        )
        self._bits_widget.repaint()

    def _on_grid_h_offset_change(self):
        self._bits_widget.grid_h_offset = self._grid_h_offset_spin_box.value()
        self._bits_widget.repaint()

    def _on_grid_height_change(self):
        self._bits_widget.grid_height = self._grid_height_spin_box.value()
        self._grid_v_offset_spin_box.setMaximum(
            max(self._grid_height_spin_box.value() - 1, 0)
        )
        self._bits_widget.repaint()

    def _on_grid_v_offset_change(self):
        self._bits_widget.grid_v_offset = self._grid_v_offset_spin_box.value()
        self._bits_widget.repaint()

    def _on_open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File")
        if not filename:
            return

        self._bits_widget.load_file(filename, self._settings_dialog.max_bytes)
        self._bits_widget.repaint()

    def _open_settings(self):
        accepted = self._settings_dialog.exec()
        if accepted:
            settings = Settings(
                max_bytes=self._settings_dialog.max_bytes,
                bit_borders_start=self._settings_dialog.min_bit_size_borders,
            )
            self._bits_widget.set_bit_border_threshold(settings.bit_borders_start - 1)
            self._save_settings(settings)
        else:
            settings = self._load_settings()
            self._settings_dialog.max_bytes = settings.max_bytes
            self._settings_dialog.min_bit_size_borders = settings.bit_borders_start

    def closeEvent(self, a0) -> None:
        settings = Settings(
            max_bytes=self._settings_dialog.max_bytes,
            bit_borders_start=self._settings_dialog.min_bit_size_borders,
            row_width=self._bits_widget.row_width,
            bit_size=self._bits_widget.bit_size,
        )
        self._save_settings(settings)
        super().closeEvent(a0)

    @staticmethod
    def _load_settings():
        if not exists(_SETTINGS_FILE):
            return Settings()

        with open(_SETTINGS_FILE) as f:
            settings = Settings(**json.load(f))
        return settings

    @staticmethod
    def _save_settings(settings):
        with open(_SETTINGS_FILE, "w") as f:
            json.dump(asdict(settings), f, indent=2)
