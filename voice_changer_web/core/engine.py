import numpy as np

class AudioEngine:
    def __init__(self, fs=16000):
        self.fs = fs

        # ====================== 参数（可调）======================
        self.voice_style = "normal"      # 当前风格
        self.special_effect = None       # "robot" / "telephone" / "cartoon" / None
        self.space_effect = None         # "echo" / "room" / "hall" / None
        self.echo_ratio = 0.4
        self.input_buffer = np.array([], dtype=np.float32)
        self.output_buffer = np.array([], dtype=np.float32)
        self.chunk_size = 1024

        # 风格预设表（你后面可以自己调整数值）
        self.voice_presets = {
            "normal": {"pitch": 0, "formant": 1.0},
            "doll":  {"pitch": 10, "formant": 1.3},
            "girl":  {"pitch": 6,  "formant": 1.25},
            "lady":  {"pitch": 3,  "formant": 1.15},
            "boy":   {"pitch": 5,  "formant": 1.28},
            "deep":  {"pitch": -3, "formant": 0.9},
            "smoky": {"pitch": -5, "formant": 0.85},
        }

        # ===== Pitch & Formant =====
        from src.dsp.pitch.psola import PSOLAPitchShifter
        from src.dsp.pitch.pitch_processor import PitchProcessor
        from src.dsp.pitch.formant_envelope import FormantEnvelope

        self.psola = PSOLAPitchShifter(fs=fs, semitone=0)
        self.pitch = PitchProcessor(self.psola)
        self.formant = FormantEnvelope(fs, shift=1.0)

        # ===== 空间音效（可叠加）=====
        from src.dsp.space_effects.echo import EchoEffect
        from src.dsp.space_effects.early_reflection import EarlyReflection
        from src.dsp.space_effects.schroeder_reverb import SchroederReverb

        self.space_effects = {
            "echo": EchoEffect(fs),
            "room": EarlyReflection(fs),
            "hall": SchroederReverb(fs),
        }

        # ===== 特殊音效（与风格互斥）=====
        from src.dsp.special_effects.telephone import TelephoneEffect
        from src.dsp.special_effects.Robot import RobotEffect
        from src.dsp.special_effects.Cartoon import CartoonEffect

        self.special_effects = {
            "robot": RobotEffect(fs),
            "telephone": TelephoneEffect(fs),
            "cartoon": CartoonEffect(fs),
        }

        # 缓存（保证连续性）
        self.prev_output = None

    # ========================= 参数更新（前端调用）=========================
    def set_pitch(self, semitone: float):
        self.psola.semitone = float(semitone)

    def set_formant(self, shift: float):
        self.formant.shift = float(shift)

    def set_voice_style(self, style: str):
        """设置音调音色风格（会自动更新 pitch + formant）"""
        if style not in self.voice_presets:
            style = "normal"
        self.voice_style = style

        preset = self.voice_presets[style]
        self._update_pitch_formant(preset["pitch"], preset["formant"])
        print(f"✅ [VoiceStyle] 设置为 {style} → pitch={preset['pitch']}, formant={preset['formant']}")

    def set_special_effect(self, effect: str | None):
        """设置特殊音效（与风格互斥）"""
        if effect in self.special_effects or effect is None:
            self.special_effect = effect
        else:
            self.special_effect = None

    def set_space_effect(self, effect: str | None):
        """设置空间音效（可叠加）"""
        if effect in self.space_effects or effect is None:
            self.space_effect = effect
        else:
            self.space_effect = None

    def set_echo_ratio(self, ratio: float):
        """用户调节回声强度（0.0~1.0）"""
        self.echo_ratio = float(ratio)
        if "echo" in self.space_effects:
            self.space_effects["echo"].set_mix_ratio(self.echo_ratio)
        print(f"✅ Echo Strength 设置为 {self.echo_ratio:.2f}")

    # 内部快捷方法
    def _update_pitch_formant(self, semitone: float, shift: float):
        self.psola.semitone = semitone
        self.formant.shift = shift

    # ========================= 核心处理 =========================
    def process(self, x: np.ndarray):
        if x is None or len(x) == 0:
            return x
        print("mean:", np.mean(x), "std:", np.std(x))
        x = np.clip(x, -1.0, 1.0)

        # ==================== 输入缓冲 ====================
        self.input_buffer = np.concatenate([self.input_buffer, x])

        # ==================== 不够一帧 → 直接输出原音 ====================
        if len(self.input_buffer) < self.chunk_size:
            return x  # ⚠️ 保持实时性

        # ==================== 取一块处理 ====================
        chunk = self.input_buffer[:self.chunk_size]
        self.input_buffer = self.input_buffer[self.chunk_size:]

        y = chunk.copy()

        try:
            # ===== 1. 特殊音效 vs Voice =====
            if self.special_effect is not None:
                y = self.special_effects[self.special_effect].process(y)
            else:
                # 👉 PSOLA 在这里终于能工作了
                y = self.pitch.process(y)
                y = self.formant.process(y)

            # ===== 2. 空间音效 =====
            if self.space_effect is not None:
                y = self.space_effects[self.space_effect].process(y)

        except Exception as e:
            print("DSP error:", e)
            y = chunk  # fallback

        # ==================== 平滑（保留你原逻辑） ====================
        if self.prev_output is None or len(self.prev_output) != len(y):
            self.prev_output = np.zeros_like(y)

        y = 0.8 * y + 0.2 * self.prev_output
        self.prev_output = y.copy()

        y = np.clip(y, -1.0, 1.0).astype(np.float32)

        # ==================== 输出缓冲 ====================
        self.output_buffer = np.concatenate([self.output_buffer, y])

        # ==================== 保证每次返回128 ====================
        if len(self.output_buffer) >= len(x):
            out = self.output_buffer[:len(x)]
            self.output_buffer = self.output_buffer[len(x):]
            return out
        else:
            # 不够就补0（极少发生）
            out = np.zeros_like(x)
            out[:len(self.output_buffer)] = self.output_buffer
            self.output_buffer = np.array([], dtype=np.float32)
            return out
