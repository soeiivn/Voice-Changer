import numpy as np
from scipy.signal import lfilter

class LPCResidual:

    def __init__(self, order=16):

        self.order = order

    # =====================
    # 主处理
    # =====================
    def process(self, x):

        x = self.preprocess(x)

        a = self.compute_lpc(x)

        residual = self.compute_residual(x, a)

        return residual, a

    # =====================
    # 预处理
    # =====================
    def preprocess(self, x):

        # 去直流
        x = x - np.mean(x)

        # 预加重
        x = np.append(x[0], x[1:] - 0.97 * x[:-1])

        # Hamming窗
        x = x * np.hamming(len(x))

        return x

    # =====================
    # LPC
    # =====================
    def compute_lpc(self, x):

        p = self.order

        r = self.autocorrelation(x, p)

        a = self.levinson_durbin(r, p)

        # 系数稳定化
        a = np.clip(a, -1.5, 1.5)

        return a

    # =====================
    # 自相关
    # =====================
    def autocorrelation(self, x, p):

        r = np.zeros(p + 1)

        for i in range(p + 1):
            r[i] = np.sum(x[:len(x)-i] * x[i:])

        return r

    # =====================
    # Levinson
    # =====================
    def levinson_durbin(self, r, p):

        a = np.zeros(p + 1)
        e = r[0]

        a[0] = 1

        if e == 0:
            return a

        for i in range(1, p + 1):

            acc = 0
            for j in range(1, i):
                acc += a[j] * r[i-j]

            k = -(r[i] + acc) / e

            a_new = a.copy()

            for j in range(1, i):
                a_new[j] = a[j] + k * a[i-j]

            a_new[i] = k

            a = a_new

            e *= (1 - k*k)

            if e <= 1e-6:
                e = 1e-6

        return a

    # =====================
    # 残差
    # =====================
    def compute_residual(self, x, a):

        residual = lfilter(a, [1], x)

        # 能量控制
        energy = np.sqrt(np.mean(residual**2))

        if energy > 1e-6:
            residual /= energy

        residual = np.clip(residual, -1, 1)

        return residual


# ==========================================
# 测试代码
# ==========================================
if __name__ == "__main__":

    import sys
    import time
    import sounddevice as sd

    # 测试参数
    fs = 16000
    block_size = 1024

    # 创建LPC残差处理器
    lpc = LPCResidual(order=16)

    print("=" * 60)
    print("🎵 LPC Residual 测试程序")
    print(f"📊 参数设置:")
    print(f"   ├─ 采样率: {fs}Hz")
    print(f"   ├─ 块大小: {block_size}")
    print(f"   └─ LPC阶数: {lpc.order}")
    print("=" * 60)
    print("⚠️  注意: 残差信号能量较大，可能产生啸叫！")
    print("⌨️  按 Ctrl+F2 或 Ctrl+C 停止程序")
    print("-" * 60)

    # 回调函数
    def callback(indata, outdata, frames, time, status):
        if status:
            print(f"Status: {status}")

        try:
            # 获取输入音频
            input_block = indata[:, 0]

            # 处理LPC残差
            residual, coeffs = lpc.process(input_block)

            # 输出残差信号
            outdata[:] = residual.reshape(-1, 1)

            # 可选：打印LPC系数（每100块打印一次）
            if not hasattr(callback, "counter"):
                callback.counter = 0
            callback.counter += 1
            if callback.counter % 100 == 0:
                print(f"LPC系数 (前5个): {coeffs[:5].round(3)}")

        except Exception as e:
            print(f"处理错误: {e}")
            outdata[:] = indata  # 安全模式

    # 启动音频流
    try:
        with sd.Stream(
                samplerate=fs,
                blocksize=block_size,
                channels=1,
                dtype='float32',
                callback=callback):

            print("▶️ 音频流已启动，正在处理...")
            print("💬 说话吧！你会听到残差信号（可能很大声！）")

            # 显示运行时间
            start_time = time.time()
            counter = 0

            while True:
                time.sleep(1)
                counter += 1
                if counter % 5 == 0:
                    elapsed = time.time() - start_time
                    print(f"⏱️ 运行中... {elapsed:.0f}秒")

    except KeyboardInterrupt:
        print("\n👋 检测到中断信号，正在停止程序...")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n" + "=" * 60)
        print("🏁 LPC Residual 测试已停止")
        print("=" * 60)
        sys.exit(0)