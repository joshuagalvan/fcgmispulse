from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from .. import server_config
from ..api_client import ApiClient, ApiError
from ..async_utils import run_async
from ..config import APP_NAME
from . import token_store


class LoginDialog(QDialog):
    def __init__(self, api: ApiClient, parent=None):
        super().__init__(parent)
        self.api = api
        self.user: dict | None = None

        self.setWindowTitle(APP_NAME)
        self.setModal(True)
        self.setMinimumWidth(420)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(font.pointSize() + 6)
        font.setBold(True)
        title.setFont(font)

        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("e.g. albert")
        self.username_edit.setMinimumWidth(260)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.returnPressed.connect(self._attempt_login)

        self.server_edit = QLineEdit(server_config.load_server_url())
        self.server_edit.setPlaceholderText("http://<server address>:8420")

        form = QFormLayout()
        form.addRow("Username", self.username_edit)
        form.addRow("Password", self.password_edit)
        form.addRow("Server", self.server_edit)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #c0392b;")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        self.login_button = QPushButton("Log In")
        self.login_button.setObjectName("primaryButton")
        self.login_button.setDefault(True)
        self.login_button.clicked.connect(self._attempt_login)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self.error_label)
        layout.addWidget(self.login_button)

        self.username_edit.setFocus()

    def _attempt_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        server_url = self.server_edit.text().strip()
        if not server_url:
            self._show_error("Enter the server address.")
            return
        if not username or not password:
            self._show_error("Enter your username and password.")
            return

        self.api.base_url = server_url.rstrip("/")
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        run_async(
            self.api.login,
            username,
            password,
            on_success=self._on_login_success,
            on_error=self._on_login_error,
        )

    def _on_login_success(self, data: dict):
        self.user = data["user"]
        token_store.save_token(data["token"])
        server_config.save_server_url(self.api.base_url)
        self.accept()

    def _on_login_error(self, message: str):
        self.login_button.setEnabled(True)
        self.login_button.setText("Log In")
        self._show_error(message)

    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
