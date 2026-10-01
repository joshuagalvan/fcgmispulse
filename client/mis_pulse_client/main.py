import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from . import config
from .local_client import LocalClient
from .theme import STYLESHEET, build_palette
from .widgets.main_window import MainWindow

# Must be set before QApplication is constructed. Fixes garbled/corrupted
# text specifically in edit-style widgets (QLineEdit/QComboBox/QDateEdit)
# on Windows displays using fractional scaling (125%/150%, very common on
# laptops) -- Qt's default "Round" policy can round each widget's effective
# scale differently, corrupting their internal text-metric layout. Labels
# and buttons use a simpler text-painting path and aren't affected, which
# is why only the input fields looked broken.
QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setPalette(build_palette())
    app.setStyleSheet(STYLESHEET)

    client = LocalClient()

    window = MainWindow(client)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
