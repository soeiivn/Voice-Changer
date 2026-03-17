import numpy as np
from scipy.signal import lfilter

class FormantFilter:

    def __init__(self, fs, shift=1.2, verbose=False):

        self.fs = fs
        self.shift = shift
        self.verbose = verbose

        # 基本共振峰
        self.formants = [500, 1500, 2500]
        self.bandwidth = [80, 120, 150]

        if verbose:
            print(f"  ├─ Formant shift: {shift:.2f}")

    # =====================
    # 主处理
    # =====================
    def process(self, x):

        y = x.copy()

        for f, bw in zip(self.formants, self.bandwidth):

            f_shift = f * self.shift

            b, a = self._formant_filter(f_shift, bw)

            y = lfilter(b, a, y)

        return y

    # =====================
    # 共振峰滤波器
    # =====================
    def _formant_filter(self, f, bw):

        r = np.exp(-np.pi * bw / self.fs)

        theta = 2 * np.pi * f / self.fs

        a = np.array([1, -2 * r * np.cos(theta), r ** 2])

        b = np.array([0.06])

        return b, a