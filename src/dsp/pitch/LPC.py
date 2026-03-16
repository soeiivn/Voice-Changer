import numpy as np
from scipy.signal import lfilter

class LPCResidual:

    def __init__(self, order=16, verbose=False):

        self.order = order
        self.verbose = verbose

        if verbose:
            print(f"LPC Residual 初始化: order={order}")

    # ==========================
    # 主处理
    # ==========================
    def process(self, x):

        x = self._preprocess(x)

        # LPC系数
        a = self.compute_lpc(x)

        # 残差
        residual = self.compute_residual(x, a)

        return residual

    # ==========================
    # 预处理
    # ==========================
    def _preprocess(self, x):

        x = x - np.mean(x)

        max_val = np.max(np.abs(x))
        if max_val > 1e-6:
            x = x / max_val

        return x

    # ==========================
    # LPC计算
    # ==========================
    def compute_lpc(self, x):

        p = self.order

        r = self.autocorrelation(x, p)

        a = self.levinson_durbin(r, p)

        return a

    # ==========================
    # 自相关
    # ==========================
    def autocorrelation(self, x, p):

        N = len(x)

        r = np.zeros(p + 1)

        for lag in range(p + 1):

            r[lag] = np.sum(x[:N - lag] * x[lag:N])

        return r

    # ==========================
    # Levinson-Durbin
    # ==========================
    def levinson_durbin(self, r, p):

        a = np.zeros(p + 1)
        e = r[0]

        if e == 0:
            return a

        a[0] = 1.0

        for i in range(1, p + 1):

            acc = 0

            for j in range(1, i):
                acc += a[j] * r[i - j]

            k = -(r[i] + acc) / e

            a_new = a.copy()

            for j in range(1, i):
                a_new[j] = a[j] + k * a[i - j]

            a_new[i] = k

            a = a_new

            e *= (1 - k * k)

            if e <= 0:
                e = 1e-6

        return a

    # ==========================
    # 残差提取
    # ==========================
    def compute_residual(self, x, a):

        residual = lfilter(a, [1.0], x)

        return residual

# ==========================
# 测试
# ==========================
if __name__ == "__main__":

    import sounddevice as sd

    fs = 16000
    block_size = 1024

    lpc = LPCResidual(order=16, verbose=True)

    def callback(indata, outdata, frames, time, status):

        x = indata[:, 0]

        residual = lpc.process(x)

        outdata[:] = residual.reshape(-1, 1)

    with sd.Stream(
        samplerate=fs,
        blocksize=block_size,
        channels=1,
        callback=callback
    ):

        print("LPC Residual Test Running...")
        while True:
            sd.sleep(1000)