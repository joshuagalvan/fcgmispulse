from PySide6.QtWidgets import QMainWindow, QTabWidget

from .. import config
from .entries_list_view import EntriesListView
from .entry_form import EntryForm
from .manage_stores_dialog import ManageStoresDialog


class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.client = client

        self.setWindowTitle(config.APP_NAME)
        self.resize(1280, 840)
        self.setMinimumSize(1000, 680)

        self.entry_form = EntryForm(client)
        self.entries_list = EntriesListView(client)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.entry_form, "New Entry")
        self.tabs.addTab(self.entries_list, "All Entries")
        self.setCentralWidget(self.tabs)

        self.entry_form.saved.connect(lambda _entry: self.entries_list.refresh())
        self.entry_form.status_message.connect(self._show_status)
        self.entries_list.status_message.connect(self._show_status)
        self.entries_list.edit_requested.connect(self._edit_entry)

        self._build_menu()
        self.statusBar().showMessage("Ready", 3000)

    def _build_menu(self):
        manage_menu = self.menuBar().addMenu("&Manage")
        manage_action = manage_menu.addAction("Stores / Departments / Area Managers...")
        manage_action.triggered.connect(self._open_manage_stores)

    def _open_manage_stores(self):
        dialog = ManageStoresDialog(self.client, self)
        dialog.exec()
        self.entry_form.reload_lookups()

    def _edit_entry(self, entry: dict):
        self.entry_form.load_entry(entry)
        self.tabs.setCurrentWidget(self.entry_form)

    def _show_status(self, message: str):
        self.statusBar().showMessage(message, 5000)
