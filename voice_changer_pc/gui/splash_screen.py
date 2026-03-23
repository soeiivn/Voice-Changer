from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class SplashScreen(QWidget):

    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # ===== 布局 =====
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # ===== 标题 =====
        self.title = QLabel("🎧 Voice Changer Pro")
        self.title.setFont(QFont("Arial", 20, QFont.Bold))
        self.title.setAlignment(Qt.AlignCenter)

        # ===== 状态 =====
        self.status = QLabel("Initializing...")
        self.status.setAlignment(Qt.AlignCenter)

        # ===== 进度条 =====
        self.progress = QProgressBar()
        self.progress.setFixedWidth(300)
        self.progress.setValue(0)

        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addWidget(self.status)
        layout.addSpacing(10)
        layout.addWidget(self.progress)

        # ===== 样式（重点）=====
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

        # ===== 进度模拟 =====
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_progress)
        self.timer.start(30)

        self.value = 0

    def _update_progress(self):
        self.value += 1
        self.progress.setValue(self.value)

        # 模拟加载阶段
        if self.value < 30:
            self.status.setText("Loading Audio Engine...")
        elif self.value < 60:
            self.status.setText("Initializing DSP Modules...")
        elif self.value < 90:
            self.status.setText("Preparing UI...")
        else:
            self.status.setText("Starting...")

        if self.value >= 100:
            self.timer.stop()
            self.close()