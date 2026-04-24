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
from PyQt5.QtGui import QPalette, QColor, QIcon
from PyQt5.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QUrl, QSize, QSettings
)

# 项目根目录
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
# 🏠 首页
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

        title = QLabel("🎧 实时语音变声器")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold;
            color: white;
        """)

        self.enter_btn = QPushButton("🚀 进入工作室")
        self.enter_btn.setMinimumHeight(50)

        self.settings_btn = QPushButton("⚙ 设置")

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
# 🎛 工作室
# =========================
class StudioPage(QWidget):
    def __init__(self, control_panel, visualizer):
        super().__init__()

        layout = QVBoxLayout(self)

        nav = QHBoxLayout()
        self.back_btn = QPushButton("← 返回首页")
        self.to_settings_btn = QPushButton("设置")

        nav.addWidget(self.back_btn)
        nav.addStretch()
        nav.addWidget(self.to_settings_btn)

        layout.addLayout(nav)

        splitter = QSplitter()
        splitter.addWidget(control_panel)
        splitter.addWidget(visualizer)

        layout.addWidget(splitter)


# =========================
# ⚙ 设置页面
# =========================
class SettingsPage(QWidget):
    theme_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        root = QVBoxLayout(self)

        self.back_btn = QPushButton("← 返回")

        # 左侧菜单
        menu_layout = QVBoxLayout()
        self.btn_audio = QPushButton("🎧 音频设置")
        self.btn_ui = QPushButton("🖥 界面设置")
        self.btn_help = QPushButton("📖 使用指南")
        self.btn_about = QPushButton("ℹ 关于我们")

        menu_layout.addWidget(self.btn_audio)
        menu_layout.addWidget(self.btn_ui)
        menu_layout.addWidget(self.btn_help)
        menu_layout.addWidget(self.btn_about)
        menu_layout.addStretch()

        # 右侧内容
        self.stack = QStackedWidget()
        self.page_audio = self._build_audio_page()
        self.page_ui = self._build_ui_page()
        self.page_help = self._build_help_page()
        self.page_about = self._build_about_page()

        self.stack.addWidget(self.page_audio)
        self.stack.addWidget(self.page_ui)
        self.stack.addWidget(self.page_help)
        self.stack.addWidget(self.page_about)

        body = QHBoxLayout()
        body.addLayout(menu_layout, 1)
        body.addWidget(self.stack, 3)

        root.addWidget(self.back_btn)
        root.addLayout(body)

        # 绑定切换
        self.btn_audio.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_ui.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_help.clicked.connect(lambda: self.stack.setCurrentIndex(2))
        self.btn_about.clicked.connect(lambda: self.stack.setCurrentIndex(3))

    def _build_audio_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("音频设置")
        title.setStyleSheet("font-size:18px;")
        device_select = QComboBox()
        device_select.addItems(["默认麦克风", "外接麦克风"])
        sample_rate = QComboBox()
        sample_rate.addItems(["16000 Hz"])
        layout.addWidget(title)
        layout.addWidget(QLabel("输入设备"))
        layout.addWidget(device_select)
        layout.addWidget(QLabel("采样率"))
        layout.addWidget(sample_rate)
        layout.addStretch()
        return w

    def _build_ui_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("界面设置")
        title.setStyleSheet("font-size:18px;")
        layout.addWidget(title)
        layout.addWidget(QLabel("更多界面设置可以后续在这里添加"))
        layout.addStretch()
        return w

    def _build_help_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        title = QLabel("使用指南")
        title.setStyleSheet("font-size:18px;")
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(
            "1. 选择变声模式\n"
            "2. 调整音高和共振峰\n"
            "3. 添加空间感或特殊效果\n"
            "4. 点击“开始说话”进行实时处理\n\n"
            "小贴士：\n"
            "- 特殊效果会覆盖普通变声模式\n"
            "- 使用混响时请注意避免声音失真"
        )
        layout.addWidget(title)
        layout.addWidget(text)
        return w

    def _build_about_page(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        title = QLabel("关于")
        title.setStyleSheet("font-size:18px;")

        info = QLabel(
            "实时语音变声器 (Voice Changer PC)\n"
            "版本：1.0.0\n\n"
            "实时语音处理系统\n"
            "基于 PyQt5 + DSP 音频管道开发\n\n"
            "作者：于皓诠\n"
            "2026 毕业设计项目"
        )
        info.setWordWrap(True)

        # 主题选择
        theme_title = QLabel("主题模式")
        theme_title.setStyleSheet("font-size:16px; font-weight:bold; margin-top:20px;")

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["深色模式", "浅色模式(默认)"])

        layout.addWidget(title)
        layout.addWidget(info)
        layout.addWidget(theme_title)
        layout.addWidget(self.theme_combo)
        layout.addStretch()

        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        return w

    def _on_theme_changed(self, text: str):
        theme = "Dark" if "深色" in text else "Light"
        self.theme_changed.emit(theme)


# =========================
# 🧠 主窗口
# =========================
class MainWindow(QMainWindow):
    def __init__(self, controller: EngineController):
        super().__init__()

        QApplication.setStyle("Fusion")

        self.controller = controller
        self.settings_store = QSettings("VoiceChangerPC", "VoiceChangerPro")

        self.setWindowTitle("实时语音变声器")
        self.resize(1200, 750)

        self.stack = QStackedWidget()

        self.control_panel = ControlPanel()
        self.visualizer_panel = VisualizerPanel()

        self.home = HomePage()
        self.studio = StudioPage(self.control_panel, self.visualizer_panel)
        self.settings = SettingsPage()

        # 初始化主题
        current_theme = self.settings_store.value("theme", "Dark")
        if current_theme not in ("Dark", "Light"):
            current_theme = "Dark"

        self.settings.theme_combo.blockSignals(True)
        self.settings.theme_combo.setCurrentIndex(0 if current_theme == "Dark" else 1)
        self.settings.theme_combo.blockSignals(False)

        self.apply_theme(current_theme)

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.studio)
        self.stack.addWidget(self.settings)
        self.setCentralWidget(self.stack)

        self.status_label = QLabel("就绪")
        bar = QStatusBar()
        bar.addWidget(self.status_label)
        self.setStatusBar(bar)

        self._bind_signals()

        self.control_panel.sync_from_state(self.controller.get_state())
        self.visualizer_panel.update_pipeline(self.controller.build_pipeline_summary())
        self.controller.audio_engine.on_spectrum = self.visualizer_panel._update_spectrum

    def _bind_signals(self):
        # 页面切换
        self.home.enter_btn.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.home.settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.studio.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.studio.to_settings_btn.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.settings.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        # 控制逻辑
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

        # 主题切换
        self.settings.theme_changed.connect(self.on_theme_changed)

    def on_theme_changed(self, theme: str):
        self.apply_theme(theme)
        self.settings_store.setValue("theme", theme)

    def apply_theme(self, theme: str):
        palette = self._dark_palette() if theme == "Dark" else self._light_palette()
        QApplication.instance().setPalette(palette)

        current = self.stack.currentWidget()
        if current:
            current.setPalette(palette)
            current.update()

    def _dark_palette(self) -> QPalette:
        p = QPalette()
        p.setColor(QPalette.Window, QColor(53, 53, 53))
        p.setColor(QPalette.WindowText, Qt.white)
        p.setColor(QPalette.Base, QColor(25, 25, 25))
        p.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        p.setColor(QPalette.Text, Qt.white)
        p.setColor(QPalette.Button, QColor(53, 53, 53))
        p.setColor(QPalette.ButtonText, Qt.white)
        p.setColor(QPalette.Highlight, QColor(42, 130, 218))
        p.setColor(QPalette.HighlightedText, Qt.black)
        return p

    def _light_palette(self) -> QPalette:
        p = QPalette()
        p.setColor(QPalette.Window, QColor(240, 240, 240))
        p.setColor(QPalette.WindowText, QColor(0, 0, 0))
        p.setColor(QPalette.Base, QColor(255, 255, 255))
        p.setColor(QPalette.Text, QColor(0, 0, 0))
        p.setColor(QPalette.Button, QColor(240, 240, 240))
        p.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        p.setColor(QPalette.Highlight, QColor(0, 120, 215))
        p.setColor(QPalette.HighlightedText, Qt.white)
        return p