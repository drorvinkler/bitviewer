from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QSpinBox,
)


class SettingsDialog(QDialog):
    def __init__(self, parent, max_bit_size) -> None:
        super().__init__(parent, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)

        self.setWindowTitle("Settings")
        self._max_bytes_spin_box = QSpinBox()
        self._min_size_bit_border_spin_box = QSpinBox()

        outer_layout = QVBoxLayout()
        outer_layout.addWidget(self._create_main(max_bit_size))
        outer_layout.addWidget(self._create_footer())

        self.setLayout(outer_layout)

    @property
    def max_bytes(self) -> int:
        return self._max_bytes_spin_box.value()

    @max_bytes.setter
    def max_bytes(self, m: int):
        self._max_bytes_spin_box.setValue(m)

    @property
    def min_bit_size_borders(self) -> int:
        return self._min_size_bit_border_spin_box.value()

    @min_bit_size_borders.setter
    def min_bit_size_borders(self, m: int):
        self._min_size_bit_border_spin_box.setValue(m)

    def _create_main(self, max_bit_size):
        main = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self._create_max_bytes())
        layout.addWidget(self._create_bit_borders(max_bit_size))
        main.setLayout(layout)
        return main

    def _create_footer(self):
        footer = QWidget()
        layout = QHBoxLayout()

        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self._ok_clicked)
        layout.addWidget(ok_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self._cancel_clicked)
        layout.addWidget(cancel_button)

        footer.setLayout(layout)
        return footer

    def _create_max_bytes(self):
        w = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Max bytes to read: "))

        self._max_bytes_spin_box.setMinimum(1)
        self._max_bytes_spin_box.setMaximum(2 ** 30)
        layout.addWidget(self._max_bytes_spin_box)

        w.setLayout(layout)
        return w

    def _create_bit_borders(self, max_bit_size):
        w = QWidget()
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Min size for bit borders: "))

        self._min_size_bit_border_spin_box.setMinimum(2)
        self._min_size_bit_border_spin_box.setMaximum(max_bit_size)
        layout.addWidget(self._min_size_bit_border_spin_box)

        w.setLayout(layout)
        return w

    def _ok_clicked(self):
        self.accept()

    def _cancel_clicked(self):
        self.reject()
