import os

APP_NAME = "FCG MIS Pulse"
APP_VERSION = "0.1.0"

DEFAULT_BASE_URL = "http://127.0.0.1:8420"
BASE_URL = os.environ.get("MIS_PULSE_SERVER_URL", DEFAULT_BASE_URL)

KEYRING_SERVICE = "fcg-mis-pulse"
