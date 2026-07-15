"""
FixBoard Miner Manager - Application Main Entrypoint
Initializes PySide6 (Qt6) QApplication, loads custom dark mode styling, and launches the main manager window.
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

# Ensure correct package resolving paths
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from gui.main_window import MainWindow

def load_stylesheet(app: QApplication):
    """Loads and compiles custom QSS stylesheet."""
    qss_path = BASE_DIR / "resources" / "style.qss"
    if qss_path.exists():
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"[WARN] Failed to load stylesheet: {e}")
    else:
        print("[WARN] style.qss stylesheet not found.")

def main():
    # Initialize PySide6 application context
    app = QApplication(sys.argv)

    # Configure RTL support and generic fonts if desired
    # By default, PySide6 supports RTL and RTL layouts out-of-the-box
    app.setLayoutDirection(Qt.RightToLeft)

    # Set application generic font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Load Glassmorphic dark styling
    load_stylesheet(app)

    # Launch main application orchestration panel
    window = MainWindow()
    window.show()

    # Exit application loop safely
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
