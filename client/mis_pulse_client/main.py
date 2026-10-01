import sys

from PySide6.QtWidgets import QApplication

from . import config
from .local_client import LocalClient
from .theme import STYLESHEET
from .widgets.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setStyleSheet(STYLESHEET)

    client = LocalClient()

    window = MainWindow(client)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
