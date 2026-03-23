from pathlib import Path
import sys
import os

# PyQt5 imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QSlider, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QGroupBox, QGridLayout, QFrame, QStackedWidget,
    QSplitter, QStatusBar, QTextEdit
)
from PyQt5.QtGui import (
    QPalette, QBrush, QPixmap, QFont, QLinearGradient, QColor, QIcon
)
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QUrl, QSize
)

# 👉 项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from voice_changer_pc.controller.engine_controller import EngineController
    from voice_changer_pc.gui.visualizer import VisualizerPanel
    from voice_changer_pc.gui.widgets import ControlPanel
    print("Main window imports successful!")
except ImportError as e:
    print(f"Main window import error: {e}")
    print(f"sys.path: {sys.path}")
    raise

# =========================
# 🏠 Home
# =========================
class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("HomePage")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._set_background_image()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🎧 Voice Changer Pro")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold;
            color: white;
        """)

        self.enter_btn = QPushButton("🚀 Enter Studio")
        self.enter_btn.setMinimumHeight(50)

        self.settings_btn = QPushButton("⚙ Settings")

        layout.addWidget(title)
        layout.addWidget(self.enter_btn)
        layout.addWidget(self.settings_btn)

    def _set_background_image(self):
        base_dir = Path(__file__).parent
        image_path = base_dir / "background.jpg"

        if image_path.exists():
            self.setStyleSheet(f"""
                QWidget#HomePage {{
                    border-image: url("{image_path.as_posix()}") 0 0 0 0 stretch stretch;
                }}
            """)
        else:
            print("背景图未找到:", image_path)

# =========================
# 🎛 Studio
# =========================
class StudioPage(QWidget):
    def __init__(self, control_panel, visualizer):
        super().__init__()

        layout = QVBoxLayout(self)

        nav = QHBoxLayout()
        self.back_btn = QPushButton("← Home")
        self.to_settings_btn = QPushButton("Settings")

        nav.addWidget(self.back_btn)
        nav.addStretch()
        nav.addWidget(self.to_settings_btn)

        layout.addLayout(nav)

        splitter = QSplitter()
        splitter.addWidget(control_panel)
        splitter.addWidget(visualizer)

        layout.addWidget(splitter)

# =========================
# ⚙ Settings
# =========================
class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)

        # ===== 顶部返回 =====
        self.back_btn = QPushButton("← Back")

        # ===== 左侧菜单 =====
        menu_layout = QVBoxLayout()
        self.btn_audio = QPushButton("🎧 Audio")
        self.btn_ui = QPushButton("🖥 UI")
        self.btn_help = QPushButton("📖 User Guide")
        self.btn_about = QPushButton("ℹ About")

        menu_layout.addWidget(self.btn_audio)
        menu_layout.addWidget(self.btn_ui)
        menu_layout.addWidget(self.btn_help)
        menu_layout.addWidget(self.btn_about)
        menu_layout.addStretch()

        # ===== 右侧内容 =====
        self.stack = QStackedWidget()

        self.page_audio = self._build_audio_page()
        self.page_ui = self._build_ui_page()
        self.page_help = self._build_help_page()
        self.page_about = self._build_about_page()

        self.stack.addWidget(self.page_audio)  # 0
        self.stack.addWidget(self.page_ui)     # 1
        self.stack.addWidget(self.page_help)   # 2
        self.stack.addWidget(self.page_about)  # 3

        # ===== 主体布局 =====
        body = QHBoxLayout()
        body.addLayout(menu_layout, 1)
        body.addWidget(self.stack, 3)

        root.addWidget(self.back_btn)
        root.addLayout(body)

        # ===== 绑定 =====
        self.btn_audio.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_ui.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_help.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_about.clicked.connect(lambda: self.stack.setCurrentIndex(3))

    # =========================
    # 🎧 Audio Settings
    # =========================
    def _build_audio_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("Audio Settings")
        title.setStyleSheet("font-size:18px;")

        device_select = QComboBox()
        device_select.addItems(["Default Microphone", "External Mic"])

        sample_rate = QComboBox()
        sample_rate.addItems(["16000 Hz", "44100 Hz", "48000 Hz"])

        layout.addWidget(title)
        layout.addWidget(QLabel("Input Device"))
        layout.addWidget(device_select)
        layout.addWidget(QLabel("Sample Rate"))
        layout.addWidget(sample_rate)
        layout.addStretch()

        return w

    # =========================
    # 🖥 UI Settings
    # =========================
    def _build_ui_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("UI Settings")
        title.setStyleSheet("font-size:18px;")

        theme = QComboBox()
        theme.addItems(["Dark (Default)", "Light"])

        layout.addWidget(title)
        layout.addWidget(QLabel("Theme"))
        layout.addWidget(theme)
        layout.addStretch()

        return w

    # =========================
    # 📖 使用说明（重点加分项）
    # =========================
    def _build_help_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("User Guide")
        title.setStyleSheet("font-size:18px;")

        text = QTextEdit()
        text.setReadOnly(True)

        text.setText(
            "1. Select a voice mode\n"
            "2. Adjust pitch and formant\n"
            "3. Add space or special effects\n"
            "4. Click Start to begin real-time processing\n\n"
            "Tips:\n"
            "- Special effects override voice modes\n"
            "- Use echo carefully to avoid distortion\n"
        )

        layout.addWidget(title)
        layout.addWidget(text)

        return w

    # =========================
    # ℹ About
    # =========================
    def _build_about_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("About")
        title.setStyleSheet("font-size:18px;")

        info = QLabel(
            "Voice Changer PC\n"
            "Version: 1.0.0\n\n"
            "A real-time voice processing system\n"
            "Built with PyQt5 + DSP pipeline\n\n"
            "Author: Haoquan Yu\n"
            "2026 Graduation Project"
        )

        info.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addStretch()

        return w

# =========================
# 🧠 MainWindow
# =========================
class MainWindow(QMainWindow):
    def __init__(self, controller: EngineController):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Voice Changer PC")
        self.resize(1200, 750)

        # ===== 页面容器 =====
        self.stack = QStackedWidget()

        # ===== 核心组件 =====
        self.control_panel = ControlPanel()
        self.visualizer_panel = VisualizerPanel()

        # ===== 页面 =====
        self.home = HomePage()
        self.studio = StudioPage(self.control_panel, self.visualizer_panel)
        self.settings = SettingsPage()

        # ===== 加入栈（🔥重新编号）=====
        self.stack.addWidget(self.home)      # 0
        self.stack.addWidget(self.studio)    # 1
        self.stack.addWidget(self.settings)  # 2

        self.setCentralWidget(self.stack)

        # ===== 状态栏 =====
        self.status_label = QLabel("Ready")
        bar = QStatusBar()
        bar.addWidget(self.status_label)
        self.setStatusBar(bar)

        self._bind_signals()

        # ===== 初始化 =====
        self.control_panel.sync_from_state(self.controller.get_state())
        self.visualizer_panel.update_pipeline(self.controller.build_pipeline_summary())
        self.controller.audio_engine.on_spectrum = self.visualizer_panel._update_spectrum

    # =========================
    # 🔥 页面跳转绑定
    # =========================
    def _bind_signals(self):
        # ===== Home =====
        self.home.enter_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.home.settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        # ===== Studio =====
        self.studio.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.studio.to_settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        # ===== Settings =====
        self.settings.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        # ===== 控制逻辑 =====
        cp = self.control_panel

        cp.start_button.clicked.connect(self.controller.start)
        cp.stop_button.clicked.connect(self.controller.stop)

        cp.mode_combo.currentTextChanged.connect(self.controller.set_voice_mode)
        cp.space_combo.currentTextChanged.connect(self.controller.set_space_effect)
        cp.special_combo.currentTextChanged.connect(self.controller.set_special_effect)

        cp.pitch_slider.valueChanged.connect(self.controller.set_pitch_semitone)
        cp.formant_slider.valueChanged.connect(self.controller.set_formant_shift)
        cp.echo_slider.valueChanged.connect(self.controller.set_echo_ratio_from_percent)

        self.controller.state_changed.connect(cp.sync_from_state)
        self.controller.status_changed.connect(self.status_label.setText)
        self.controller.pipeline_changed.connect(self.visualizer_panel.update_pipeline)