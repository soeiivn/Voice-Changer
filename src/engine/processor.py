import numpy as np

# ===== pitch =====
from Project.src.dsp.pitch.psola import PSOLAPitchShifter
from Project.src.dsp.pitch.formant_envelope import FormantEnvelope

# ===== space =====
from Project.src.dsp.space_effects.echo import EchoEffect
from Project.src.dsp.space_effects.schroeder_reverb import SchroederReverb
from Project.src.dsp.space_effects.early_reflection import EarlyReflection

# ===== special =====
from Project.src.dsp.special_effects.Robot import RobotEffect
from Project.src.dsp.special_effects.telephone import TelephoneEffect
from Project.src.dsp.special_effects.Cartoon import CartoonEffect

# ===== config =====
from .config import ECHO_DEFAULTS, VOICE_PRESETS

class AudioProcessor:

    def __init__(self, fs=44100):

        self.fs = fs

        # ===== 模块实例 =====
        self.psola = PSOLAPitchShifter(fs)
        self.formant = FormantEnvelope(fs)

        self.echo = EchoEffect(
            fs,
            delay_ms=ECHO_DEFAULTS["delay_ms"],
            decay=ECHO_DEFAULTS["ratio"]
        )
        self.early_reflect = EarlyReflection(fs)
        self.reverb = SchroederReverb(fs)

        self.robot = RobotEffect(fs)
        self.telephone = TelephoneEffect(fs)
        self.cartoon = CartoonEffect(fs)

        # ===== 状态控制（关键）=====
        self.enable_pitch = False
        self.enable_space = None      # "reverb" / "echo" / "reflect" / None
        self.enable_special = None    # "robot" / "telephone" / "cartoon" / None
        self.echo_ratio = ECHO_DEFAULTS["ratio"]

    # =========================
    # 🎯 音色设置（唯一需要调参）
    # =========================
    def set_voice_mode(self, mode):

        # 允许关闭
        if mode is None:
            self.enable_pitch = False
            return

        if mode not in VOICE_PRESETS:
            print(f"[Warning] Unknown voice mode: {mode}")
            return

        p = VOICE_PRESETS[mode]

        self.psola.set_semitone(p["semitone"])
        self.formant.shift = p["formant"]

        self.enable_pitch = True

    # =========================
    # 🎯 空间效果选择（无需调参）
    # =========================
    def set_space_effect(self, effect_name):
        valid = ["reverb", "echo", "reflect", None]

        if effect_name not in valid:
            print(f"[Warning] Unknown space effect: {effect_name}")
            return

        self.enable_space = effect_name

    def set_echo_ratio(self, ratio):
        self.echo_ratio = min(max(float(ratio), 0.0), 0.95)
        self.echo.set_mix_ratio(self.echo_ratio)

    def set_echo_delay(self, delay_ms):
        self.echo.set_delay_ms(delay_ms)

    def set_echo_params(self, ratio=None, delay_ms=None):
        if ratio is not None:
            self.set_echo_ratio(ratio)

        if delay_ms is not None:
            self.set_echo_delay(delay_ms)

    # =========================
    # 🎯 特殊效果选择（无需调参）
    # =========================
    def set_special_effect(self, effect_name):
        valid = ["robot", "telephone", "cartoon", None]

        if effect_name not in valid:
            print(f"[Warning] Unknown special effect: {effect_name}")
            return

        self.enable_special = effect_name

    # =========================
    # 🎯 核心处理流程（动态组合）
    # =========================
    def process_block(self, x: np.ndarray):

        y = x.copy()

        # ===== 1️⃣ 音色模块 =====
        if self.enable_pitch:
            y = self.psola.process_block(y)
            y = self.formant.process(y)

        # ===== 2️⃣ 空间模块 =====
        if self.enable_space == "reverb":
            y = self.reverb.process(y)

        elif self.enable_space == "echo":
            y = self.echo.process(y)

        elif self.enable_space == "reflect":
            y = self.early_reflect.process(y)

        # ===== 3️⃣ 特殊模块 =====
        if self.enable_special == "robot":
            y = self.robot.process(y)

        elif self.enable_special == "telephone":
            y = self.telephone.process(y)

        elif self.enable_special == "cartoon":
            y = self.cartoon.process(y)

        return y