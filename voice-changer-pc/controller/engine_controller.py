from dataclasses import asdict, dataclass

from PyQt5.QtCore import QObject, pyqtSignal

try:
    from controller.audio_engine import AudioEngine
except ImportError:
    pass

@dataclass

class EngineController(QObject):

    state_changed = pyqtSignal(dict)
    status_changed = pyqtSignal(str)
    pipeline_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.audio_engine = AudioEngine()

        # 状态
        self.voice_mode = "normal"

    # =========================
    # 🎯 状态获取
    # =========================
    def get_state(self):
        return {
            "voice_mode": self.voice_mode,
            "space_effect": self.audio_engine.space_effect,
            "special_effect": self.audio_engine.special_effect,
            "pitch_semitone": self.audio_engine.pitch_semitone,
            "formant_shift": self.audio_engine.formant_shift,
            "echo_ratio": self.audio_engine.echo_ratio,
            "running": self.audio_engine.running,
        }

    # =========================
    # 🎯 音色（互斥）
    # =========================
    def set_voice_mode(self, mode):

        # ❗特效开启 → 禁止音色
        if self.audio_engine.special_effect != "none" and mode != "normal":
            self.status_changed.emit("⚠ 特效开启时不能使用音色")
            return

        self.voice_mode = mode

        if mode == "girl":
            self.audio_engine.pitch_semitone = 6
            self.audio_engine.formant_shift = 1.25

        elif mode == "doll":
            self.audio_engine.pitch_semitone = 10
            self.audio_engine.formant_shift = 1.3

        elif mode == "boy":
            self.audio_engine.pitch_semitone = 5
            self.audio_engine.formant_shift = 1.28

        elif mode == "lady":
            self.audio_engine.pitch_semitone = 3
            self.audio_engine.formant_shift = 1.15

        elif mode == "deep":
            self.audio_engine.pitch_semitone = -3
            self.audio_engine.formant_shift = 0.9

        elif mode == "smoky":
            self.audio_engine.pitch_semitone = -5
            self.audio_engine.formant_shift = 0.85

        else:
            self.audio_engine.pitch_semitone = 0
            self.audio_engine.formant_shift = 1.0

        self._emit_all()

    # =========================
    # 🎯 特效（互斥）
    # =========================
    def set_special_effect(self, effect):

        # ❗音色开启 → 禁止特效
        if self.voice_mode != "normal" and effect != "none":
            self.status_changed.emit("⚠ 音色开启时不能使用特效")
            return

        self.audio_engine.special_effect = effect
        self._emit_all()

    # =========================
    # 🎯 空间（可叠加）
    # =========================
    def set_space_effect(self, effect):
        self.audio_engine.space_effect = effect
        self._emit_all()

    def set_echo_ratio_from_percent(self, value):
        self.audio_engine.echo_ratio = value / 100.0
        self._emit_all()

    def set_pitch_semitone(self, value):
        self.audio_engine.pitch_semitone = value
        self._emit_all()

    def set_formant_shift(self, value):
        self.audio_engine.formant_shift = value / 100.0
        self._emit_all()

    # =========================
    # ▶️ 控制
    # =========================
    def start(self):
        self.audio_engine.start()
        self._emit_all()
        self.status_changed.emit("▶️ 已启动")

    def stop(self):
        self.audio_engine.stop()
        self._emit_all()
        self.status_changed.emit("⏹️ 已停止")

    # =========================
    # 🔁 UI更新
    # =========================
    def _emit_all(self):
        self.state_changed.emit(self.get_state())
        self.pipeline_changed.emit(self.build_pipeline_summary())

    def build_pipeline_summary(self):

        parts = []

        if self.audio_engine.special_effect != "none":
            parts.append(f"Special({self.audio_engine.special_effect})")
        else:
            parts.append(f"Voice({self.voice_mode})")

        if self.audio_engine.space_effect != "none":
            parts.append(f"Space({self.audio_engine.space_effect})")

        return " → ".join(parts)