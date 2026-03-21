from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QSplitter, QStatusBar, QVBoxLayout, QWidget

import sys

try:
    from controller.engine_controller import EngineController
    from gui.visualizer import VisualizerPanel
    from gui.widgets import ControlPanel
    print("Main window imports successful!")  # 调试用
except ImportError as e:
    print(f"Main window import error: {e}")
    print(f"sys.path: {sys.path}")

class MainWindow(QMainWindow):

    def __init__(self, controller: EngineController):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("Voice Changer PC")
        self.resize(1180, 720)

        self.control_panel = ControlPanel()
        self.visualizer_panel = VisualizerPanel()
        self.status_label = QLabel("阶段 3: 控制器接入音频引擎。")

        self._build_ui()
        self._bind_signals()

        # 初始化 UI 状态
        self.control_panel.sync_from_state(self.controller.get_state())
        self.visualizer_panel.update_pipeline(self.controller.build_pipeline_summary())
        self.controller.audio_engine.on_spectrum = self.visualizer_panel._update_spectrum

    def _build_ui(self):
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        header = QLabel("Voice Changer 桌面端 - 阶段 3 原型")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        central_layout.addWidget(header)

        subtitle = QLabel("当前阶段目标：让 GUI 与控制器联动，明确实时处理链路与参数流向。")
        subtitle.setWordWrap(True)
        central_layout.addWidget(subtitle)

        splitter = QSplitter()
        splitter.addWidget(self.control_panel)
        splitter.addWidget(self.visualizer_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        central_layout.addWidget(splitter, stretch=1)

        self.setCentralWidget(central_widget)

        status_bar = QStatusBar()
        status_bar.addWidget(self.status_label, 1)
        self.setStatusBar(status_bar)

    def _bind_signals(self):
        # ===== 按钮 =====
        self.control_panel.start_button.clicked.connect(self._handle_start_clicked)
        self.control_panel.stop_button.clicked.connect(self._handle_stop_clicked)

        # ===== 核心修复：直接绑定 controller（不要再走中转函数） =====
        self.control_panel.mode_combo.currentTextChanged.connect(self.controller.set_voice_mode)
        self.control_panel.space_combo.currentTextChanged.connect(self.controller.set_space_effect)
        self.control_panel.special_combo.currentTextChanged.connect(self.controller.set_special_effect)

        self.control_panel.pitch_slider.valueChanged.connect(self.controller.set_pitch_semitone)
        self.control_panel.formant_slider.valueChanged.connect(
            self.controller.set_formant_shift
        )
        self.control_panel.echo_slider.valueChanged.connect(self.controller.set_echo_ratio_from_percent)

        # ===== Controller → UI =====
        self.controller.state_changed.connect(self.control_panel.sync_from_state)
        self.controller.status_changed.connect(self.status_label.setText)
        self.controller.pipeline_changed.connect(self.visualizer_panel.update_pipeline)
        self.controller.state_changed.connect(self._force_ui_sync)

    def _force_ui_sync(self, state):
        self.control_panel.sync_from_state(state)

    # ===== 按钮 handler =====
    def _handle_start_clicked(self):
        self.controller.start()

    def _handle_stop_clicked(self):
        self.controller.stop()