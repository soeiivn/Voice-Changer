import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
import sys

# ==========================================
# Telephone Effect
# Bandpass + Soft Clipping
# ==========================================
class TelephoneEffect:
    def __init__(self, fs):
        self.fs = fs

        # 电话带宽
        low = 300
        high = 3400

        # 归一化频率
        nyq = fs / 2

        # Butterworth 带通滤波器
        self.b, self.a = butter(
            4,
            [low / nyq, high / nyq],
            btype='band'
        )

        # 软削波阈值
        self.threshold = 0.8

    # ===============================
    # 软削波
    # ===============================
    def soft_clip(self, x):
        return np.tanh(2 * x)

    # ===============================
    # 主处理函数
    # ===============================
    def process_block(self, input_block):
        # 带通滤波
        filtered = lfilter(self.b, self.a, input_block)

        # 软削波
        distorted = self.soft_clip(filtered)

        return distorted


# ==========================================
# 实时音频
# ==========================================

fs = 16000
block_size = 1024

effect = TelephoneEffect(fs)

def callback(indata, outdata, frames, time, status):
    if status:
        print(f"Status: {status}")

    try:
        input_block = indata[:, 0]
        processed = effect.process_block(input_block)
        outdata[:] = processed.reshape(-1, 1)
    except Exception as e:
        print(f"处理错误: {e}")
        # 出错时输出原始音频（安全模式）
        outdata[:] = indata


print("=" * 50)
print("☎ Telephone Effect 电话效果启动")
print(f"带宽: 300Hz - 3400Hz (模拟电话音质)")
print("按 Ctrl+F2 停止程序...")
print("=" * 50)

try:
    with sd.Stream(
            samplerate=fs,
            blocksize=block_size,
            channels=1,
            dtype='float32',
            callback=callback):

        print("音频流已启动，正在处理...")

        while True:
            sd.sleep(1000)

except KeyboardInterrupt:
    print("\n👋 检测到中断信号，正在停止程序...")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")

finally:
    print("Telephone Effect 电话效果已停止")
    print("=" * 50)
    sys.exit(0)