import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from gui.main_window import MainWindow

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Voice Changer PC")

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
