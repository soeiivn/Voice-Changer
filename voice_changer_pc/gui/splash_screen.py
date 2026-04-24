from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel("🎧 Voice Changer PC")
        self.title.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))  # 推荐使用微软雅黑
        self.title.setAlignment(Qt.AlignCenter)

        self.status = QLabel("正在初始化...")
        self.status.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setFixedWidth(300)
        self.progress.setValue(0)

        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addWidget(self.status)
        layout.addSpacing(10)
        layout.addWidget(self.progress)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00aaff;
                width: 20px;
            }
        """)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(30)

        self.value = 0

    def _update_progress(self):
        self.value += 1
        self.progress.setValue(self.value)

        if self.value < 30:
            self.status.setText("正在加载音频引擎...")
        elif self.value < 60:
            self.status.setText("正在初始化 DSP 模块...")
        elif self.value < 90:
            self.status.setText("正在准备界面...")
        else:
            self.status.setText("启动中...")

        if self.value >= 100:
            self.timer.stop()
            self.close()