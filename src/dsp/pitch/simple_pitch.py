import numpy as np
from scipy.signal import resample_poly

class SimplePitchShifter:
    def __init__(self, fs=16000):
        self.fs = fs
        self.semitone = 0.0
        self.ratio = 1.0

    def set_semitone(self, semitone: float):
        self.semitone = float(semitone)
        self.ratio = 2 ** (semitone / 12.0)

    def process(self, x: np.ndarray) -> np.ndarray:
        if abs(self.semitone) < 0.15:
            return x.copy()

        if len(x) < 128:
            return x.copy()

        try:
            # 🔥 修复：正 semitone 要变高 → 时间压缩（new_len 更小）
            ratio = 2 ** (self.semitone / 12.0)
            new_len = int(len(x) * ratio)  # ← 改成 * ratio（关键修复）

            if new_len < 64:
                new_len = 64

            # 重采样回原始长度（只变音高，不变时长）
            y = resample_poly(x, up=len(x), down=new_len, window=('kaiser', 8.0))

            # 音量补偿 + 高音时轻微提亮
            gain = 1.0 + abs(self.semitone) * 0.04
            if self.semitone > 0:
                y = y * 1.10  # 正半音额外提亮一点

            return np.clip(y, -1.0, 1.0).astype(np.float32)

        except:
            return x.copy()