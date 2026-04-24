import numpy as np
import sounddevice as sd

from voice_changer_pc.audio_utils.resample import downsample_48k_to_16k, upsample_16k_to_48k

from src.dsp.pitch.psola import PSOLAPitchShifter
from src.dsp.pitch.formant_envelope import FormantEnvelope

from src.dsp.space_effects.echo import EchoEffect
from src.dsp.space_effects.early_reflection import EarlyReflection
from src.dsp.space_effects.schroeder_reverb import SchroederReverb

from src.dsp.special_effects.telephone import TelephoneEffect
from src.dsp.special_effects.Robot import RobotEffect
from src.dsp.special_effects.Cartoon import CartoonEffect

class AudioEngine:

    def __init__(self, fs=16000, block_size=1536,
                 input_device=None, output_device=None):
        self.internal_fs = fs
        self.external_fs = 48000
        self.block_size = block_size

        self.input_device = input_device
        self.output_device = output_device

        # ===== 参数 =====
        self.pitch_semitone = 0
        self.formant_shift = 1.0
        self.echo_ratio = 0.4

        self.space_effect = "none"
        self.special_effect = "none"

        # ===== 模块 =====
        self.pitch = PSOLAPitchShifter(self.internal_fs)
        self.formant = FormantEnvelope(self.internal_fs)

        self.echo = EchoEffect(self.internal_fs)
        self.reflect = EarlyReflection(self.internal_fs)
        self.reverb = SchroederReverb(self.internal_fs)

        self.telephone = TelephoneEffect(self.internal_fs)
        self.robot = RobotEffect(self.internal_fs)
        self.cartoon = CartoonEffect(self.internal_fs)

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

            # 🔥 第二阶段智能 bypass

            need_pitch = abs(self.pitch_semitone) > 0.1

            need_formant = abs(self.formant_shift - 1.0) > 0.02

            if need_pitch or need_formant:
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

            # 🔥 关键修复：强制补到 512 长度（可视化面板需要）
            if len(spectrum) < 512:
                padded = np.zeros(512, dtype=np.float32)
                padded[:len(spectrum)] = spectrum
                spectrum = padded
            else:
                spectrum = spectrum[:512]

            self.on_spectrum(spectrum)
        return x

    # ==========================
    # 🎤 音频回调（唯一入口）
    # ==========================
    def _callback(self, indata, outdata, frames, time, status):
        try:
            # 输入是 48kHz
            x_48k = indata[:, 0].astype(np.float32)

            # 1. 输入降噪（防止爆炸声）
            rms = np.sqrt(np.mean(x_48k ** 2))
            if rms > 0.3:  # 输入太响就压低
                x_48k = x_48k * 0.5
            else:
                x_48k = x_48k * 0.8

            # 2. 降采样到 16kHz
            x_16k = downsample_48k_to_16k(x_48k)

            # 3. DSP 处理
            y_16k = self.process(x_16k)

            # 4. 升采样回 48kHz
            y_48k = upsample_16k_to_48k(y_16k)

            # 5. 输出轻微增益（让变声更明显）
            y_48k = y_48k * 1.15

            # 6. 长度对齐
            if len(y_48k) != frames:
                y_48k = np.resize(y_48k, frames)

            outdata[:, 0] = np.clip(y_48k, -1.0, 1.0)

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
            samplerate=self.external_fs,
            blocksize=self.block_size,
            channels=1,
            dtype='float32',
            device=(self.input_device, self.output_device),  # ← 输入真实麦克风，输出 CABLE Input
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