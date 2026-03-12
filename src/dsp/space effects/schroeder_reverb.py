import numpy as np
import sounddevice as sd
import sys

class CombFilter:

    def __init__(self, delay, gain):
        self.buffer = np.zeros(delay)
        self.gain = gain
        self.ptr = 0

    def process(self, x):
        y = self.buffer[self.ptr]

        self.buffer[self.ptr] = x + self.gain * y

        self.ptr = (self.ptr + 1) % len(self.buffer)

        return y

class AllpassFilter:

    def __init__(self, delay, gain):
        self.buffer = np.zeros(delay)
        self.gain = gain
        self.ptr = 0

    def process(self, x):
        buf = self.buffer[self.ptr]

        y = -x + buf

        self.buffer[self.ptr] = x + self.gain * buf

        self.ptr = (self.ptr + 1) % len(self.buffer)

        return y

class SchroederReverb:

    def __init__(self, fs):

        comb_delays = [29, 37, 41, 43]
        comb_gains = [0.75, 0.73, 0.71, 0.70]

        self.combs = [
            CombFilter(int(fs * d / 1000), g)
            for d, g in zip(comb_delays, comb_gains)
        ]

        allpass_delays = [5, 1.7]

        self.allpasses = [
            AllpassFilter(int(fs * d / 1000), 0.7)
            for d in allpass_delays
        ]

    def process_block(self, input_block):

        output = np.zeros_like(input_block)

        for i in range(len(input_block)):

            x = input_block[i]

            y = 0

            for comb in self.combs:
                y += comb.process(x)

            y /= len(self.combs)

            for ap in self.allpasses:
                y = ap.process(y)

            output[i] = y

        return output

# ==============================
# 实时音频
# ==============================

fs = 16000
block_size = 1024

reverb = SchroederReverb(fs)

def callback(indata, outdata, frames, time, status):
    if status:
        print(f"Status: {status}")

    try:
        input_block = indata[:, 0]
        processed = reverb.process_block(input_block)
        outdata[:] = processed.reshape(-1, 1)
    except Exception as e:
        print(f"处理错误: {e}")
        # 出错时输出原始音频（安全模式）
        outdata[:] = indata

print("=" * 50)
print("🎵 Schroeder 混响效果启动")
print("梳状滤波器延迟(ms): 29, 37, 41, 43")
print("梳状滤波器增益: 0.75, 0.73, 0.71, 0.70")
print("全通滤波器延迟(ms): 5, 1.7")
print("全通滤波器增益: 0.7")
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
    print("Schroeder 混响效果已停止")
    print("=" * 50)
    sys.exit(0)