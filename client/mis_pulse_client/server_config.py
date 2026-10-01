"""Remembers which server URL to use, per machine.

The server address will change again once this is hosted online (it's
currently a temporary LAN IP), and different machines may need pointing
at different addresses in the meantime -- so this is kept editable from
the login screen and persisted locally (QSettings -> Windows registry /
platform-native store), rather than baked into the build.
"""

from PySide6.QtCore import QSettings

from . import config

_ORG = "FCG"
_APP = "MIS Pulse"
_KEY = "server_url"


def load_server_url() -> str:
    settings = QSettings(_ORG, _APP)
    return settings.value(_KEY, config.BASE_URL)


def save_server_url(url: str) -> None:
    settings = QSettings(_ORG, _APP)
    settings.setValue(_KEY, url)
