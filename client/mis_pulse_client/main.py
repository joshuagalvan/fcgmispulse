import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from . import config, server_config
from .api_client import ApiClient, ApiError
from .auth import token_store
from .auth.login_dialog import LoginDialog
from .theme import STYLESHEET
from .widgets.main_window import MainWindow


def _check_server_version(api: ApiClient):
    try:
        info = api.server_version()
    except ApiError:
        return
    min_version = info.get("min_client_version")
    if min_version and min_version > config.APP_VERSION:
        QMessageBox.warning(
            None,
            "Update available",
            f"A newer version of {config.APP_NAME} ({min_version}) is available. "
            "Some features may not work correctly until you update.",
        )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setStyleSheet(STYLESHEET)

    api = ApiClient(server_config.load_server_url())

    user = None
    saved_token = token_store.load_token()
    if saved_token:
        api.token = saved_token
        try:
            user = api.me()
        except ApiError:
            api.token = None
            token_store.clear_token()

    if user is None:
        dialog = LoginDialog(api)
        if dialog.exec() != LoginDialog.Accepted:
            return 0
        user = dialog.user

    _check_server_version(api)

    window = MainWindow(api, user)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
