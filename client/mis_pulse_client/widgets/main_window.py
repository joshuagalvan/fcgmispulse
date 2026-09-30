from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from .. import config
from ..api_client import ApiClient
from ..async_utils import run_async
from ..auth import token_store
from .entries_list_view import EntriesListView
from .entry_form import EntryForm
from .manage_stores_dialog import ManageStoresDialog


class MainWindow(QMainWindow):
    def __init__(self, api: ApiClient, user: dict):
        super().__init__()
        self.api = api
        self.user = user

        self.setWindowTitle(f"{config.APP_NAME} — {user['display_name']}")
        self.resize(1280, 840)
        self.setMinimumSize(1000, 680)

        self.entry_form = EntryForm(api, current_user_name=user.get("display_name"))
        self.entries_list = EntriesListView(api)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.entry_form, "New Entry")
        self.tabs.addTab(self.entries_list, "All Entries")
        self.setCentralWidget(self.tabs)

        self.entry_form.saved.connect(lambda _entry: self.entries_list.refresh())
        self.entry_form.status_message.connect(self._show_status)
        self.entries_list.status_message.connect(self._show_status)
        self.entries_list.edit_requested.connect(self._edit_entry)

        self._build_menu()
        self.statusBar().showMessage(f"Logged in as {user['display_name']}", 5000)

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        log_out_action = file_menu.addAction("Log Out")
        log_out_action.triggered.connect(self._log_out)
        exit_action = file_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)

        if self.user.get("is_admin"):
            admin_menu = self.menuBar().addMenu("&Admin")
            manage_action = admin_menu.addAction("Manage Stores / Departments / Area Managers...")
            manage_action.triggered.connect(self._open_manage_stores)

    def _open_manage_stores(self):
        dialog = ManageStoresDialog(self.api, self)
        dialog.exec()
        self.entry_form.reload_lookups()

    def _edit_entry(self, entry: dict):
        self.entry_form.load_entry(entry)
        self.tabs.setCurrentWidget(self.entry_form)

    def _show_status(self, message: str):
        self.statusBar().showMessage(message, 5000)

    def _log_out(self):
        token_store.clear_token()
        run_async(self.api.logout, on_success=lambda _=None: None, on_error=lambda _=None: None)
        QMessageBox.information(self, "Logged out", "Restart the app to log in again.")
        self.close()
