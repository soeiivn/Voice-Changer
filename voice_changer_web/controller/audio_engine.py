import numpy as np
import sounddevice as sd

from Project.src.dsp.pitch.psola import PSOLAPitchShifter
from Project.src.dsp.pitch.formant_envelope import FormantEnvelope

from Project.src.dsp.space_effects.echo import EchoEffect
from Project.src.dsp.space_effects.early_reflection import EarlyReflection
from Project.src.dsp.space_effects.schroeder_reverb import SchroederReverb

from Project.src.dsp.special_effects.telephone import TelephoneEffect
from Project.src.dsp.special_effects.Robot import RobotEffect
from Project.src.dsp.special_effects.Cartoon import CartoonEffect

class AudioEngine:

    def __init__(self, fs=16000, block_size=1024):
        self.fs = fs
        self.block_size = block_size

        # ===== 参数 =====
        self.pitch_semitone = 0
        self.formant_shift = 1.0
        self.echo_ratio = 0.4

        self.space_effect = "none"
        self.special_effect = "none"

        # ===== 模块 =====
        self.pitch = PSOLAPitchShifter(fs)
        self.formant = FormantEnvelope(fs)

        self.echo = EchoEffect(fs)
        self.reflect = EarlyReflection(fs)
        self.reverb = SchroederReverb(fs)

        self.telephone = TelephoneEffect(fs)
        self.robot = RobotEffect(fs)
        self.cartoon = CartoonEffect(fs)

        self.stream = None
        self.running = False

        # 👉 给 UI 用
        self.on_spectrum = None

    # ==========================
    # 🎧 核心处理链（唯一入口）
    # ==========================
    def process(self, x):

        # ===== ① 特效 or 音色（互斥）=====
        if self.special_effect != "none":

            if self.special_effect == "robot":
                x = self.robot.process(x)

            elif self.special_effect == "telephone":
                x = self.telephone.process(x)

            elif self.special_effect == "cartoon":
                x = self.cartoon.process(x)

        else:
            # 🎯 音色模块
            self.pitch.set_semitone(self.pitch_semitone)
            self.formant.shift = self.formant_shift

            x = self.pitch.process_block(x)
            x = self.formant.process(x)

        # ===== ② 空间模块（可叠加）=====
        if self.space_effect == "echo":
            self.echo.set_mix_ratio(self.echo_ratio)
            x = self.echo.process(x)

        elif self.space_effect == "reflect":
            x = self.reflect.process(x)

        elif self.space_effect == "reverb":
            x = self.reverb.process(x)

        # ===== ③ 频谱 =====
        if self.on_spectrum is not None:
            spectrum = np.abs(np.fft.rfft(x))
            self.on_spectrum(spectrum)

        return x

    # ==========================
    # 🎤 音频回调（唯一入口）
    # ==========================
    def _callback(self, indata, outdata, frames, time, status):

        try:
            x = indata[:, 0]
            y = self.process(x)
            if len(y) != len(x):
                y = np.zeros_like(x)

            outdata[:, 0] = y

        except Exception as e:
            print("Audio error:", e)
            outdata[:, 0] = np.zeros(frames)

    # ==========================
    # ▶️ 启动
    # ==========================
    def start(self):

        if self.running:
            return

        self.stream = sd.Stream(
            samplerate=self.fs,
            blocksize=self.block_size,
            channels=1,
            callback=self._callback
        )

        self.stream.start()
        self.running = True

    # ==========================
    # ⏹️ 停止
    # ==========================
    def stop(self):

        if self.stream:
            self.stream.stop()
            self.stream.close()

        self.running = False