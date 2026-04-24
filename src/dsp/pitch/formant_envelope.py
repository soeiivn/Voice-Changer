import numpy as np

class FormantEnvelope:
    def __init__(self, fs, shift=1.0):
        self.fs = fs
        self.shift = shift

    def process(self, x):
        if abs(self.shift - 1.0) < 0.04:   # 变化很小时直接返回，节省计算
            return x.copy()

        N = len(x)
        if N < 64:
            return x.copy()

        # ===== FFT =====
        X = np.fft.rfft(x)
        mag = np.abs(X)
        phase = np.angle(X)

        # ===== 包络提取 =====
        envelope = self._smooth(mag)

        # ===== 细节（激励源）=====
        detail = mag / (envelope + 1e-6)

        # ===== 频率轴 & 拉伸 =====
        freqs = np.linspace(0, 1, len(envelope))
        shift = np.clip(self.shift, 0.75, 1.40)

        warped_freqs = freqs / shift
        warped_freqs = np.clip(warped_freqs, 0, 1)

        # 插值新的 envelope
        new_envelope = np.interp(freqs, warped_freqs, envelope)

        # ===== 加强音色变化（关键！）=====
        mean_env = np.mean(new_envelope)
        new_envelope = mean_env + 1.45 * (new_envelope - mean_env)   # 增加对比度

        # ===== 高频抑制（防止刺耳）=====
        freq_axis = np.linspace(0, self.fs / 2, len(new_envelope))
        hf_mask = 1 / (1 + (freq_axis / 4500) ** 2)
        new_envelope *= hf_mask

        # ===== 重建频谱 =====
        new_mag = new_envelope * detail

        Y = new_mag * np.exp(1j * phase)

        # ===== IFFT =====
        y = np.fft.irfft(Y, n=N)

        # 轻微增益补偿
        y = y * 1.12

        return np.clip(y, -1.0, 1.0).astype(np.float32)

    def _smooth(self, mag):
        """简单低通平滑（包络）"""
        kernel_size = 41
        kernel = np.ones(kernel_size) / kernel_size
        return np.convolve(mag, kernel, mode='same')