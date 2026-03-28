class EngineState:

    def __init__(self):
        # 🎤 音色
        self.voice_mode = "normal"

        # 🌌 空间
        self.space_effect = "none"

        # 🤖 特效
        self.special_effect = "none"

        # 🎚 参数
        self.pitch_semitone = 0
        self.formant_shift = 1.0
        self.echo_ratio = 0.0

        # ▶️ 状态
        self.running = False

    # =========================
    # 📦 导出（给前端 / debug）
    # =========================
    def to_dict(self):
        return {
            "voice_mode": self.voice_mode,
            "space_effect": self.space_effect,
            "special_effect": self.special_effect,
            "pitch_semitone": self.pitch_semitone,
            "formant_shift": self.formant_shift,
            "echo_ratio": self.echo_ratio,
            "running": self.running,
        }

    # =========================
    # 🔄 从engine同步（关键）
    # =========================
    def sync_from_engine(self, engine):
        self.space_effect = engine.space_effect
        self.special_effect = engine.special_effect
        self.pitch_semitone = engine.pitch_semitone
        self.formant_shift = engine.formant_shift
        self.echo_ratio = engine.echo_ratio
        self.running = engine.running