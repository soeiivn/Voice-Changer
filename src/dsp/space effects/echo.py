import numpy as np
import sounddevice as sd
import sys

# ==========================================
# Delay Echo Effect
# ==========================================
class EchoEffect:

    def __init__(self, fs, delay_ms=250, decay=0.4):

        self.fs = fs
        self.delay_samples = int(fs * delay_ms / 1000)

        self.decay = decay

        self.buffer = np.zeros(self.delay_samples)
        self.ptr = 0

    def process_block(self, input_block):

        output = np.zeros_like(input_block)

        for i in range(len(input_block)):

            delayed = self.buffer[self.ptr]

            y = input_block[i] + self.decay * delayed

            output[i] = y

            self.buffer[self.ptr] = input_block[i]

            self.ptr += 1
            if self.ptr >= self.delay_samples:
                self.ptr = 0

        return output


fs = 16000
block_size = 1024

echo = EchoEffect(fs, delay_ms=300, decay=0.5)


def callback(indata, outdata, frames, time, status):
    input_block = indata[:, 0]
    processed = echo.process_block(input_block)
    outdata[:] = processed.reshape(-1, 1)


print("🎤 Echo Effect Start")
print("按 Ctrl+F2 停止程序...")
print("=" * 40)

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
    # 不重新抛出异常，直接退出

except Exception as e:
    print(f"\n❌ 发生错误: {e}")

finally:
    print("程序已停止")
    sys.exit(0)  # 正常退出