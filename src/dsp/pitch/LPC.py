import numpy as np

class LPCAnalysis:
    def __init__(self, order=16, verbose=False):

        self.order = order
        self.verbose = verbose

        if self.verbose:
            print(f"LPC Analysis 初始化: 阶数 = {order}")

    # ==========================
    # 主处理函数
    # ==========================
    def process(self, x):

        x = self._preprocess(x)

        a = self.compute_lpc(x)

        return a

    # ==========================
    # 预处理
    # ==========================
    def _preprocess(self, x):

        # 去直流
        x = x - np.mean(x)

        # 归一化
        max_val = np.max(np.abs(x))
        if max_val > 1e-6:
            x = x / max_val

        return x

    # ==========================
    # LPC计算
    # ==========================
    def compute_lpc(self, x):

        p = self.order

        # Step 1 自相关
        r = self.autocorrelation(x, p)

        # Step 2 Levinson-Durbin
        a = self.levinson_durbin(r, p)

        return a

    # ==========================
    # 自相关函数
    # ==========================
    def autocorrelation(self, x, p):

        N = len(x)

        r = np.zeros(p + 1)

        for lag in range(p + 1):

            r[lag] = np.sum(x[:N - lag] * x[lag:N])

        return r

    # ==========================
    # Levinson-Durbin算法
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
# 独立测试
# ==========================
if __name__ == "__main__":

    import sounddevice as sd

    fs = 16000
    block_size = 1024

    lpc = LPCAnalysis(order=16, verbose=True)

    print("=" * 50)
    print("LPC Analysis Test")
    print("=" * 50)

    def callback(indata, outdata, frames, time_info, status):

        x = indata[:, 0]

        a = lpc.process(x)

        # 打印前几个系数
        print("LPC:", np.round(a[:5], 3))

        outdata[:] = indata

    with sd.Stream(
        samplerate=fs,
        blocksize=block_size,
        channels=1,
        callback=callback,
    ):

        print("音频流启动...")
        while True:
            sd.sleep(1000)