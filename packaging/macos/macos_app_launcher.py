from __future__ import annotations

import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

from streamlit.web import bootstrap
from streamlit.web.bootstrap import load_config_options


def resource_root() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parents[2]


def find_port(start: int = 8501, end: int = 8599) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No available local port found.")


def open_browser(port: int) -> None:
    time.sleep(3)
    webbrowser.open(f"http://localhost:{port}")


def main() -> int:
    root = resource_root()
    sys.path.insert(0, str(root))

    os.environ.setdefault("PYTHONUTF8", "1")
    os.environ.setdefault("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false")

    app_path = root / "app.py"
    port = find_port()
    flag_options = {
        "global.developmentMode": False,
        "server.address": "127.0.0.1",
        "server.port": port,
        "server.headless": True,
        "browser.serverAddress": "localhost",
        "browser.serverPort": port,
        "browser.gatherUsageStats": False,
    }
    load_config_options(flag_options)

    threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    bootstrap.run(str(app_path), False, [], flag_options)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
