import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# 获取当前文件的绝对路径的父目录（即voice-changer-pc目录）
CURRENT_DIR = Path(__file__).resolve().parent
print(f"Current directory: {CURRENT_DIR}")  # 调试用，看看路径是否正确

# 将项目根目录添加到系统路径
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# 现在应该可以导入了
try:
    from controller.engine_controller import EngineController
    from gui.main_window import MainWindow
    print("Imports successful!")  # 调试用
except ImportError as e:
    print(f"Import error: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Voice Changer PC")

    controller = EngineController()
    window = MainWindow(controller=controller)
    window.show()

    return app.exec_()

if __name__ == "__main__":
    raise SystemExit(main())
