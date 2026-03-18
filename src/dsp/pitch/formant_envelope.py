import numpy as np

class FormantEnvelope:

    def __init__(self, fs, shift=1.2):

        self.fs = fs
        self.shift = shift

    def process(self, x):

        N = len(x)

        # ===== FFT =====
        X = np.fft.rfft(x)
        mag = np.abs(X)
        phase = np.angle(X)

        # ===== 包络提取（平滑）=====
        envelope = self._smooth(mag)

        # ===== 细节（激励）=====
        detail = mag / (envelope + 1e-6)

        # ===== 频率轴 =====
        freqs = np.linspace(0, 1, len(envelope))

        # ===== 关键：频率拉伸 =====
        warped_freqs = freqs / self.shift
        warped_freqs = np.clip(warped_freqs, 0, 1)

        # 插值新的 envelope
        new_envelope = np.interp(
            freqs,
            warped_freqs,
            envelope
        )

        # ===== 重建频谱 =====
        new_mag = new_envelope * detail

        Y = new_mag * np.exp(1j * phase)

        # ===== IFFT =====
        y = np.fft.irfft(Y, n=N)

        return y

    def _smooth(self, mag):
        """简单低通平滑（包络）"""
        kernel_size = 15
        kernel = np.ones(kernel_size) / kernel_size
        return np.convolve(mag, kernel, mode='same')