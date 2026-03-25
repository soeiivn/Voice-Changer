import sys
from pathlib import Path

# 👉 项目根目录
ROOT_DIR = Path(__file__).resolve().parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from audio_engine import AudioEngine

class EngineController:

    def __init__(self):
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

        if self.audio_engine.special_effect != "none" and mode != "normal":
            print("⚠ 特效开启时不能使用音色")
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

        self._log_state()

    # =========================
    # 🎯 特效（互斥）
    # =========================
    def set_special_effect(self, effect):

        if self.voice_mode != "normal" and effect != "none":
            print("⚠ 音色开启时不能使用特效")
            return

        self.audio_engine.special_effect = effect
        self._log_state()

    # =========================
    # 🎯 空间（可叠加）
    # =========================
    def set_space_effect(self, effect):

        SPACE_MAP = {
            "none": "none",
            "echo": "echo",
            "room": "reflect",
            "hall": "reverb"
        }

        mapped = SPACE_MAP.get(effect, "none")

        self.audio_engine.space_effect = mapped

        self._log_state()

    def set_echo_ratio_from_percent(self, value):
        self.audio_engine.echo_ratio = value / 100.0
        self._log_state()

    def set_pitch_semitone(self, value):
        self.audio_engine.pitch_semitone = value
        self._log_state()

    def set_formant_shift(self, value):
        self.audio_engine.formant_shift = value / 100.0
        self._log_state()

    # =========================
    # ▶️ 控制
    # =========================
    def start(self):
        self.audio_engine.start()
        print("▶️ 已启动")

    def stop(self):
        self.audio_engine.stop()
        print("⏹️ 已停止")

    # =========================
    # 🔁 Debug用（代替 signal）
    # =========================
    def _log_state(self):
        print("[STATE]", self.get_state())
        print("[PIPELINE]", self.build_pipeline_summary())

    def build_pipeline_summary(self):

        parts = []

        if self.audio_engine.special_effect != "none":
            parts.append(f"Special({self.audio_engine.special_effect})")
        else:
            parts.append(f"Voice({self.voice_mode})")

        if self.audio_engine.space_effect != "none":
            parts.append(f"Space({self.audio_engine.space_effect})")

        return " → ".join(parts)