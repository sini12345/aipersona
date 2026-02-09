"""
Persona Træningsplatform - Launcher
Starter webserveren og åbner browseren automatisk.
Bruges til at bygge .exe med PyInstaller.
"""

import webbrowser
import threading
import sys
import os

# Sørg for at data-filer kan findes i bundled exe
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    os.chdir(BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(BASE_DIR)


def open_browser():
    """Åbner browseren efter kort forsinkelse."""
    import time
    time.sleep(1.5)
    webbrowser.open("http://localhost:5000")


if __name__ == "__main__":
    # Åbn browser i baggrunden
    threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask server
    from web import app
    print("\n  Persona Træningsplatform")
    print("  Browseren åbner automatisk...")
    print("  Luk dette vindue for at stoppe.\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
