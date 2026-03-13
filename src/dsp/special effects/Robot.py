import numpy as np
import sounddevice as sd
from scipy.signal import butter, lfilter
import sys

# ==========================================
# Robot Voice Effect
# ==========================================
class RobotEffect:
    def __init__(self, fs, carrier_freq=200):
        self.fs = fs
        self.carrier_freq = carrier_freq

        # 相位累加器（生成连续正弦波）
        self.phase = 0

        # 低通滤波器参数
        cutoff = 1000
        nyq = fs / 2

        self.b, self.a = butter(
            4,
            cutoff / nyq,
            btype='low'
        )

    # ===============================
    # 生成载波
    # ===============================
    def generate_carrier(self, length):
        t = (np.arange(length) + self.phase) / self.fs

        carrier = np.sin(2 * np.pi * self.carrier_freq * t)

        self.phase += length
        self.phase %= self.fs

        return carrier

    # ===============================
    # 主处理函数
    # ===============================
    def process_block(self, input_block):
        # 生成调制载波
        carrier = self.generate_carrier(len(input_block))

        # 环形调制
        ring_mod = input_block * carrier * 2.0

        # 低通滤波
        robot_voice = 2.0 * lfilter(self.b, self.a, ring_mod)

        return robot_voice

# ==========================================
# 实时音频
# ==========================================

fs = 16000
block_size = 1024

effect = RobotEffect(fs, carrier_freq=200)

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
print("🤖 Robot Voice 机器人音效启动")
print(f"载波频率: {effect.carrier_freq}Hz")
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
    print("Robot Voice 机器人音效已停止")
    print("=" * 50)
    sys.exit(0)