import numpy as np


class PhaseVocoder:
    def __init__(self, frame_size=512, hop=128, fs=16000):
        self.frame_size = frame_size
        self.hop = hop
        self.fs = fs

        self.prev_phase = np.zeros(frame_size // 2 + 1)
        self.phase_acc = np.zeros(frame_size // 2 + 1)

        self.window = np.hanning(frame_size)
        self.omega = 2 * np.pi * np.arange(frame_size // 2 + 1) / frame_size

        # ✅ 更稳定（不使用 sum(window)）
        self.norm_factor = 1.0

    def process_frame(self, frame: np.ndarray, ratio: float):
        # ❗ 不再重复 window
        X = np.fft.rfft(frame * self.window)

        mag = np.abs(X)
        phase = np.angle(X)

        delta_phase = phase - self.prev_phase - self.omega * self.hop
        delta_phase -= 2 * np.pi * np.round(delta_phase / (2 * np.pi))

        true_freq = self.omega + delta_phase / self.hop

        self.phase_acc += self.hop * true_freq / ratio
        self.prev_phase = phase

        Y = mag * np.exp(1j * self.phase_acc)
        y = np.fft.irfft(Y)

        return (y * self.norm_factor).astype(np.float32)