from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

class ControlPanel(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ===== 控件（完全不动）=====
        self.start_button = QPushButton("🟢 Start Talking")
        self.stop_button = QPushButton("🔴 Stop")
        self.stop_button.setEnabled(False)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["normal", "doll", "girl", "lady", "boy", "deep", "smoky"])

        self.space_combo = QComboBox()
        self.space_combo.addItems(["none", "echo", "room", "hall"])

        self.special_combo = QComboBox()
        self.special_combo.addItems(["none", "robot", "telephone", "cartoon"])

        self.pitch_slider = self._create_slider(-12, 12, 0)
        self.echo_slider = self._create_slider(0, 100, 40)

        self.pitch_value_label = QLabel("0 semitone")
        self.echo_value_label = QLabel("40 %")

        self.formant_slider = self._create_slider(50, 200, 100)
        self.formant_value_label = QLabel("1.00")

        self._build_ui()
        self._bind_default_signals()

    # =========================
    # Slider工厂
    # =========================
    @staticmethod
    def _create_slider(minimum: int, maximum: int, value: int) -> QSlider:
        slider = QSlider(Qt.Horizontal)
        slider.setRange(minimum, maximum)
        slider.setValue(value)
        return slider

    # =========================
    # 🔥 UI重构核心
    # =========================
    def _build_ui(self):
        root_layout = QVBoxLayout(self)

        # 👉 间距（高级感关键）
        root_layout.setSpacing(12)
        root_layout.setContentsMargins(10, 10, 10, 10)

        # ===== 控制区（更突出）=====
        root_layout.addWidget(self._build_transport_box())

        # ===== 三大模块（分组强化）=====
        root_layout.addWidget(self._build_voice_box())
        root_layout.addWidget(self._build_space_box())
        root_layout.addWidget(self._build_special_box())

        root_layout.addStretch(1)

    # =========================
    # 🔥 控制模块（大按钮）
    # =========================
    def _build_transport_box(self) -> QGroupBox:
        group = QGroupBox("Control")
        layout = QVBoxLayout(group)

        self.start_button.setMinimumHeight(50)
        self.stop_button.setMinimumHeight(40)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        return group

    # =========================
    # 🎤 Voice模块（核心模块）
    # =========================
    def _build_voice_box(self) -> QGroupBox:
        group = QGroupBox("🎤 Voice")
        layout = QFormLayout(group)

        layout.addRow("Mode", self.mode_combo)
        layout.addRow("Pitch", self._wrap_slider(self.pitch_slider, self.pitch_value_label))
        layout.addRow("Formant", self._wrap_slider(self.formant_slider, self.formant_value_label))

        return group

    # =========================
    # 🌌 Space模块
    # =========================
    def _build_space_box(self) -> QGroupBox:
        group = QGroupBox("🌌 Space")
        layout = QFormLayout(group)

        layout.addRow("Effect", self.space_combo)
        layout.addRow("Echo", self._wrap_slider(self.echo_slider, self.echo_value_label))

        return group

    # =========================
    # ⚡ Special模块
    # =========================
    def _build_special_box(self) -> QGroupBox:
        group = QGroupBox("⚡ Special")
        layout = QFormLayout(group)

        layout.addRow("Effect", self.special_combo)

        return group

    # =========================
    # Slider + 数值
    # =========================
    @staticmethod
    def _wrap_slider(slider: QSlider, label: QLabel) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(slider, stretch=1)
        layout.addWidget(label)
        return widget

    # =========================
    # 信号
    # =========================
    def _bind_default_signals(self):
        self.pitch_slider.valueChanged.connect(self._update_pitch_label)
        self.formant_slider.valueChanged.connect(self._update_formant_label)
        self.echo_slider.valueChanged.connect(self._update_echo_label)

    # =========================
    # ❗功能核心
    # =========================
    def sync_from_state(self, state: dict):
        self.mode_combo.setCurrentText(state["voice_mode"])
        self.space_combo.setCurrentText(state["space_effect"])
        self.special_combo.setCurrentText(state["special_effect"])
        self.pitch_slider.setValue(int(state["pitch_semitone"]))
        self.formant_slider.setValue(int(state["formant_shift"] * 100))
        self.echo_slider.setValue(int(round(state["echo_ratio"] * 100)))
        self.set_running(state["running"])

        voice_mode = state["voice_mode"]
        special = state["special_effect"]

        if special != "none":
            self.mode_combo.setEnabled(False)
            self.special_combo.setEnabled(True)
            self.formant_slider.setEnabled(False)

        elif voice_mode != "normal":
            self.mode_combo.setEnabled(True)
            self.formant_slider.setEnabled(True)
            self.special_combo.setEnabled(False)

        else:
            self.mode_combo.setEnabled(True)
            self.formant_slider.setEnabled(True)
            self.special_combo.setEnabled(True)

        self.blockSignals(False)

    def set_running(self, running: bool):
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)

    def _update_pitch_label(self, value: int):
        self.pitch_value_label.setText(f"{value} semitone")

    def _update_formant_label(self, value):
        self.formant_value_label.setText(f"{value / 100:.2f}")

    def _update_echo_label(self, value: int):
        self.echo_value_label.setText(f"{value} %")