import numpy as np

class AudioEngine:
    def __init__(self, fs=16000):
        self.fs = fs

        # ====================== 参数（可调）======================
        self.voice_style = "normal"
        self.special_effect = None
        self.space_effect = None
        self.echo_ratio = 0.4
        self.input_buffer = np.array([], dtype=np.float32)
        self.output_buffer = np.array([], dtype=np.float32)
        self.chunk_size = 512

        # 风格预设表
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
        from src.dsp.pitch.simple_pitch import SimplePitchShifter
        from src.dsp.pitch.formant_envelope import FormantEnvelope

        self.pitch = SimplePitchShifter(fs=fs)
        self.formant = FormantEnvelope(fs, shift=1.0)

        # ===== 空间音效 =====
        from src.dsp.space_effects.echo import EchoEffect
        from src.dsp.space_effects.early_reflection import EarlyReflection
        from src.dsp.space_effects.schroeder_reverb import SchroederReverb

        self.space_effects = {
            "echo": EchoEffect(fs),
            "room": EarlyReflection(fs),
            "hall": SchroederReverb(fs),
        }

        # ===== 特殊音效 =====
        from src.dsp.special_effects.telephone import TelephoneEffect
        from src.dsp.special_effects.Robot import RobotEffect
        from src.dsp.special_effects.Cartoon import CartoonEffect

        self.special_effects = {
            "robot": RobotEffect(fs),
            "telephone": TelephoneEffect(fs),
            "cartoon": CartoonEffect(fs),
        }

        self.prev_output = None

    # ========================= 参数更新 =========================
    def set_pitch(self, semitone: float):
        self.pitch.set_semitone(float(semitone))

    def set_formant(self, shift: float):
        self.formant.shift = float(shift)

    def set_voice_style(self, style: str):
        if style not in self.voice_presets:
            style = "normal"
        self.voice_style = style

        preset = self.voice_presets[style]
        self._update_pitch_formant(preset["pitch"], preset["formant"])
        print(f"✅ [VoiceStyle] 设置为 {style} → pitch={preset['pitch']}, formant={preset['formant']}")

    def set_special_effect(self, effect: str | None):
        self.special_effect = effect if effect in self.special_effects else None

    def set_space_effect(self, effect: str | None):
        self.space_effect = effect if effect in self.space_effects else None

    def set_echo_ratio(self, ratio: float):
        self.echo_ratio = float(ratio)
        if "echo" in self.space_effects:
            self.space_effects["echo"].set_mix_ratio(self.echo_ratio)
        print(f"✅ Echo Strength 设置为 {self.echo_ratio:.2f}")

    # 内部更新
    def _update_pitch_formant(self, semitone: float, shift: float):
        self.pitch.set_semitone(semitone)
        self.formant.shift = shift

    # ========================= 核心处理 =========================
    def process(self, x: np.ndarray):
        if x is None or len(x) == 0:
            return x
        x = np.clip(x, -1.0, 1.0).astype(np.float32)

        self.input_buffer = np.concatenate([self.input_buffer, x])

        processed_chunks = []

        while len(self.input_buffer) >= self.chunk_size:
            chunk = self.input_buffer[:self.chunk_size]
            self.input_buffer = self.input_buffer[self.chunk_size:]

            y = chunk.copy()

            try:
                if self.special_effect is not None and self.special_effect in self.special_effects:
                    y = self.special_effects[self.special_effect].process(y)
                else:
                    # Voice 处理（轻量版）
                    self.pitch.set_semitone(self.pitch.semitone)   # 确保同步
                    y = self.pitch.process(y)
                    y = self.formant.process(y)
                    y = y * 1.25                     # 加强变化

                # 空间音效
                if self.space_effect is not None and self.space_effect in self.space_effects:
                    if self.space_effect == "echo":
                        self.space_effects["echo"].set_mix_ratio(self.echo_ratio)
                    y = self.space_effects[self.space_effect].process(y)

            except Exception as e:
                print("DSP error:", e)
                y = chunk

            # 平滑
            if self.prev_output is None or len(self.prev_output) != len(y):
                self.prev_output = y.copy()
            y = 0.65 * y + 0.35 * self.prev_output
            self.prev_output = y.copy()

            y = np.clip(y, -1.0, 1.0).astype(np.float32)
            processed_chunks.append(y)

        # 输出处理
        if processed_chunks:
            y_full = np.concatenate(processed_chunks)
            self.output_buffer = np.concatenate([self.output_buffer, y_full])

        if len(self.output_buffer) >= len(x):
            out = self.output_buffer[:len(x)]
            self.output_buffer = self.output_buffer[len(x):]
            return out
        else:
            out = np.zeros_like(x)
            if len(self.output_buffer) > 0:
                out[:len(self.output_buffer)] = self.output_buffer
                self.output_buffer = np.array([], dtype=np.float32)
            return out