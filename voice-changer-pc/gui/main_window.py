from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QMainWindow, QSplitter, QStatusBar, QVBoxLayout, QWidget

from .visualizer import VisualizerPanel
from .widgets import ControlPanel

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Changer PC")
        self.resize(1180, 720)

        self.control_panel = ControlPanel()
        self.visualizer_panel = VisualizerPanel()
        self.status_label = QLabel("阶段 1：GUI 骨架已就绪，音频引擎尚未接入。")

        self._build_ui()
        self._bind_signals()
        self._update_status_from_controls()

    def _build_ui(self):
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)

        header = QLabel("Voice Changer 桌面端 - 阶段 1 原型")
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setStyleSheet("font-size: 22px; font-weight: bold;")
        central_layout.addWidget(header)

        subtitle = QLabel("当前阶段目标：先完成桌面端基础界面、参数控件和可视化占位区。")
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
        self.control_panel.start_button.clicked.connect(self._handle_start_clicked)
        self.control_panel.stop_button.clicked.connect(self._handle_stop_clicked)

        self.control_panel.mode_combo.currentTextChanged.connect(lambda _: self._update_status_from_controls())
        self.control_panel.space_combo.currentTextChanged.connect(lambda _: self._update_status_from_controls())
        self.control_panel.special_combo.currentTextChanged.connect(lambda _: self._update_status_from_controls())
        self.control_panel.pitch_slider.valueChanged.connect(lambda _: self._update_status_from_controls())
        self.control_panel.echo_slider.valueChanged.connect(lambda _: self._update_status_from_controls())

    def _handle_start_clicked(self):
        self.control_panel.start_button.setEnabled(False)
        self.control_panel.stop_button.setEnabled(True)
        self.status_label.setText("界面模拟状态：已点击启动。下一阶段将接入音频引擎。")

    def _handle_stop_clicked(self):
        self.control_panel.start_button.setEnabled(True)
        self.control_panel.stop_button.setEnabled(False)
        self._update_status_from_controls(prefix="界面模拟状态：已点击停止。")

    def _update_status_from_controls(self, prefix: str = "当前配置"):
        mode = self.control_panel.mode_combo.currentText()
        space = self.control_panel.space_combo.currentText()
        special = self.control_panel.special_combo.currentText()
        pitch = self.control_panel.pitch_slider.value()
        echo = self.control_panel.echo_slider.value()

        self.status_label.setText(
            f"{prefix} 音色={mode} | 空间={space} | 特效={special} | 音高={pitch} semitone | 回声={echo}%"
        )
