import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# 👉 项目根目录 Project
ROOT_DIR = Path(__file__).resolve().parent.parent
qss_path = Path(__file__).parent / "style.qss"

# 👉 加入 Python 路径
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# 👉 导入模块
try:
    from voice_changer_pc.controller.engine_controller import EngineController
    from voice_changer_pc.gui.main_window import MainWindow
    from voice_changer_pc.gui.splash_screen import SplashScreen
    print("Imports successful!")
except ImportError as e:
    print(f"Import error: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Voice Changer PC")

    # =========================
    # 🎨 加载 QSS（修复路径问题）
    # =========================
    try:
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        else:
            print("QSS not found:", qss_path)
    except Exception as e:
        print("QSS load failed:", e)

    # =========================
    # 🚀 启动页
    # =========================
    splash = SplashScreen()
    splash.show()

    # 👉 防止被GC（非常关键）
    app.splash = splash
    app.main_window = None
    app.controller = None

    # =========================
    # 🧠 延迟启动主程序
    # =========================
    def start_main():
        print("Starting main window...")

        app.controller = EngineController()
        app.main_window = MainWindow(controller=app.controller)

        app.main_window.show()

    # 👉 3秒后启动主窗口（可改2秒）
    QTimer.singleShot(3000, start_main)

    return app.exec_()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("🔥 Main crash:", e)