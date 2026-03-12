import numpy as np
import sounddevice as sd
import sys

class FDNReverb:

    def __init__(self, fs):

        self.fs = fs

        # 延迟时间(ms)
        delays_ms = [13, 17, 19, 23]

        # 反馈系数
        self.gains = [0.55, 0.52, 0.50, 0.48]

        self.delays = [int(fs * d / 1000) for d in delays_ms]

        self.buffers = [np.zeros(d) for d in self.delays]

        self.ptrs = [0] * len(self.delays)

    def process_block(self, input_block):

        output = np.zeros_like(input_block)

        for n in range(len(input_block)):

            x = input_block[n]

            y_total = 0

            for i in range(len(self.buffers)):
                buffer = self.buffers[i]
                ptr = self.ptrs[i]
                gain = self.gains[i]

                delayed = buffer[ptr]

                y = x + gain * delayed

                buffer[ptr] = y

                self.ptrs[i] = (ptr + 1) % len(buffer)

                y_total += delayed

            output[n] = y_total / len(self.buffers)

        return output

# ==============================
# 实时音频
# ==============================

fs = 16000
block_size = 1024

reverb = FDNReverb(fs)

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
print("🎵 FDN 混响效果启动")
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
        print("-" * 50)

        # 添加计数器显示运行时间
        import time

        start_time = time.time()
        counter = 0

        while True:
            sd.sleep(1000)
            counter += 1
            if counter % 5 == 0:  # 每5秒显示一次状态
                elapsed = time.time() - start_time
                print(f"⏱️ 运行中... {elapsed:.0f}秒")

except KeyboardInterrupt:
    print("\n👋 检测到中断信号，正在停止程序...")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")
    import traceback

    traceback.print_exc()

finally:
    print("正在清理资源...")
    print("FDN 混响效果已停止")
    print("=" * 50)
    sys.exit(0)