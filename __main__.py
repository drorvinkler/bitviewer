import sys

from PyQt5.QtWidgets import QApplication

from qt_classes.main_window import MainWindow

MAX_BYTES = 10 ** 6

app = QApplication(sys.argv)
window = MainWindow()
app.exec()
