"""PyInstaller entry point.

Must live outside the mis_pulse_client package and import it by absolute
name. Pointing PyInstaller directly at mis_pulse_client/main.py instead
freezes it as a bare top-level script with no parent package, which breaks
every relative import inside the package ("attempted relative import with
no known parent package").
"""

import sys

from mis_pulse_client.main import main

if __name__ == "__main__":
    sys.exit(main())
